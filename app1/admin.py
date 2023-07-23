from django.contrib import admin
from .models import Announcement,User

# Register your models here.
admin.site.register(User)
admin.site.register(Announcement)