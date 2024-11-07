from django.urls import path
from . import views

urlpatterns = [
    path('', views.interface, name='interface'),
    path('codetemplates/', views.code_templates, name='codetemplates'),
    path('upload/', views.upload_page, name='upload_page'),
    path('upload_program', views.upload_program, name='upload_program'),
    path('prepare_save_program/', views.prepare_save, name='prepare_save_program'),
    path('save_program/', views.save_program, name='save_program'),
    path('robot_code/<int:robot_id>', views.robot_get_code, name='robot_get_code'),
    path('sitemap/', views.sitemap_view, name='sitemap')
]