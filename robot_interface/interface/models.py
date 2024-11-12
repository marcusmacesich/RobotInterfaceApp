from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Robot(models.Model):
    name = models.CharField(max_length=100)
    # Add any other fields relevant to the robot

    def __str__(self):
        return self.name

class Program(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE)
    code = models.TextField()
    status = models.TextField()
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username}'s program for {self.robot.name}"