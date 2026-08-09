from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from billing.models import Invoice
from complaints.models import Complaint
from notices.models import Notice
from visitors.models import Visitor
from amenities.models import AmenityBooking
from .decorators import role_required
from .forms import FlatForm, SocietyForm, BuildingForm
from .models import Flat, Society, Building


@login_required
def dashboard(request):
    user = request.user
    context = {'today': timezone.localdate()}

    if user.is_admin_or_committee():
        context.update({
            'total_flats': Flat.objects.count(),
            'pending_invoices': Invoice.objects.exclude(status=Invoice.Status.PAID).count(),
            'open_complaints': Complaint.objects.exclude(status__in=[Complaint.Status.RESOLVED, Complaint.Status.CLOSED]).count(),
            'pending_visitors': Visitor.objects.filter(status=Visitor.Status.PENDING_APPROVAL).count(),
            'recent_notices': Notice.objects.all()[:5],
            'recent_complaints': Complaint.objects.all()[:5],
            'pending_bookings': AmenityBooking.objects.filter(status=AmenityBooking.Status.REQUESTED).count(),
        })
    else:
        flat = getattr(getattr(user, 'resident_profile', None), 'flat', None)
        my_invoices = Invoice.objects.filter(flat=flat) if flat else Invoice.objects.none()
        context.update({
            'my_flat': flat,
            'my_due_invoices': my_invoices.exclude(status=Invoice.Status.PAID),
            'my_complaints': Complaint.objects.filter(raised_by=user)[:5],
            'recent_notices': Notice.objects.all()[:5],
            'my_bookings': AmenityBooking.objects.filter(booked_by=user).order_by('-booking_date')[:5],
        })

    return render(request, 'core/dashboard.html', context)


@role_required('ADMIN', 'COMMITTEE')
def flat_list(request):
    flats = Flat.objects.select_related('building', 'building__society').prefetch_related('residents__user')
    return render(request, 'core/flat_list.html', {'flats': flats})


@role_required('ADMIN', 'COMMITTEE')
def flat_add(request):
    form = FlatForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Flat added successfully.')
        return redirect('core:flats')
    return render(request, 'core/form.html', {'form': form, 'title': 'Add Flat'})


@role_required('ADMIN', 'COMMITTEE')
def society_add(request):
    form = SocietyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Society added successfully.')
        return redirect('core:flats')
    return render(request, 'core/form.html', {'form': form, 'title': 'Add Society'})


@role_required('ADMIN', 'COMMITTEE')
def building_add(request):
    form = BuildingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Building added successfully.')
        return redirect('core:flats')
    return render(request, 'core/form.html', {'form': form, 'title': 'Add Building'})
