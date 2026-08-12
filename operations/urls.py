from django.urls import path
from . import views

app_name = 'operations'
urlpatterns = [
    path('vehicles/', views.vehicle_list, name='vehicles'), path('vehicles/add/', views.vehicle_add, name='vehicle_add'),
    path('parcels/', views.parcel_list, name='parcels'), path('parcels/add/', views.parcel_add, name='parcel_add'),
    path('vendors/', views.vendor_list, name='vendors'), path('vendors/add/', views.vendor_add, name='vendor_add'),
    path('expenses/', views.expense_list, name='expenses'), path('expenses/add/', views.expense_add, name='expense_add'),
    path('moves/', views.move_list, name='moves'), path('moves/add/', views.move_add, name='move_add'),
    path('workers/', views.worker_list, name='workers'), path('workers/add/', views.worker_add, name='worker_add'),
    path('workers/<int:pk>/check-in/', views.worker_checkin, name='worker_checkin'), path('workers/<int:pk>/check-out/', views.worker_checkout, name='worker_checkout'),
    path('certificates/', views.certificate_list, name='certificates'), path('certificates/add/', views.certificate_add, name='certificate_add'),
    path('meetings/', views.meeting_list, name='meetings'), path('meetings/add/', views.meeting_add, name='meeting_add'),
    path('polls/', views.poll_list, name='polls'), path('polls/add/', views.poll_add, name='poll_add'), path('polls/vote/<int:option_id>/', views.poll_vote, name='poll_vote'),
    path('assets/', views.asset_list, name='assets'), path('assets/add/', views.asset_add, name='asset_add'),
    path('emergency/', views.emergency_list, name='emergency'), path('emergency/add/', views.emergency_add, name='emergency_add'),
    path('lost-found/', views.lostfound_list, name='lostfound'), path('lost-found/add/', views.lostfound_add, name='lostfound_add'),
    path('events/', views.event_list, name='events'), path('events/add/', views.event_add, name='event_add'),
]
