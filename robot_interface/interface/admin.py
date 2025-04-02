from django.contrib import admin
from .models import Robot, Program, Functions, SavedProgram, WebSocketIP

# Register your models here.
admin.site.register(Robot)
admin.site.register(Program)
admin.site.register(Functions)
admin.site.register(SavedProgram)
admin.site.register(WebSocketIP)