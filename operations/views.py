from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from core.decorators import role_required
from .models import (Vehicle, Parcel, VendorAMC, Expense, MoveRequest, DomesticWorker,
                     StaffAttendance, CertificateRequest, SocietyMeeting, Poll, PollOption,
                     PollVote, SocietyAsset, EmergencyContact, LostFoundItem, SocietyEvent)
from .forms import (VehicleForm, ParcelForm, VendorAMCForm, ExpenseForm, MoveRequestForm,
                    DomesticWorkerForm, CertificateRequestForm, SocietyMeetingForm, PollForm,
                    SocietyAssetForm, EmergencyContactForm, LostFoundForm, SocietyEventForm)


def _save_form(request, form_class, title, success_url, set_user_field=None):
    form = form_class(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        if set_user_field:
            setattr(obj, set_user_field, request.user)
        obj.save()
        if hasattr(form, 'save_m2m'):
            form.save_m2m()
        messages.success(request, f'{title} saved successfully.')
        return redirect(success_url)
    return render(request, 'operations/form.html', {'form': form, 'title': title})


def _simple_list(request, items, title, kind, add_url=None):
    return render(request, 'operations/list.html', {'items':items, 'title':title, 'kind':kind, 'add_url':add_url})

@login_required
def vehicle_list(request):
    qs = Vehicle.objects.select_related('flat', 'flat__building')
    if not request.user.is_admin_or_committee():
        flat = getattr(getattr(request.user, 'resident_profile', None), 'flat', None)
        qs = qs.filter(flat=flat) if flat else qs.none()
    return _simple_list(request, qs, 'Parking & Vehicles', 'vehicle', 'operations:vehicle_add' if request.user.is_admin_or_committee() else None)

@role_required('ADMIN','COMMITTEE')
def vehicle_add(request): return _save_form(request, VehicleForm, 'Add Vehicle', 'operations:vehicles')

@login_required
def parcel_list(request):
    qs = Parcel.objects.select_related('flat').order_by('-received_at')
    if not request.user.is_admin_or_committee() and getattr(request.user, 'role', '') != 'SECURITY':
        flat = getattr(getattr(request.user, 'resident_profile', None), 'flat', None)
        qs = qs.filter(flat=flat) if flat else qs.none()
    can_add = request.user.is_admin_or_committee() or getattr(request.user,'role','') == 'SECURITY'
    return _simple_list(request, qs, 'Parcels & Deliveries', 'parcel', 'operations:parcel_add' if can_add else None)

@role_required('ADMIN','COMMITTEE','SECURITY')
def parcel_add(request): return _save_form(request, ParcelForm, 'Log Parcel / Delivery', 'operations:parcels', 'received_by')

@role_required('ADMIN','COMMITTEE')
def vendor_list(request): return _simple_list(request, VendorAMC.objects.all(), 'Vendors & AMC', 'vendor', 'operations:vendor_add')
@role_required('ADMIN','COMMITTEE')
def vendor_add(request): return _save_form(request, VendorAMCForm, 'Add Vendor / AMC', 'operations:vendors')
@role_required('ADMIN','COMMITTEE')
def expense_list(request): return _simple_list(request, Expense.objects.all(), 'Society Expenses', 'expense', 'operations:expense_add')
@role_required('ADMIN','COMMITTEE')
def expense_add(request): return _save_form(request, ExpenseForm, 'Record Expense', 'operations:expenses', 'created_by')

@login_required
def move_list(request):
    qs = MoveRequest.objects.select_related('flat','requested_by').order_by('-created_at')
    if not request.user.is_admin_or_committee(): qs = qs.filter(requested_by=request.user)
    return _simple_list(request, qs, 'Move In / Move Out', 'move', 'operations:move_add')
@login_required
def move_add(request): return _save_form(request, MoveRequestForm, 'Request Move In / Move Out', 'operations:moves', 'requested_by')

@login_required
def worker_list(request):
    return _simple_list(request, DomesticWorker.objects.prefetch_related('flats').all(), 'Domestic Staff', 'worker', 'operations:worker_add' if (request.user.is_admin_or_committee() or getattr(request.user,'role','') == 'SECURITY') else None)
@role_required('ADMIN','COMMITTEE','SECURITY')
def worker_add(request): return _save_form(request, DomesticWorkerForm, 'Add Domestic Staff', 'operations:workers')
@role_required('ADMIN','COMMITTEE','SECURITY')
def worker_checkin(request, pk):
    worker = get_object_or_404(DomesticWorker, pk=pk, is_active=True)
    StaffAttendance.objects.create(worker=worker, recorded_by=request.user)
    messages.success(request, f'{worker.name} checked in.')
    return redirect('operations:workers')
@role_required('ADMIN','COMMITTEE','SECURITY')
def worker_checkout(request, pk):
    attendance = StaffAttendance.objects.filter(worker_id=pk, check_out__isnull=True).first()
    if attendance:
        attendance.check_out = timezone.now(); attendance.save(update_fields=['check_out'])
        messages.success(request, 'Check-out recorded.')
    return redirect('operations:workers')

@login_required
def certificate_list(request):
    qs = CertificateRequest.objects.select_related('flat','requested_by')
    if not request.user.is_admin_or_committee(): qs = qs.filter(requested_by=request.user)
    return _simple_list(request, qs, 'NOC & Certificates', 'certificate', 'operations:certificate_add')
@login_required
def certificate_add(request): return _save_form(request, CertificateRequestForm, 'Request Certificate / NOC', 'operations:certificates', 'requested_by')

@login_required
def meeting_list(request): return _simple_list(request, SocietyMeeting.objects.all(), 'Meetings & AGM', 'meeting', 'operations:meeting_add' if request.user.is_admin_or_committee() else None)
@role_required('ADMIN','COMMITTEE')
def meeting_add(request): return _save_form(request, SocietyMeetingForm, 'Schedule Meeting / AGM', 'operations:meetings', 'created_by')

@login_required
def poll_list(request): return _simple_list(request, Poll.objects.prefetch_related('options','votes').all(), 'Polls & Voting', 'poll', 'operations:poll_add' if request.user.is_admin_or_committee() else None)
@role_required('ADMIN','COMMITTEE')
def poll_add(request):
    form = PollForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        poll = form.save(commit=False); poll.created_by = request.user; poll.save()
        for key in ['option_1','option_2','option_3','option_4']:
            label = form.cleaned_data.get(key)
            if label: PollOption.objects.create(poll=poll, label=label)
        messages.success(request, 'Poll created successfully.'); return redirect('operations:polls')
    return render(request, 'operations/form.html', {'form':form,'title':'Create Poll'})
@login_required
def poll_vote(request, option_id):
    option = get_object_or_404(PollOption.objects.select_related('poll'), pk=option_id)
    poll = option.poll
    if request.method == 'POST' and poll.is_active and (not poll.closes_at or poll.closes_at >= timezone.now()):
        PollVote.objects.update_or_create(poll=poll, user=request.user, defaults={'option':option})
        messages.success(request, 'Your vote has been recorded.')
    return redirect('operations:polls')

@role_required('ADMIN','COMMITTEE')
def asset_list(request): return _simple_list(request, SocietyAsset.objects.all(), 'Assets & Inventory', 'asset', 'operations:asset_add')
@role_required('ADMIN','COMMITTEE')
def asset_add(request): return _save_form(request, SocietyAssetForm, 'Add Society Asset', 'operations:assets')

@login_required
def emergency_list(request): return _simple_list(request, EmergencyContact.objects.filter(is_active=True), 'Emergency Directory', 'emergency', 'operations:emergency_add' if request.user.is_admin_or_committee() else None)
@role_required('ADMIN','COMMITTEE')
def emergency_add(request): return _save_form(request, EmergencyContactForm, 'Add Emergency Contact', 'operations:emergency')

@login_required
def lostfound_list(request): return _simple_list(request, LostFoundItem.objects.select_related('reported_by'), 'Lost & Found', 'lostfound', 'operations:lostfound_add')
@login_required
def lostfound_add(request): return _save_form(request, LostFoundForm, 'Report Lost / Found Item', 'operations:lostfound', 'reported_by')

@login_required
def event_list(request): return _simple_list(request, SocietyEvent.objects.all(), 'Society Events', 'event', 'operations:event_add' if request.user.is_admin_or_committee() else None)
@role_required('ADMIN','COMMITTEE')
def event_add(request): return _save_form(request, SocietyEventForm, 'Create Society Event', 'operations:events')
