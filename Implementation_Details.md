# Chapter: System Implementation

This section details the core implementation of the system, highlighting the essential code segments and logic used to build the Exam Fee Payment Portal. The application follows the Django web framework's Model-View-Template (MVT) architecture.

## 1. Database Model Implementation

The system’s data structure is designed to robustly handle user authentication, student profiles, exam records, and financial transactions.

### User Management Models
The core authentication system overrides Django's default user model to use an email-based login system while introducing custom roles (Student, Exam Branch, Admin).

```python
# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Role-Based Access Control flags
    is_student = models.BooleanField(default=False)
    is_exam_branch = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=100, default='')
    roll_number = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES)
    year = models.IntegerField(choices=YEAR_CHOICES)
```

### Fee and Transaction Models
To keep track of exams and payment logic, the `Exam` and `Transaction` models were implemented. The `Transaction` model is vital for maintaining audit logs of payment statuses and associating payments with third-party gateways (Stripe/Razorpay).

```python
# fees/models.py
import uuid
from django.db import models
from django.conf import settings

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    EXAM_TYPE_CHOICES = [
        ('REGULAR', 'Regular'),
        ('SUPPLY', 'Supply'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=50, choices=EXAM_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Third-party payment tracking
    payment_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=200, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)
```

## 2. Authentication and Role-Based Access Control (RBAC)

The portal implements a secure dynamic OTP-based login for students and a secondary, strict password-based authentication for administrative and exam branch staff.

### OTP Generation and Verification
The system utilizes a session-based approach to temporarily store and verify One-Time Passwords sent to the user's registered email.

```python
# users/views.py
def otp_verify_view(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            session_otp = request.session.get('auth_otp')
            
            # OTP Validation
            if str(otp) == str(session_otp):
                email = request.session.get('auth_email')
                user, created = CustomUser.objects.get_or_create(email=email)
                
                del request.session['auth_otp'] # Security cleanup
                
                # RBAC Logic checking
                if user.is_staff or user.is_superuser or user.is_exam_branch:
                    return redirect('verify_password') # Secondary Auth
                
                if created:
                    user.is_student = True
                    user.save()
                
                login(request, user)
                return redirect('dashboard')
```

## 3. Payment Gateway Integration (Stripe)

A critical functionality of the application is the secure processing of exam fees online. The `stripe` API is integrated for generating checkout sessions and managing transaction callbacks.

### Creating a Stripe Checkout Session
When a student selects an exam and proceeds to pay, a pending transaction is created, followed by a Stripe Checkout Session instance.

```python
# fees/views.py
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_page_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, student=request.user)
    
    if not transaction.stripe_session_id:
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': transaction.exam.name,
                        },
                        'unit_amount': int(transaction.amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/fees/stripe/success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/fees/stripe/cancel/'),
                client_reference_id=str(transaction.id)
            )
            transaction.stripe_session_id = checkout_session.id
            transaction.save()
        except Exception as e:
            messages.error(request, str(e))
            return redirect('dashboard')
            
    # View renders payment interface with Stripe Session Context
```

### Payment Verification Webhook/Success Callback
After the payment process completes, the portal handles the response to update the student's transaction history correctly.

```python
# fees/views.py
@login_required
def stripe_success_view(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            transaction_id = session.client_reference_id
            transaction = get_object_or_404(Transaction, id=transaction_id)
            
            if session.payment_status == 'paid':
                transaction.status = 'SUCCESS'
                transaction.payment_method = 'STRIPE'
                transaction.save()
                messages.success(request, 'Payment Successful!')
                return redirect('receipt', transaction_id=transaction.id)
            else:
                transaction.status = 'FAILED'
                transaction.save()
                return redirect('payment_page', transaction_id=transaction.id)
                
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            
    return redirect('dashboard')
```

## 4. Administrative Dashboards and Data Filtering
The application offers custom views targeted strictly at high-level staff members for filtering student registries. This employs scalable query parameters.

