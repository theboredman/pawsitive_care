from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # My bills / dashboard
    path('', views.my_bills, name='my_bills'),

    # Add a new bill
    path('add/', views.add_bill, name='add_bill'),

    # View all bills (admin/staff view)
    path('view/', views.view_bills, name='view_bills'),

    # Bill detail
    path('pay/<int:billing_id>/', views.pay_bill, name='pay_bill'),
    path('servicecost/', views.servicecost_list, name='servicecost_list'),
    path('servicecost/delete/<int:pk>/', views.servicecost_delete, name='servicecost_delete'),
    path('success/', views.payment_success, name='payment_success')

   
]
