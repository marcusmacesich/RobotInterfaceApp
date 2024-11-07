from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Robot, Program

def interface(request):
    # Load the editor interface page
    return render(request, 'idewindow.html')

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
        Program.objects.create(
            student=request.user,
            robot=robot,
            code=code
        )
        # place holder for passing through error message
        # error_message = None

        # Success message
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

        # Logic to save the program to database
        Program.objects.create(
            student=request.user,
            robot=Robot.objects.get(name=program_name),  # Adjust as needed
            code=code
        )

        # Clear code from session
        request.session['code_to_save'] = ''

        # Redirect to editor
        return redirect('interface')
    else:
        code = request.session.get('code_to_save', '')
        if not code:
            return redirect('interface')
        return render(request, 'savewindow.html', {'code': code})
     
def code_templates(request):
    return render(request, 'codetemplates.html')

def robot_get_code(request, robot_id):
    # The robot will request this URL with its robot_id
    try:
        robot = Robot.objects.get(id=robot_id)
    except Robot.DoesNotExist:
        return HttpResponse('Robot not found.', status=404)

    # Get the latest program for this robot
    program = Program.objects.filter(robot=robot).order_by('-upload_time').first()
    if program is None:
        return HttpResponse('No program available.', status=404)

    # Return the code
    return HttpResponse(program.code, content_type='text/plain')
def sitemap_view(request):
    return render(request, 'sitemap.html')