```python
# users/views.py
@login_required
def admin_dashboard_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('dashboard')
        
    branch = request.GET.get('branch')
    year = request.GET.get('year')
    
    students = StudentProfile.objects.select_related('user')
    
    # Conditional queryset filtering
    if branch:
        students = students.filter(branch=branch)
    if year:
        students = students.filter(year=year)
        
    context = {
        'students': students,
        'branch_choices': StudentProfile.BRANCH_CHOICES,
        'year_choices': StudentProfile.YEAR_CHOICES,
    }
    return render(request, 'users/admin_dashboard.html', context)
```

## 5. User Interface Implementation (Index/Home Page)
The application’s landing page (`home.html` functioning as `index.html`) is designed with a modern, glass-morphism UI powered by TailwindCSS. It provides clear, role-based entry points for Students, Administrators, and Exam Branch Personnel.

```html
<!-- users/templates/users/home.html -->
{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="min-h-screen flex items-center justify-center relative overflow-hidden py-12 px-4 sm:px-6 lg:px-8">
    <!-- Static Background with Overlay -->
    <div class="absolute inset-0 z-0">
        <div class="absolute inset-0 bg-cover bg-center" style="background-image: url('{% static 'home_bg.jpg' %}');"></div>
        <div class="absolute inset-0 bg-gray-900/80"></div>
    </div>

    <!-- Main Content Grid -->
    <div class="max-w-4xl w-full space-y-8 relative z-10 glass-card p-8 rounded-2xl border border-white/10 shadow-2xl backdrop-blur-sm">
        <div class="text-center">
            <h2 id="greeting-text" class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-indigo-500 mb-2 animate-pulse">
                Welcome!
            </h2>
            <h1 class="text-4xl font-extrabold text-white tracking-tight sm:text-5xl mb-4">
                Select User Role
            </h1>
        </div>

        <!-- Role Selection Cards -->
        <div class="mt-10 grid grid-cols-1 gap-8 sm:grid-cols-3">
            
            <!-- Student Entry -->
            <a href="{% url 'login' %}" class="relative group bg-gray-800 p-6 rounded-lg shadow-lg hover:bg-gray-700 transition duration-300 ease-in-out transform hover:-translate-y-1">
                <span class="rounded-lg inline-flex p-3 bg-indigo-500 text-white ring-4 ring-white">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <!-- SVG Path -->
                    </svg>
                </span>
                <div class="mt-8">
                    <h3 class="text-lg font-medium">Student</h3>
                    <p class="mt-2 text-sm text-gray-400">Login with email OTP to view results and pay fees.</p>
                </div>
            </a>

            <!-- Administrator Entry -->
            <a href="{% url 'internal_login' %}?role=admin" class="relative group bg-gray-800 p-6 rounded-lg shadow-lg hover:bg-gray-700 transition duration-300 ease-in-out transform hover:-translate-y-1">
                <span class="rounded-lg inline-flex p-3 bg-purple-500 text-white ring-4 ring-white">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <!-- SVG Path -->
                    </svg>
                </span>
                <div class="mt-8">
                    <h3 class="text-lg font-medium">Admin</h3>
                    <p class="mt-2 text-sm text-gray-400">Manage students and track system logs.</p>
                </div>
            </a>

            <!-- Exam Branch Entry -->
            <a href="{% url 'internal_login' %}?role=exam_branch" class="relative group bg-gray-800 p-6 rounded-lg shadow-lg hover:bg-gray-700 transition duration-300 ease-in-out transform hover:-translate-y-1">
                <span class="rounded-lg inline-flex p-3 bg-green-500 text-white ring-4 ring-white">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <!-- SVG Path -->
                    </svg>
                </span>
                <div class="mt-8">
                    <h3 class="text-lg font-medium">Exam Branch</h3>
                    <p class="mt-2 text-sm text-gray-400">Manage exam configurations and view enrolled students.</p>
                </div>
            </a>
            
        </div>
    </div>
</div>
{% endblock %}
```
### Client-Side Logic (JavaScript)
The application leverages vanilla JavaScript to enhance user experience and provide dynamic, responsive client-side behaviors without heavy framework overhead. Some key implementations include:

