from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse, Http404
from interface.models import code_templates
from django.template import loader
from .models import Robot, Program, Functions, SavedProgram, WebSocketIP, LabDocument
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404

#Diffrent IPs used to test. Will eventually need to get the server and ice server variables from the DJango server automatically.
#172.28.123.183 Dreese lab ip
#172.27.52.190 Scott lab ip
ip_address = "172.27.52.190" 
stun_server = "stun:stun.l.google.com:19302"

# Retrieves the IP address that the websockets server is running on from the DB
web_ip_address = WebSocketIP.objects.first()


# Function to load the HTML of the IDE page
def interface(request):
    
    # Get all of the function objects for code blocks
    functions = Functions.objects.all()

    if request.user.is_authenticated:
        saved_programs = SavedProgram.objects.filter(student=request.user)
    else:
        saved_programs = None
    # Load the editor interface page
    return render(request, 'idewindow.html', {'functions': functions, 'saved_programs': saved_programs})

# Function to handle when the 'Upload' button is pressed
def upload_program(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        selected_robot = request.POST.get('selected_robot')

        print(code)
        print(selected_robot)

        # logic to handle uploading the code to the actual robot
        try:
            robot = Robot.objects.get(name=selected_robot)
        except Robot.DoesNotExist:
            error_message = 'Robot not found.'
            request.session['error_message'] = error_message
            return redirect('interface')

        # Save the code to the database
        program = Program.objects.create(
            student=request.user,
            robot=robot,
            code=code,
            status='Waiting'
        )

        # Success message
        request.session['upload_status'] = 'Program uploaded successfully'
        return redirect('upload_page', program_id=program.id)
    else:
        return redirect('interface')

# Function to render the upload page with console and control buttons 
def upload_page(request, program_id):
    status = request.session.get('upload_status', '')

    request.session['upload_status'] = ''

    # Get the latest Program for the current user
    try:
        program = Program.objects.get(id=program_id, student=request.user)
    except Program.DoesNotExist:
        program = None

    host = request.get_host().split(':')[0]          # get the active ip address
    scheme = 'ws' if request.is_secure() is False else 'wss'
    ws_base = f"{scheme}://{host}"
    return render(request, 'uploadwindow.html', {
        'program': program,
        'ws_base': ws_base,
    })
# Function to begin the save process
def prepare_save(request):
    if request.method == 'POST':
        code = request.POST.get('code')

        # Store the code
        request.session['code_to_save'] = code
        return redirect('save_program')
    else:
        return redirect('interface')

def save_program(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        code = request.session.get('code_to_save', '')

        if action == 'overwrite':
            # Get the ID of the program selected for overwriting
            existing_program_id = request.POST.get('existing_program')
            if existing_program_id:
                # Ensure that the selected program belongs to the user
                try:
                    saved_program = SavedProgram.objects.get(id=existing_program_id, student=request.user)
                    saved_program.code = code
                    saved_program.save()
                except SavedProgram.DoesNotExist:
                    # Handle case if the program does not exist (or doesn't belong to the user)
                    # You can add error messaging or simply redirect
                    return redirect('save_program')
            else:
                # Optionally, add a message or redirect if no selection was made
                return redirect('save_program')
        else:  # action == 'save_new'
            # Use the program name from the text input for a new saved program
            program_name = request.POST.get('program_name')
            SavedProgram.objects.create(
                program_name=program_name,
                student=request.user,
                code=code
            )

        # Clear the code from session and redirect to the interface
        request.session['code_to_save'] = ''
        return redirect('interface')
    else:
        code = request.session.get('code_to_save', '')
        if not code:
            return redirect('interface')
        # Fetch the user's saved programs to populate the dropdown
        saved_programs = SavedProgram.objects.filter(student=request.user)
        return render(request, 'savewindow.html', {'code': code, 'saved_programs': saved_programs})

# Updates program status to 'Run' when start is pressed 
#@csrf_exempt
def start_program(request, robot_id):
    if request.method == 'POST':
        # Parse JSON data from the request body
        data = json.loads(request.body)
        program_id = data.get('program_id')

        #robot = Robot.objects.get(id=robot_id)

        try:
            # Fetch the Program instance by ID
            program = Program.objects.get(id=program_id, robot__id=robot_id, student=request.user)
            # Update the status to 'Run'
            program.status = 'Run'
            program.save()
            return HttpResponse('Success')
        except Program.DoesNotExist:
            return HttpResponse('Program not found', status=404)
    else:
        return HttpResponse('Invalid request method', status=405)

# Updated program status to 'Stop' when stop button is pressed
def stop_program(request, robot_id):
    if request.method == 'POST':
        # Parse JSON data from the request body
        data = json.loads(request.body)
        program_id = data.get('program_id')

        #robot = Robot.objects.get(id=robot_id)

        try:
            # Fetch the Program instance by ID
            program = Program.objects.get(id=program_id, robot__id=robot_id, student=request.user)
            # Update the status to 'Run'
            program.status = 'Stop'
            program.save()
            return HttpResponse('Success')
        except Program.DoesNotExist:
            return HttpResponse('Program not found', status=404)
    else:
        return HttpResponse('Invalid request method', status=405)
        
# Updated the program status back to 'Waiting' when Requeue is pressed
def requeue_program(request, robot_id):
    if request.method == 'POST':
        # Parse JSON data from the request body
        data = json.loads(request.body)
        program_id = data.get('program_id')

        #robot = Robot.objects.get(id=robot_id)

        try:
            # Fetch the Program instance by ID
            program = Program.objects.get(id=program_id, robot__id=robot_id, student=request.user)
            # Update the status to 'Run'
            program.status = 'Waiting'
            program.save()
            return HttpResponse('Success')
        except Program.DoesNotExist:
            return HttpResponse('Program not found', status=404)
    else:
        return HttpResponse('Invalid request method', status=405)
        
# Old function that posts code to a URL rather than using a websocket
def robot_get_code(request, robot_id):
    # The robot will request this URL with its robot_id
    try:
        robot = Robot.objects.get(id=robot_id)
    except Robot.DoesNotExist:
        return JsonResponse({'error': 'Robot not found.'}, status=404)

    # Get the latest program for this robot
    program = Program.objects.filter(robot=robot, status='Waiting').order_by('-upload_time').first()
    if program is None:
        return JsonResponse({'error': 'No program available.'}, status=404)

    data = {
        'program_id': program.id,
        'code': program.code
    }
    return JsonResponse(data)

# Posts a given programs execution status to a URL for the robot
def robot_exec_status(request, robot_id, program_id):
    try:
        program = Program.objects.get(id=program_id, robot__id=robot_id, status__in=['Waiting', 'Run', 'Stop'])
    except Program.DoesNotExist:
        return HttpResponse('Program Not Found', status=404)

    return HttpResponse(program.status, content_type='text/plain')

# Allows the robot to set the status of a program to 'Finished'
@csrf_exempt
def finish_program(request, robot_id):
    if request.method == 'POST':
        try:
            robot = Robot.objects.get(id=robot_id)
        except Robot.DoesNotExist:
            return JsonResponse({'error': 'Robot Not Found'}, status=404)

        # Parse JSON data from the request body
        data = json.loads(request.body)
        program_id = data.get('program_id')

        try:
            # Fetch the Program instance by ID and robot ID
            program = Program.objects.get(id=program_id, robot=robot)
            # Update the status to 'Finished'
            program.status = 'Finished'
            program.save()
            return JsonResponse({'message': 'Program status updated to Finished'})
        except Program.DoesNotExist:
            return JsonResponse({'error': 'Program not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def sitemap_view(request):
    return render(request, 'sitemap.html')

def code_template_page(request):
    return render(request, 'codetemplates.html')

def stream(request):
    # Load the stream page
    context = {
        'ip_address': ip_address,
        'stun_server': stun_server,
    }
    return render(request, 'stream.html', context)

def manage_templates(request):
    return render(request, 'AddTemplates.html')

def get_template_names(request):
    with open('./interface/files/CodeTemplates/names.txt', 'r') as file:
        names = file.read()
    return HttpResponse(names, content_type="text/plain")

@csrf_exempt
def handle_text_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            # Validate text
            if not isinstance(text, str):
                return JsonResponse({'error': 'Invalid input'}, status=400)

            if text[:13] == "templateWrite":
                try:
                    write_to_file(text)

                    return JsonResponse({'status': 'success', 'message': 'Templates updated successfully!'})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)})

            if text[:14] == "templateRemove":
                try:
                    remove_file(text)

                    return JsonResponse({'status': 'success', 'message': 'Templates updated successfully!'})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)})
                
            if text[:10] == "namesWrite":
                try:
                    lines = text.splitlines()
                    filename = lines[1]
                    content="\n".join(lines[2:])
                    with open('./interface/files/CodeTemplates/'+filename, "w") as file:
                        file.write(content)
                    return JsonResponse({'status': 'success', 'message': 'Names file updated successfully!'})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)})
                
            if text[:11] == "namesRemove":
                try:
                    lines = text.splitlines()
                    filename = lines[1]
                    content="\n".join(lines[2:])
                    with open('./interface/files/CodeTemplates/'+filename, "w") as file:
                        file.write(content)
                    return JsonResponse({'status': 'success', 'message': 'Names file updated successfully!'})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)})
                
            # Process text (e.g., save to the database, etc.)
            return JsonResponse({'message': 'Data received successfully, no updates to rules or functions'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def write_to_file(input_string):
    # Split the input string by lines
    lines = input_string.splitlines()

    # Validate that there's at least three lines
    if len(lines) < 3:
        raise ValueError("Input format is invalid. At least three lines are required.")

    # Extract the first line, filename, and content
    header = lines[0]
    filename = lines[1]
    displayname = lines[2]
    content = "\n".join(lines[3:])

    # Validate the header
    if not header.strip() == "templateWrite":
        raise ValueError("The first line must be 'templateWrite'.")

    # Check for invalid cases where 'templateWrite' is detected but format is wrong
    if "templateWrite" in input_string and header.strip() != "templateWrite":
        raise ValueError("The substring 'templateWrite' is detected but the format is incorrect.")

    # Write content to the file
    with open('./interface/files/CodeTemplates/'+filename, "w") as file:
        file.write(content)

    new_item = code_templates.objects.create(name=filename, description=f"{displayname}", value=content)
    print(f"Created item with ID: {new_item.id}")
    print(f"Content successfully written to {filename}.")

def fetch_text_file(request):
    # Get the file name from the query parameters
    file_name = request.GET.get('file_name', '')

    # Create the full path to the file
    file_path = './interface/files/CodeTemplates/' + file_name

    # Check if the file exists and is safe to access
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return HttpResponse(content, content_type='text/plain')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'File not found or invalid file name.'}, status=404)


