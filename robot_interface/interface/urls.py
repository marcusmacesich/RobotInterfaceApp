from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.interface, name='interface'),
    path('upload/<int:program_id>/', views.upload_page, name='upload_page'),
    path('upload_program/', views.upload_program, name='upload_program'),
    path('prepare_save_program/', views.prepare_save, name='prepare_save_program'),
    path('save_program/', views.save_program, name='save_program'),
    path('robot_code/<int:robot_id>', views.robot_get_code, name='robot_get_code'),
    path('robot_code/<int:robot_id>/<int:program_id>/exec/', views.robot_exec_status, name='robot_exec_status'),
    path('start_program/<int:robot_id>/', views.start_program, name='start_program'),
    path('stop_program/<int:robot_id>/', views.stop_program, name='stop_program'),
    path('requeue_program/<int:robot_id>/', views.requeue_program, name='requeue_program'),
    path('sitemap/', views.sitemap_view, name='sitemap'),
    path('stream', views.stream, name='stream'),
    path('codetemplates/', views.code_template_page, name='codetemplates'),\
    path('robot_code/<int:robot_id>/finish_program/', views.finish_program, name='finish_program'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('manage_templates/', views.manage_templates, name='manage_templates'),
    path('get-template-names/', views.get_template_names, name='get_template_names'),
    path('fetch_text_file/', views.fetch_text_file, name='fetch_text_file'),
    path('handle_text_data/', views.handle_text_data, name='handle_text_data'),
    path('lab/<int:lab_id>/', views.lab_view, name='lab_view'),
    path('lab_list/', views.lab_list, name='lab_list'),
    path('upload_lab/', views.upload_lab, name='upload_lab'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard')
]
