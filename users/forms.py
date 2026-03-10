from django import forms
from .models import StudentProfile, StudentRegistry

class StudentEntryForm(forms.ModelForm):
    class Meta:
        model = StudentRegistry
        fields = ['full_name', 'roll_number', 'branch', 'year', 'mobile_number']
        labels = {
            'full_name': 'Full Name',
            'roll_number': 'Roll Number',
            'branch': 'Branch',
            'year': 'Year',
            'mobile_number': 'Mobile Number',
        }

class StudentRegistryForm(forms.ModelForm):
    class Meta:
        model = StudentRegistry
        fields = ['full_name', 'roll_number', 'branch', 'year', 'mobile_number']
        labels = {
            'full_name': 'Full Name',
            'roll_number': 'Roll Number',
            'branch': 'Branch',
            'year': 'Year',
            'mobile_number': 'Mobile Number (Optional)',
        }

class EmailLoginForm(forms.Form):
    email = forms.EmailField(label="Email Address")

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, label="Enter OTP")

class SecondaryLoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Enter Password")

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['full_name', 'roll_number', 'branch', 'year']

class StudentEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = StudentProfile
        fields = ['full_name', 'roll_number', 'branch', 'year']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['mobile_number'].initial = self.instance.user.mobile_number

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.email = self.cleaned_data['email']
        user.mobile_number = self.cleaned_data['mobile_number']
        if commit:
            user.save()
            profile.save()
        return profile