def remove_file(input_string):
    lines = input_string.split()
    prompt = lines[0]
    name_to_delete = lines[1]
    flag = False
    all_items = code_templates.objects.all()
    for item in all_items:
        if [all_strings for all_strings in input_string.split() if "delete_all" in all_strings]:
            item.delete()
            file_path = f'./interface/files/CodeTemplates/{item.name}'
            os.remove(file_path)
        if item.name == name_to_delete:
            try:
                item.delete()
                file_path = f'./interface/files/CodeTemplates/{name_to_delete}'
                os.remove(file_path)
                flag = True
                print(f"Item {item.name} deleted successfully.")
            except code_templates.DoesNotExist:
                print(f"Item {name_to_delete} was not deleted.")
    if not flag:
        print(f"Item {name_to_delete} not found for deletion.")

# Opens a new tab with the lab pdf

def lab_view(request, lab_id):
    """
    Lookup the LabDocument by its ID, then open and stream
    the PDF whose filename is stored in the model.
    """
    # 1) Fetch the model (404 if not found)
    lab_doc = get_object_or_404(LabDocument, id=lab_id)

    # 2) Build the absolute path to your files/labs directory
    file_path = os.path.join(
        settings.BASE_DIR,
        'interface', 'files', 'labs',
        lab_doc.file_name
    )

    # 3) If the file isn’t on disk, return 404
    if not os.path.exists(file_path):
        raise Http404(f"Lab file '{lab_doc.file_name}' not found.")

    # 4) Stream it back as PDF
    return FileResponse(
        open(file_path, 'rb'),
        content_type='application/pdf'
    )

