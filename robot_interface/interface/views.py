from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

def interface(request):
    # Load the editor interface page
    return render(request, 'idewindow.html')

def upload_program(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        selected_robot = request.POST.get('selected_robot')

        # logic to handle uploading the code to the actual robot

        # place holder for passing through error message
        error_message = None

        if error_message:
            # Save error and send back to editor
            request.session['error_message'] = error_message
            return redirect('interface')
        else:
            # Save success and send to upload page
            request.session['upload_status'] = 'Program uploaded successfully'
            return redirect('upload_page')

    else:
        return redirect('interface')

def upload_page(request):
    status = request.session.get('upload_status', '')

    request.session['upload_status'] = ''
    return render(request, 'uploadwindow.html', {'status': status})

def prepare_save(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        # Store the code in session or pass via context
        request.session['code_to_save'] = code
        return redirect('save_program')
    else:
        return redirect('interface')

def save_program(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        program_name = request.POST.get('program_name')
        code = request.session.get('code_to_save', '')

        # Logic to save the program to database in future
        # new_program = Program.objects.create(
        #     username=username,
        #     program_name=program_name,
        #     code=code
        # )

        # Clear code from session
        request.session['code_to_save'] = ''

        # Redirect to editor
        return redirect('interface')
    else:
        code = request.session.get('code_to_save', '')
        if not code:
            return redirect('interface')
        return render(request, 'savewindow.html', {'code': code})