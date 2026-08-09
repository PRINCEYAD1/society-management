from django.urls import path
from . import views

app_name = 'staffmgmt'

urlpatterns = [
    path('', views.staff_list, name='list'),
    path('add/', views.staff_add, name='add'),
    path('<int:pk>/', views.staff_detail, name='detail'),
    path('<int:pk>/mark-attendance/', views.mark_attendance, name='mark_attendance'),
]
