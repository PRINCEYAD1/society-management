from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/pay/', views.record_payment, name='record_payment'),
    path('templates/', views.template_list, name='template_list'),
    path('templates/add/', views.template_add, name='template_add'),
    path('generate-monthly/', views.generate_monthly, name='generate_monthly'),
]
