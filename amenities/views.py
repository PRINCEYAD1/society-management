from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.decorators import role_required
from .forms import AmenityForm, AmenityBookingForm
from .models import Amenity, AmenityBooking


@login_required
def amenity_list(request):
    amenities = Amenity.objects.filter(is_active=True)
    return render(request, 'amenities/amenity_list.html', {'amenities': amenities})


@role_required('ADMIN', 'COMMITTEE')
def amenity_add(request):
    form = AmenityForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Amenity added.')
        return redirect('amenities:list')
    return render(request, 'core/form.html', {'form': form, 'title': 'Add Amenity'})


@login_required
def amenity_book(request, pk):
    amenity = get_object_or_404(Amenity, pk=pk)
    form = AmenityBookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.amenity = amenity
        booking.booked_by = request.user
        booking.save()
        messages.success(request, f'Booking requested for {amenity.name}.')
        return redirect('amenities:my_bookings')
    return render(request, 'core/form.html', {'form': form, 'title': f'Book {amenity.name}'})


@login_required
def my_bookings(request):
    user = request.user
    if user.is_admin_or_committee():
        bookings = AmenityBooking.objects.select_related('amenity', 'booked_by')
    else:
        bookings = AmenityBooking.objects.filter(booked_by=user).select_related('amenity')
    return render(request, 'amenities/my_bookings.html', {'bookings': bookings})


@role_required('ADMIN', 'COMMITTEE')
def booking_confirm(request, pk):
    booking = get_object_or_404(AmenityBooking, pk=pk)
    booking.status = AmenityBooking.Status.CONFIRMED
    booking.save()
    messages.success(request, 'Booking confirmed.')
    return redirect('amenities:my_bookings')


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(AmenityBooking, pk=pk)
    if booking.booked_by_id != request.user.id and not request.user.is_admin_or_committee():
        messages.error(request, "You can't cancel this booking.")
        return redirect('amenities:my_bookings')
    booking.status = AmenityBooking.Status.CANCELLED
    booking.save()
    messages.info(request, 'Booking cancelled.')
    return redirect('amenities:my_bookings')
