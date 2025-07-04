from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Table for a robot along with its IP
class Robot(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    # Add any other fields relevant to the robot

    def __str__(self):
        return self.name

# Table for a program used by the robot
class Program(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE)
    code = models.TextField()
    status = models.TextField()
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username}'s program for {self.robot.name}"

# Table for a program saved for recall
class SavedProgram(models.Model):
    program_name = models.TextField()
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

# Table to store function templates for IDE page
class Functions(models.Model):
    func_name = models.TextField(max_length=100)
    func_description = models.TextField(max_length=250)

    def __str__(self):
        return self.func_name
    
# Store the IP address of the WebSockets server
class WebSocketIP(models.Model):
    web_ip_address = models.TextField(max_length=20)

    def __str__(self):
        return self.web_ip_address

class code_templates(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True) # Optional description
    value = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)     # Automatically updated on save

    def __str__(self):
        return self.name # For a readable representation in the admin and shell

# Model to describe uploaded Lab Documents
class LabDocument(models.Model):
    display_name = models.TextField(max_length=50)
    file_name = models.TextField(max_length=50)

    def __str__(self):
        return self.display_name