from django.urls import path
from . import views

app_name = 'notices'

urlpatterns = [
    path('', views.notice_list, name='list'),
    path('add/', views.notice_add, name='add'),
    path('<int:pk>/', views.notice_detail, name='detail'),
    path('<int:pk>/delete/', views.notice_delete, name='delete'),
]
