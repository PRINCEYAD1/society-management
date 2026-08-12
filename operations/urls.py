from django.urls import path
from . import views

app_name = 'operations'
urlpatterns = [
    path('vehicles/', views.vehicle_list, name='vehicles'), path('vehicles/add/', views.vehicle_add, name='vehicle_add'),
    path('parcels/', views.parcel_list, name='parcels'), path('parcels/add/', views.parcel_add, name='parcel_add'),
    path('vendors/', views.vendor_list, name='vendors'), path('vendors/add/', views.vendor_add, name='vendor_add'),
    path('expenses/', views.expense_list, name='expenses'), path('expenses/add/', views.expense_add, name='expense_add'),
    path('moves/', views.move_list, name='moves'), path('moves/add/', views.move_add, name='move_add'),
]
