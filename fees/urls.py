from django.urls import path
from . import views

urlpatterns = [
    path('select/<int:exam_id>/', views.select_exam_view, name='select_exam'),
    path('payment/<int:transaction_id>/', views.payment_page_view, name='payment_page'),
    path('payment-callback/', views.payment_callback_view, name='payment_callback'),
    path('receipt/<int:transaction_id>/', views.receipt_view, name='receipt'),
    path('add-exam/', views.add_exam_view, name='add_exam'),
    path('stats/', views.exam_stats_view, name='exam_stats'),
    path('paid-students/', views.paid_students_list, name='paid_students_list'),
]
