//192.168.0.162
//172.28.123.183
const server = "http://172.28.123.183:8088/janus";
const iceServers = [{ urls: "stun:stun.l.google.com:19302" }]; // Example STUN server, modify as needed
const sessionData = { session_id: null, plugin_id: null };
var janus = null;
var textroom = null;
var opaqueId = "textroomtest-"+Janus.randomString(12);
var consoleElement = '#console';
var myroom = 1234;	// Demo room
var myusername = "User";
var myid = null;
var participants = {}
var transactions = {}
$(document).ready(function() {
    Janus.init({debug: "all", callback: function() {
        if(!Janus.isWebrtcSupported()) {
            bootbox.alert("No WebRTC support... ");
            return;
        }
        janus = new Janus(
        {
            server: server,
            iceServers: iceServers,
            success: function()
            {
                // Attach to TextRoom plugin
                janus.attach(
                    {
                        plugin: "janus.plugin.textroom",
                        opaqueId: opaqueId,
                        success: function(pluginHandle) {
                            $('#details').remove();
                            textroom = pluginHandle;
                            Janus.log("Plugin attached! (" + textroom.getPlugin() + ", id=" + textroom.getId() + ")");
                            // Setup the DataChannel
                            let body = { request: "setup" };
                            Janus.debug("Sending message:", body);
                            textroom.send({ message: body });
                        },
                        error: function(error) {
                            console.error("  -- Error attaching plugin...", error);
                            bootbox.alert("Error attaching plugin... " + error);
                        },
                        iceState: function(state) {
                            Janus.log("ICE state changed to " + state);
                        },
                        mediaState: function(medium, on) {
                            Janus.log("Janus " + (on ? "started" : "stopped") + " receiving our " + medium);
                        },
                        webrtcState: function(on) {
                            Janus.log("Janus says our WebRTC PeerConnection is " + (on ? "up" : "down") + " now");
                        },
                        onmessage: function(msg, jsep) {
                            Janus.debug(" ::: Got a message :::", msg);
                            if(msg["error"]) {
                                bootbox.alert(msg["error"]);
                            }
                            if(jsep) {
                                // Answer
                                textroom.createAnswer(
                                    {
                                        jsep: jsep,
                                        // We only use datachannels
                                        tracks: [
                                            { type: 'data' }
                                        ],
                                        success: function(jsep) {
                                            Janus.debug("Got SDP!", jsep);
                                            let body = { request: "ack" };
                                            textroom.send({ message: body, jsep: jsep });
                                        },
                                        error: function(error) {
                                            Janus.error("WebRTC error:", error);
                                            bootbox.alert("WebRTC error... " + error.message);
                                        }
                                    });
                            }
                        },
                        // eslint-disable-next-line no-unused-vars
                        ondataopen: function(label, protocol) {
                            Janus.log("The DataChannel is available!");
                            // Prompt for a display name to join the default room
                            registerUsername();
                            console.log("Username set as ", myusername);
                            

                        },
                        ondata: function(data) {
                            Janus.debug("We got data from the DataChannel!", data);
                            //~ $('#datarecv').val(data);
                            let json = JSON.parse(data);
                            let transaction = json["transaction"];
                            if(transactions[transaction]) {
                                // Someone was waiting for this
                                transactions[transaction](json);
                                delete transactions[transaction];
                                return;
                            }
                            let what = json["textroom"];
                            if(what === "message") {
                                // Incoming message: public or private?
                                let msg = escapeXmlTags(json["text"]);
                                let from = json["from"];
                                let dateString = getDateString(json["date"]);
                                let whisper = json["whisper"];
                                let sender = participants[from] ? participants[from] : escapeXmlTags(json["display"]);
                                if(whisper === true) {
                                    // Private message
                                    $(consoleElement).append('<p style="color: purple;">[' + dateString + '] <b>[whisper from ' + sender + ']</b> ' + msg);
                                    $(consoleElement).get(0).scrollTop = $(consoleElement).get(0).scrollHeight;
                                } else {
                                    // Public message
                                    $(consoleElement).append('<p>[' + dateString + '] <b>' + sender + ':</b> ' + msg);
                                    $(consoleElement).get(0).scrollTop = $(consoleElement).get(0).scrollHeight;
                                }
                            } else if(what === "announcement") {
                                // Room announcement
                                let msg = escapeXmlTags(json["text"]);
                                let dateString = getDateString(json["date"]);
                                $(consoleElement).append('<p style="color: purple;">[' + dateString + '] <i>' + msg + '</i>');
                                $(consoleElement).get(0).scrollTop = $(consoleElement).get(0).scrollHeight;
                            } else if(what === "join") {
                                // Somebody joined
                                let username = json["username"];
                                let display = json["display"];
                                participants[username] = escapeXmlTags(display ? display : username);
                                console.log(participants[username], "joined");
                                //$('#chatroom').append('<p style="color: green;">[' + getDateString() + '] <i>' + participants[username] + ' joined</i></p>');
                                //$('#chatroom').get(0).scrollTop = $('#chatroom').get(0).scrollHeight;
                            } else if(what === "leave") {
                                // Somebody left
                                let username = json["username"];
                                console.log(participants[username], "left");
                                //$('#rp' + username).remove();
                                //$('#chatroom').append('<p style="color: green;">[' + getDateString() + '] <i>' + participants[username] + ' left</i></p>');
                                //$('#chatroom').get(0).scrollTop = $('#chatroom').get(0).scrollHeight;
                                delete participants[username];
                            } else if(what === "kicked") {
                                // Somebody was kicked
                                let username = json["username"];
                                $('#rp' + username).remove();
                                $(consoleElement).append('<p style="color: green;">[' + getDateString() + '] <i>' + participants[username] + ' was kicked from the room</i></p>');
                                $(consoleElement).get(0).scrollTop = $(consoleElement).get(0).scrollHeight;
                                delete participants[username];
                                if(username === myid) {
                                    bootbox.alert("You have been kicked from the room", function() {
                                        window.location.reload();
                                    });
                                }
                            } else if(what === "destroyed") {
                                if(json["room"] !== myroom)
                                    return;
                                // Room was destroyed, goodbye!
                                Janus.warn("The room has been destroyed!");
                                bootbox.alert("The room has been destroyed", function() {
                                    window.location.reload();
                                });
                            }
                        },
                        oncleanup: function() {
                            Janus.log(" ::: Got a cleanup notification :::");
                            $('#datasend').attr('disabled', true);
                        }
                    });
            },
            error: function(error) {
                Janus.error(error);
                bootbox.alert(error, function() {
                    window.location.reload();
                });
            },
            destroyed: function() {
                window.location.reload();
            }
        });
}});
});
// eslint-disable-next-line no-unused-vars
function checkEnter(field, event) {
let theCode = event.keyCode ? event.keyCode : event.which ? event.which : event.charCode;
if(theCode == 13) {
if(field.id == 'username')
    registerUsername();
else if(field.id == 'datasend')
    sendData();
return false;
} else {
return true;
}
}

