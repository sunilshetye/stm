from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return f"{self.username}: {self.name}"


class Student(User):
    pass


class Teacher(User):
    pass


class Admin(User):
    pass


class Announcement(models.Model):
    teacher = Teacher()
    student = Student()
    message = models.TextField()
    acknowledgement = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=datetime.now)
