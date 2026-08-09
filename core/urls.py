from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('flats/', views.flat_list, name='flats'),
    path('flats/add/', views.flat_add, name='flat_add'),
    path('societies/add/', views.society_add, name='society_add'),
    path('buildings/add/', views.building_add, name='building_add'),
]
