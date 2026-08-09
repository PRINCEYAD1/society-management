from django.urls import path
from . import views

app_name = 'amenities'

urlpatterns = [
    path('', views.amenity_list, name='list'),
    path('add/', views.amenity_add, name='add'),
    path('<int:pk>/book/', views.amenity_book, name='book'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/confirm/', views.booking_confirm, name='booking_confirm'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
]