1. **Dynamic Welcome Message**:
   An inline script calculates the user's local browser time upon page load (`DOMContentLoaded`) and dynamically injects a contextual greeting ("Good Morning", "Good Afternoon", or "Good Evening") into the landing page interface, establishing an inviting user experience.

```javascript
// Example from home.html
document.addEventListener('DOMContentLoaded', function () {
    const hour = new Date().getHours();
    let greeting = "Welcome";
    
    if (hour >= 5 && hour < 12) greeting = "Good Morning";
    else if (hour >= 12 && hour < 17) greeting = "Good Afternoon";
    else if (hour >= 17 && hour < 22) greeting = "Good Evening";

    const greetingElement = document.getElementById('greeting-text');
    if (greetingElement) {
        greetingElement.textContent = greeting + ", User!";
    }
});
```

2. **Form Validation & Interactive Enhancements**:
   Beyond simple greetings, JavaScript is strategically utilized across various application templates (such as transaction flows or exam selections) to ensure client-side data validity, manipulate the Document Object Model (DOM) for instant user feedback, and manage modal or state transitions securely before backend submission.

### SVG Icon Usage
Responsive vector graphics (`SVG` icons) from Heroicons are utilized to create a rich graphical menu. Using inline SVGs cuts down on page weight and external HTTP requests. Each role choice has a distinct color scheme using Tailwind's ring features for focus states (`ring-indigo-500`, `ring-purple-500`, `ring-green-500`, `ring-pink-500`) to increase usability and navigational clarity.

## 6. Django Application Configuration (`apps.py`)
The project utilizes Django's modular concept of "Apps" to cleanly separate business logical components, such as `users` and `fees`. Each application requires configuration metadata via `apps.py`.

```python
# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = 'users'
    # Default auto field for primary keys can be configured here 
    # e.g., default_auto_field = 'django.db.models.BigAutoField'
```

### Purpose of Application Configuration
The `AppConfig` class acts as the central registry for the specific application (e.g., `UsersConfig`). It provides the Django framework with structural metadata, primarily the `name` attribute which ensures that when the project starts up, Django knows precisely where to locate the models, views, templates, and static directories for this particular module. Furthermore, although not explicitly defined in the minimal configuration, developers can hook into the `AppConfig.ready()` initialization lifecycle method to register signals, import dependencies that must load post-startup, or connect third-party APIs exactly when the specific app becomes active.

## 7. Security Implementation

Maintaining the integrity of user data and backend functionality is crucial, especially in an application handling payments. This system relies heavily on Django's built-in security features, reinforced by custom logical checks.

### Cross-Site Request Forgery (CSRF) Protection
Django inherently protects against Cross-Site Request Forgery via CSRF tokens. This token is required on every POST form submitted by users, ensuring that the request genuinely originated from the portal rather than a malicious third-party site.

```html
<!-- Example of CSRF usage in a Django Template -->
<form method="POST" action="{% url 'login' %}">
    {% csrf_token %}
    <!-- Form Inputs -->
    <button type="submit">Submit</button>
</form>
```

### View-Level Authorization (Decorators)
Beyond authentication, specific endpoints dynamically enforce authorization. The `@login_required` decorator secures the majority of the views. However, critical endpoints use `@user_passes_test` or internal `if` statement logic to evaluate user flags (`is_student`, `is_staff`, `is_exam_branch`) before rendering sensitive data like the `admin_dashboard` or `exam_stats`.

```python
# users/views.py
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def add_student_view(request):
    # Only staff members can access this block
    # ...
```

### Defense-in-Depth Authentication
The portal does not rely on simple passwords for students. Using an ephemeral, One-Time Password (OTP) tied to an email session adds a layer of Two-Factor Authentication (2FA) for student accounts. For administrative accounts (`is_staff`, `is_exam_branch`), the system mandates a secondary secure password verification checkpoint to mitigate the risk of compromised active sessions.

### Environment Variable Secrets
Sensitive infrastructure credentials are decoupled from the application logic entirely. Using packages like `python-dotenv`, production keys (like `STRIPE_SECRET_KEY` or `EMAIL_HOST_PASSWORD`) are loaded strictly from an untracked `.env` file, preventing accidental exposure of these credentials into version control software.
