from django.urls import path
from . import views

app_name = 'visitors'

urlpatterns = [
    path('', views.visitor_list, name='list'),
    path('add/', views.visitor_add, name='add'),
    path('<int:pk>/approve/', views.visitor_approve, name='approve'),
    path('<int:pk>/deny/', views.visitor_deny, name='deny'),
    path('<int:pk>/checkin/', views.visitor_checkin, name='checkin'),
    path('<int:pk>/checkout/', views.visitor_checkout, name='checkout'),
]
