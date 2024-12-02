from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Robot, Program
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

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
        program = Program.objects.create(
            student=request.user,
            robot=robot,
            code=code,
            status='Waiting'
        )
        # place holder for passing through error message
        # error_message = None

        # Success message
        request.session['upload_status'] = 'Program uploaded successfully'
        return redirect('upload_page', program_id=program.id)
    else:
        return redirect('interface')

def upload_page(request, program_id):
    status = request.session.get('upload_status', '')

    request.session['upload_status'] = ''

    # Get the latest Program for the current user
    try:
        program = Program.objects.get(id=program_id, student=request.user)
    except Program.DoesNotExist:
        program = None

    return render(request, 'uploadwindow.html', {'status': status, 'program': program})

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

def robot_exec_status(request, robot_id):

    try:
        robot = Robot.objects.get(id=robot_id)
    except Robot.DoesNotExist:
        return HttpResponse('Robot Not Found', status=404)

    program = Program.objects.filter(robot=robot, status__in=['Waiting', 'Run', 'Stop']).order_by('-upload_time').first()

    if program is None:
        return HttpResponse('No Status Available', status=404)

    return(HttpResponse(program.status, content_type='text/plain'))

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

def code_templates(request):
    return render(request, 'codetemplates.html')