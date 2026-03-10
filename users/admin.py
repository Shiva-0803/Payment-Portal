from django.contrib import admin
from .models import CustomUser, StudentProfile, StudentRegistry

admin.site.register(CustomUser)
admin.site.register(StudentProfile)
admin.site.register(StudentRegistry)
