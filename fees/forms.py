from django import forms
from .models import Exam

class ExamCreationForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'semester', 'fee_regular', 'fee_supply_small', 'fee_supply_large', 'is_active']
        widgets = {
             'name': forms.TextInput(attrs={'placeholder': 'e.g., B.Tech 3-1 Regular Exams'}),
        }
        labels = {
            'name': 'Exam Name',
            'semester': 'Semester',
            'fee_regular': 'Fee (Regular)',
            'fee_supply_small': 'Fee (Supply ≤ 2 Subjects)',
            'fee_supply_large': 'Fee (Supply > 2 Subjects)',
            'is_active': 'Is Active?',
        }
