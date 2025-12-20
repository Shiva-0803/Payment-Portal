from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .forms import EmailLoginForm, OTPForm, StudentRegistrationForm, SecondaryLoginForm, StudentEditForm
from .models import CustomUser, StudentProfile
from .utils import send_email_otp, generate_otp
from fees.models import Transaction, Exam
from fees.forms import ExamCreationForm

def home_view(request):
    # Auto-logout Staff/Exam Branch when visiting Home Page
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or request.user.is_exam_branch):
        logout(request)
    return render(request, 'users/home.html')

def internal_login_view(request):
    if request.user.is_authenticated:
        # If already logged in as Staff/Exam Branch, go to dashboard
        if request.user.is_staff or request.user.is_superuser or request.user.is_exam_branch:
             return redirect('dashboard')
        
        # If logged in as Student but trying to access Internal Login, logout first
        if request.user.is_student:
             logout(request)
             # Proceed to render login form below
    role = request.GET.get('role')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        # Try to get role from POST (hidden input), fallback to GET
        role = request.POST.get('role', role)
        
        print(f"DEBUG LOGIN: Role={role}") # Debugging
        
        if form.is_valid():
            user = form.get_user()
            print(f"DEBUG USER: {user.email} | Staff: {user.is_staff} | Exam: {user.is_exam_branch}")

            # Strict Role Validation
            if role == 'admin':
                # Allowed: Superuser OR (Staff AND NOT Exam Branch)
                if not (user.is_superuser or (user.is_staff and not user.is_exam_branch)):
                    print("DEBUG: Blocking Exam Branch/User from Admin")
                    form.add_error(None, "Invalid credentials for Admin Login.")
                    return render(request, 'users/internal_login.html', {'form': form, 'role': role})
            
            elif role == 'exam_branch':
                # Allowed: Exam Branch Only
                if not user.is_exam_branch:
                    print("DEBUG: Blocking Non-Exam Branch from Exam Login")
                    form.add_error(None, "Invalid credentials for Exam Branch Login.")
                    return render(request, 'users/internal_login.html', {'form': form, 'role': role})
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'users/internal_login.html', {'form': form, 'role': role})

def login_view(request):
    if request.user.is_authenticated:
        # If already logged in as Student, go to dashboard
        if request.user.is_student and not (request.user.is_staff or request.user.is_superuser):
            return redirect('dashboard')
            
        # If logged in as Admin/Exam Branch but trying to access Student Login, logout first
        if request.user.is_staff or request.user.is_superuser or request.user.is_exam_branch:
            logout(request)
            # Proceed to render login form below
    
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Dynamic OTP Generation
            otp = generate_otp()
            
            # Store in session
            request.session['auth_email'] = email
            request.session['auth_otp'] = otp
            
            # Send Email
            sent = send_email_otp(email, otp)
            
            if sent:
                messages.success(request, f'OTP sent to {email}')
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
                # Fallback for dev/testing if API fails
                messages.warning(request, f'DEV MODE: OTP is {otp}')
            
            return redirect('otp_verify')
    else:
        form = EmailLoginForm()
    return render(request, 'users/login.html', {'form': form})

def otp_verify_view(request):
    if 'auth_email' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if otp == request.session.get('auth_otp'):
                email = request.session.get('auth_email')
                user, created = CustomUser.objects.get_or_create(email=email)
                
                # Cleanup OTP session
                del request.session['auth_otp']
                
                # Check for RBAC - Secondary Auth for Staff
                if user.is_staff or user.is_superuser or user.is_exam_branch:
                     # Keep auth_email in session for next step
                     return redirect('verify_password')
                
                # Student Logic
                if created:
                    user.is_student = True
                    user.save()
                
                login(request, user)
                del request.session['auth_email'] # Cleanup email for students
                
                if not hasattr(user, 'student_profile') and user.is_student:
                    return redirect('register_student')
                return redirect('dashboard')
            else:
                form.add_error('otp', 'Invalid OTP')
    else:
        form = OTPForm()
    return render(request, 'users/otp_verify.html', {'form': form})

