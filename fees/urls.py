from django.urls import path
from . import views

urlpatterns = [
    path('select/<int:exam_id>/', views.select_exam_view, name='select_exam'),
    path('payment/<int:transaction_id>/', views.payment_mock_view, name='payment_mock'),
    path('receipt/<int:transaction_id>/', views.receipt_view, name='receipt'),
    path('add-exam/', views.add_exam_view, name='add_exam'),
    path('stats/', views.exam_stats_view, name='exam_stats'),
    path('paid-students/', views.paid_students_list, name='paid_students_list'),
]
