from django.db import models
from django.conf import settings
import uuid

class Exam(models.Model):
    SEMESTER_CHOICES = [
        (1, '1st Semester'),
        (2, '2nd Semester'),
        (3, '3rd Semester'),
        (4, '4th Semester'),
        (5, '5th Semester'),
        (6, '6th Semester'),
        (7, '7th Semester'),
        (8, '8th Semester'),
    ]

    name = models.CharField(max_length=100)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    fee_regular = models.DecimalField(max_digits=10, decimal_places=2, default=1200.00)
    fee_supply_small = models.DecimalField(max_digits=10, decimal_places=2, default=600.00, verbose_name="Supply (<=2 Subjects)")
    fee_supply_large = models.DecimalField(max_digits=10, decimal_places=2, default=1100.00, verbose_name="Supply (>2 Subjects)")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - Sem {self.semester}"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('QR', 'QR Code'),
    ]
    
    EXAM_TYPE_CHOICES = [
        ('REGULAR', 'Regular'),
        ('SUPPLY', 'Supply'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=50, choices=EXAM_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=50, blank=True, null=True) # broadened for other methods
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_id} - {self.student.mobile_number} - {self.status}"