# Lists all of the labs with buttons to retrieve them
def lab_list(request):
    # grab all your uploaded labs (order by whatever you like)
    labs = LabDocument.objects.all().order_by('id')
    return render(request, 'lablist.html', {
        'labs': labs
    })



def upload_lab(request):
    """
    GET:  render upload form
    POST: save uploaded PDF to /files/labs/, record its filename + display_name
    """
    error = None

    if request.method == 'POST':
        display_name  = request.POST.get('display_name', '').strip()
        uploaded_file = request.FILES.get('lab_file')

        if not display_name or not uploaded_file:
            error = "You must provide both a display name and a PDF file."
        else:
            # where to save on disk: <project_root>/files/labs/
            target_dir = os.path.join(settings.BASE_DIR, 'interface', 'files', 'labs')
            os.makedirs(target_dir, exist_ok=True)

            fs = FileSystemStorage(location=target_dir)
            # this preserves the original uploaded filename
            saved_filename = fs.save(uploaded_file.name, uploaded_file)

            # record in the database
            LabDocument.objects.create(
                display_name=display_name,
                file_name=saved_filename
            )
            return redirect('lab_list')  # or wherever you list your labs

    return render(request, 'UploadLab.html', {
        'error': error
    })


def admin_dashboard(request):
    return render(request, 'AdminDashboard.html')