function registerUsername() {
let username = myusername;
myid = Janus.randomString(12);
let transaction = Janus.randomString(12);
let register = {
    textroom: "join",
    transaction: transaction,
    room: myroom,
    username: myid,
    display: username
};
myusername = escapeXmlTags(username);
transactions[transaction] = function(response) {
    if(response["textroom"] === "error") {
        // Something went wrong
        if(response["error_code"] === 417) {
            // This is a "no such room" error: give a more meaningful description
            bootbox.alert(
                "<p>Apparently room <code>" + myroom + "</code> (the one this demo uses as a test room) " +
                "does not exist...</p><p>Do you have an updated <code>janus.plugin.textroom.jcfg</code> " +
                "configuration file? If not, make sure you copy the details of room <code>" + myroom + "</code> " +
                "from that sample in your current configuration file, then restart Janus and try again."
            );
        } else {
            bootbox.alert(response["error"]);
        }
        return;
    }
    $(consoleElement).css('height', ($(window).height()-420)+"px");
    // We're in
    // Any participants already in?
    console.log("Participants:", response.participants);
    if(response.participants && response.participants.length > 0) {
        for(let i in response.participants) {
            let p = response.participants[i];
            participants[p.username] = escapeXmlTags(p.display ? p.display : p.username);
            if(p.username !== myid && $('#rp' + p.username).length === 0) {
                // Add to the participants list
                $('#rp' + p.username).css('cursor', 'pointer').click(function() {
                    let username = $(this).attr('id').split("rp")[1];
                    sendPrivateMsg(username);
                });
            }
            console.log(participants[p.username]);
            //$('#chatroom').append('<p style="color: green;">[' + getDateString() + '] <i>' + participants[p.username] + ' joined</i></p>');
            //$('#chatroom').get(0).scrollTop = $('#chatroom').get(0).scrollHeight;
        }
    }
};
textroom.data({
    text: JSON.stringify(register),
    error: function(reason) {
        bootbox.alert(reason);
        $('#username').removeAttr('disabled').val("");
        $('#register').removeAttr('disabled').click(registerUsername);
    }
});
}

function sendPrivateMsg(username) {
let display = participants[username];
if(!display)
return;
bootbox.prompt("Private message to " + display, function(result) {
if(result && result !== "") {
    let message = {
        textroom: "message",
        transaction: Janus.randomString(12),
        room: myroom,
        to: username,
        text: result
    };
    textroom.data({
        text: JSON.stringify(message),
        error: function(reason) { bootbox.alert(reason); },
        success: function() {
            console.log(escapeXmlTags(result))
            //$('#chatroom').append('<p style="color: purple;">[' + getDateString() + '] <b>[whisper to ' + display + ']</b> ' + escapeXmlTags(result));
            //$('#chatroom').get(0).scrollTop = $('#chatroom').get(0).scrollHeight;
        }
    });
}
});
return;
}

function sendData() {
let data = $('#datasend').val();
if(data === "") {
bootbox.alert('Insert a message to send on the DataChannel');
return;
}
let message = {
textroom: "message",
transaction: Janus.randomString(12),
room: myroom,
text: data,
};
// Note: messages are always acknowledged by default. This means that you'll
// always receive a confirmation back that the message has been received by the
// server and forwarded to the recipients. If you do not want this to happen,
// just add an ack:false property to the message above, and server won't send
// you a response (meaning you just have to hope it succeeded).
textroom.data({
text: JSON.stringify(message),
error: function(reason) { bootbox.alert(reason); },
success: function() { $('#datasend').val(''); }
});
}

// Helper to format times
function getDateString(jsonDate) {
let when = new Date();
if(jsonDate) {
when = new Date(Date.parse(jsonDate));
}
let dateString =
    ("0" + when.getUTCHours()).slice(-2) + ":" +
    ("0" + when.getUTCMinutes()).slice(-2) + ":" +
    ("0" + when.getUTCSeconds()).slice(-2);
return dateString;
}

// Helper to parse query string
function getQueryStringValue(name) {
name = name.replace(/[[]/, "\\[").replace(/[\]]/, "\\]");
let regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
results = regex.exec(location.search);
return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

// Helper to escape XML tags
function escapeXmlTags(value) {
if(value) {
let escapedValue = value.replace(new RegExp('<', 'g'), '&lt');
escapedValue = escapedValue.replace(new RegExp('>', 'g'), '&gt');
return escapedValue;
}
}