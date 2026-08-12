from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum

from billing.models import Invoice, Payment
from complaints.models import Complaint
from notices.models import Notice
from visitors.models import Visitor
from amenities.models import AmenityBooking
from operations.models import Vehicle, Parcel, VendorAMC, Expense, MoveRequest
from .decorators import role_required
from .forms import FlatForm, SocietyForm, BuildingForm
from .models import Flat, Society, Building, ResidentProfile


@login_required
def dashboard(request):
    user = request.user
    today = timezone.localdate()
    context = {'today': today}
    if user.is_admin_or_committee():
        total_flats = Flat.objects.count()
        occupied = Flat.objects.exclude(ownership_type=Flat.OwnershipType.VACANT).count()
        context.update({
            'total_flats': total_flats,
            'occupied_flats': occupied,
            'vacant_flats': max(total_flats - occupied, 0),
            'total_residents': ResidentProfile.objects.count(),
            'pending_invoices': Invoice.objects.exclude(status=Invoice.Status.PAID).count(),
            'pending_amount': Invoice.objects.exclude(status=Invoice.Status.PAID).aggregate(total=Sum('amount'))['total'] or 0,
            'collection_month': Payment.objects.filter(paid_on__year=today.year, paid_on__month=today.month).aggregate(total=Sum('amount'))['total'] or 0,
            'open_complaints': Complaint.objects.exclude(status__in=[Complaint.Status.RESOLVED, Complaint.Status.CLOSED]).count(),
            'pending_visitors': Visitor.objects.filter(status=Visitor.Status.PENDING_APPROVAL).count(),
            'vehicles': Vehicle.objects.filter(is_active=True).count(),
            'parcels_waiting': Parcel.objects.exclude(status=Parcel.Status.COLLECTED).count(),
            'monthly_expenses': Expense.objects.filter(expense_date__year=today.year, expense_date__month=today.month).aggregate(total=Sum('amount'))['total'] or 0,
            'amc_due': VendorAMC.objects.filter(is_active=True, renewal_date__gte=today, renewal_date__lte=today + timezone.timedelta(days=30)).count(),
            'move_requests': MoveRequest.objects.filter(status=MoveRequest.Status.REQUESTED).count(),
            'recent_notices': Notice.objects.all()[:5],
            'recent_complaints': Complaint.objects.all()[:5],
            'recent_parcels': Parcel.objects.select_related('flat').order_by('-received_at')[:5],
            'pending_bookings': AmenityBooking.objects.filter(status=AmenityBooking.Status.REQUESTED).count(),
        })
    else:
        flat = getattr(getattr(user, 'resident_profile', None), 'flat', None)
        my_invoices = Invoice.objects.filter(flat=flat) if flat else Invoice.objects.none()
        context.update({'my_flat':flat,'my_due_invoices':my_invoices.exclude(status=Invoice.Status.PAID),'my_complaints':Complaint.objects.filter(raised_by=user)[:5],'recent_notices':Notice.objects.all()[:5],'my_bookings':AmenityBooking.objects.filter(booked_by=user).order_by('-booking_date')[:5],'my_parcels':Parcel.objects.filter(flat=flat).exclude(status=Parcel.Status.COLLECTED)[:5] if flat else Parcel.objects.none()})
    return render(request, 'core/dashboard.html', context)

@role_required('ADMIN','COMMITTEE')
def flat_list(request):
    flats=Flat.objects.select_related('building','building__society').prefetch_related('residents__user')
    return render(request,'core/flat_list.html',{'flats':flats})
@role_required('ADMIN','COMMITTEE')
def flat_add(request):
    form=FlatForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Flat added successfully.'); return redirect('core:flats')
    return render(request,'core/form.html',{'form':form,'title':'Add Flat'})
@role_required('ADMIN','COMMITTEE')
def society_add(request):
    form=SocietyForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Society added successfully.'); return redirect('core:flats')
    return render(request,'core/form.html',{'form':form,'title':'Add Society'})
@role_required('ADMIN','COMMITTEE')
def building_add(request):
    form=BuildingForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Building added successfully.'); return redirect('core:flats')
    return render(request,'core/form.html',{'form':form,'title':'Add Building'})
