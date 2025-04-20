from django.contrib import admin
from .models import Robot, Program, Functions, SavedProgram, WebSocketIP,LabDocument

# Register your models here.
admin.site.register(Robot)
admin.site.register(Program)
admin.site.register(Functions)
admin.site.register(SavedProgram)
admin.site.register(WebSocketIP)
admin.site.register(LabDocument)