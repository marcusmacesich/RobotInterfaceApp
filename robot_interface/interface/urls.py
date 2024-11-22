from django.urls import path
from . import views

urlpatterns = [
    path('', views.interface, name='interface'),
    path('upload/<int:program_id>/', views.upload_page, name='upload_page'),
    path('upload_program/', views.upload_program, name='upload_program'),
    path('prepare_save_program/', views.prepare_save, name='prepare_save_program'),
    path('save_program/', views.save_program, name='save_program'),
    path('robot_code/<int:robot_id>', views.robot_get_code, name='robot_get_code'),
    path('robot_code/<int:robot_id>/exec', views.robot_exec_status, name='robot_exec_status'),
    path('start_program/<int:robot_id>/', views.start_program, name='start_program'),
    path('sitemap/', views.sitemap_view, name='sitemap'),
    path('stream', views.stream, name='stream'),
    path('codetemplates/', views.code_templates, name='codetemplates')
]