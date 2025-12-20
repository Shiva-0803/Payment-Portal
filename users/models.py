from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    is_student = models.BooleanField(default=False)
    is_exam_branch = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=100, default='')
    roll_number = models.CharField(max_length=20, unique=True)
    BRANCH_CHOICES = [
        ('IT', 'Information Technology (IT)'),
        ('CSE', 'Computer Science & Engineering (CSE)'),
        ('CSD', 'Computer Science & Design (CSD)'),
        ('EEE', 'Electrical & Electronics Engineering (EEE)'),
        ('ECE', 'Electronics & Communication Engineering (ECE)'),
        ('MECH', 'Mechanical Engineering (MECH)'),
        ('CIV', 'Civil Engineering (CIV)'),
    ]

    YEAR_CHOICES = [
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year'),
    ]

    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES)
    year = models.IntegerField(choices=YEAR_CHOICES)

    def __str__(self):
        return f"{self.roll_number} - {self.user.mobile_number}"
