from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import Exam, Transaction
from .forms import ExamCreationForm
from .utils import create_razorpay_order, verify_razorpay_payment_signature
from django.views.decorators.csrf import csrf_exempt

# --- New RBAC Views ---

@login_required
def add_exam_view(request):
    if not request.user.is_exam_branch and not request.user.is_superuser:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = ExamCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam added successfully!')
            return redirect('dashboard')
    else:
        form = ExamCreationForm()
        
    return render(request, 'fees/add_exam.html', {'form': form})

@login_required
def exam_stats_view(request):
    if not request.user.is_exam_branch and not request.user.is_superuser:
        return redirect('dashboard')
    
    # Logic to count paid students per exam
    exams = Exam.objects.all()
    stats = []
    
    for exam in exams:
        paid_count = Transaction.objects.filter(exam=exam, status='SUCCESS').count()
        stats.append({
            'exam': exam,
            'paid_count': paid_count
        })
        
    return render(request, 'fees/exam_stats.html', {'stats': stats})

# --- Payment Flow Views ---

@login_required
def select_exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Check if already paid
    existing_txn = Transaction.objects.filter(student=request.user, exam=exam, status='SUCCESS').exists()
    if existing_txn:
        messages.info(request, 'You have already paid for this exam.')
        return redirect('dashboard')

    if request.method == 'POST':
        # Create Pending Transaction
        exam_type = request.POST.get('exam_category', 'REGULAR') # Match template name
        
        if exam_type == 'REGULAR':
            amount = exam.fee_regular
        else:
            try:
                subject_count = int(request.POST.get('subject_count', 0))
            except ValueError:
                subject_count = 0
                
            if subject_count <= 2:
                amount = exam.fee_supply_small
            else:
                amount = exam.fee_supply_large
        
        transaction = Transaction.objects.create(
            student=request.user,
            exam=exam,
            exam_type=exam_type,
            amount=amount,
            status='PENDING'
        )
        return redirect('payment_page', transaction_id=transaction.id)
        
    return render(request, 'fees/select_exam.html', {'exam': exam})

@login_required
def payment_page_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, student=request.user)
    
    if transaction.status == 'SUCCESS':
        return redirect('receipt', transaction_id=transaction.id)
        
    # Create Razorpay Order if not exists
    if not transaction.razorpay_order_id:
        rp_order = create_razorpay_order(
            amount=transaction.amount, 
            currency='INR', 
            receipt=str(transaction.payment_id),
            notes={'transaction_id': transaction.id, 'exam': transaction.exam.name}
        )
        transaction.razorpay_order_id = rp_order['id']
        transaction.save()
        
    context = {
        'transaction': transaction,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': transaction.razorpay_order_id,
        'razorpay_amount': int(transaction.amount * 100), # Amount in paisa
        'callback_url': request.build_absolute_uri('/fees/payment-callback/') # Simplified
    }
        
    return render(request, 'fees/payment.html', context)

@csrf_exempt
def payment_callback_view(request):
    if request.method == "POST":
        data = request.POST
        razorpay_order_id = data.get('razorpay_order_id', '')
        razorpay_payment_id = data.get('razorpay_payment_id', '')
        razorpay_signature = data.get('razorpay_signature', '')

        # Verify Signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            transaction = Transaction.objects.get(razorpay_order_id=razorpay_order_id)
        except Transaction.DoesNotExist:
            return render(request, 'fees/payment_failed.html', {'error': 'Transaction not found'})

        if verify_razorpay_payment_signature(params_dict):
            transaction.status = 'SUCCESS'
            transaction.payment_method = 'RAZORPAY' # Or 'Online'
            transaction.save()
            messages.success(request, 'Payment Successful!')
            return redirect('receipt', transaction_id=transaction.id)
        else:
            transaction.status = 'FAILED'
            transaction.save()
            return render(request, 'fees/payment_failed.html', {'error': 'Signature Verification Failed'})
    else:
        return redirect('dashboard')

@login_required
def receipt_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, student=request.user)
    
    if transaction.status != 'SUCCESS':
        return redirect('dashboard')
        
    return render(request, 'fees/receipt.html', {'transaction': transaction})

@login_required
def paid_students_list(request):
    if not request.user.is_exam_branch and not request.user.is_superuser:
        return redirect('dashboard')
    
    transactions = Transaction.objects.filter(status='SUCCESS').select_related('student', 'exam', 'student__student_profile').order_by('-timestamp')
    
    return render(request, 'fees/paid_students_list.html', {'transactions': transactions})
