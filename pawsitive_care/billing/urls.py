from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.billing_list, name='billing_list'),
    path('create/', views.billing_create, name='billing_create'),
    path('<int:billing_id>/', views.billing_detail, name='billing_detail'),
    path('<int:billing_id>/update/', views.billing_update, name='billing_update'),
    path('<int:billing_id>/delete/', views.billing_delete, name='billing_delete'),
    path('<int:billing_id>/paid/', views.mark_billing_paid, name='billing_mark_paid'),
     path('pay/', views.pay_bill, name='pay_bill'),
]
