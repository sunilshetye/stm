from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


class Administrator(User):
    def __str__(self):
        return f"administrator: {self.username}: {self.name}"


class Student(User):
    def __str__(self):
        return f"student: {self.username}: {self.name}"


class Teacher(User):
    def __str__(self):
        return f"teacher: {self.username}: {self.name}"


class Announcement(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, default=None)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.teacher}: {self.message}"


class Notification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, default=None)
    announcement = models.ForeignKey(Announcement, on_delete=models.PROTECT, default=None)
    acknowledgement = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=None, null=True)
