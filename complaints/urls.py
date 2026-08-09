from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list, name='list'),
    path('add/', views.complaint_add, name='add'),
    path('<int:pk>/', views.complaint_detail, name='detail'),
    path('<int:pk>/update-status/', views.update_status, name='update_status'),
]