def verify_password_view(request):
    if 'auth_email' not in request.session:
        return redirect('login')
    
    email = request.session['auth_email']
    
    if request.method == 'POST':
        form = SecondaryLoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            try:
                user = CustomUser.objects.get(email=email)
                if user.check_password(password):
                    login(request, user)
                    del request.session['auth_email']
                    return redirect('dashboard')
                else:
                    form.add_error('password', 'Incorrect Password')
            except CustomUser.DoesNotExist:
                 return redirect('login') # Should not happen
    else:
        form = SecondaryLoginForm()
    
    return render(request, 'users/verify_password.html', {'form': form})

@login_required
def register_student_view(request):
    if hasattr(request.user, 'student_profile'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def dashboard_view(request):
    user = request.user
    context = {}
    
    if user.is_exam_branch:
        return redirect('exam_dashboard')
    elif user.is_staff or user.is_superuser:
        return redirect('admin_dashboard')
    else:
        # Student dashboard logic
        if not hasattr(user, 'student_profile'):
             return redirect('register_student')
        
        exams = Exam.objects.filter(is_active=True)
        my_transactions = Transaction.objects.filter(student=user).order_by('-timestamp')
        context['exams'] = exams
        context['transactions'] = my_transactions
        context['student_profile'] = user.student_profile
        context['is_student'] = True

    return render(request, 'users/dashboard.html', context)

@login_required
def admin_dashboard_view(request):
    if request.user.is_exam_branch:
        return redirect('exam_dashboard')
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('dashboard')
        
    branch = request.GET.get('branch')
    year = request.GET.get('year')
    
    students = StudentProfile.objects.all().select_related('user')
    
    if branch:
        students = students.filter(branch=branch)
    if year:
        students = students.filter(year=year)
        
    context = {
        'students': students,
        'branch_choices': StudentProfile.BRANCH_CHOICES,
        'year_choices': StudentProfile.YEAR_CHOICES,
        'selected_branch': branch,
        'selected_year': int(year) if year else None,
    }
    return render(request, 'users/admin_dashboard.html', context)

@login_required
def exam_dashboard_view(request):
    if not request.user.is_exam_branch:
        if request.user.is_superuser:
             return redirect('admin_dashboard')
        return redirect('dashboard')
        
    transactions = Transaction.objects.filter(status='SUCCESS').order_by('-timestamp')
    
    # Exam Creation Handling
    if request.method == 'POST' and 'add_exam' in request.POST:
        exam_form = ExamCreationForm(request.POST)
        if exam_form.is_valid():
            exam_form.save()
            messages.success(request, 'Exam added successfully!')
            return redirect('exam_dashboard')
    else:
        exam_form = ExamCreationForm()

    # Student Filter Logic (Similar to Admin)
    branch = request.GET.get('branch')
    year = request.GET.get('year')
    students = StudentProfile.objects.all().select_related('user')

    if branch:
        students = students.filter(branch=branch)
    if year:
        students = students.filter(year=year)

    context = {
        'transactions': transactions,
        'is_exam_branch': True,
        'exam_form': exam_form,
        'students': students,
        'branch_choices': StudentProfile.BRANCH_CHOICES,
        'year_choices': StudentProfile.YEAR_CHOICES,
        'selected_branch': branch,
        'selected_year': int(year) if year else None,
    }
    return render(request, 'users/exam_dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def edit_student_view(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student details updated successfully.')
            return redirect('admin_dashboard')
    else:
        form = StudentEditForm(instance=student)
    return render(request, 'users/edit_student.html', {'form': form, 'student': student})

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def delete_student_view(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    user = student.user
    student.delete()
    user.delete()
    messages.success(request, 'Student deleted successfully.')
    return redirect('admin_dashboard')
