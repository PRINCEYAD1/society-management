from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.decorators import role_required
from .models import Vehicle, Parcel, VendorAMC, Expense, MoveRequest
from .forms import VehicleForm, ParcelForm, VendorAMCForm, ExpenseForm, MoveRequestForm


def _save_form(request, form_class, title, success_url, set_user_field=None):
    form = form_class(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        if set_user_field:
            setattr(obj, set_user_field, request.user)
        obj.save()
        messages.success(request, f'{title} saved successfully.')
        return redirect(success_url)
    return render(request, 'operations/form.html', {'form': form, 'title': title})


@login_required
def vehicle_list(request):
    qs = Vehicle.objects.select_related('flat', 'flat__building')
    if not request.user.is_admin_or_committee():
        flat = getattr(getattr(request.user, 'resident_profile', None), 'flat', None)
        qs = qs.filter(flat=flat) if flat else qs.none()
    return render(request, 'operations/list.html', {'items': qs, 'title':'Parking & Vehicles', 'kind':'vehicle', 'add_url':'operations:vehicle_add'})

@role_required('ADMIN','COMMITTEE')
def vehicle_add(request): return _save_form(request, VehicleForm, 'Add Vehicle', 'operations:vehicles')

@login_required
def parcel_list(request):
    qs = Parcel.objects.select_related('flat').order_by('-received_at')
    if not request.user.is_admin_or_committee() and getattr(request.user, 'role', '') != 'SECURITY':
        flat = getattr(getattr(request.user, 'resident_profile', None), 'flat', None)
        qs = qs.filter(flat=flat) if flat else qs.none()
    return render(request, 'operations/list.html', {'items': qs, 'title':'Parcels & Deliveries', 'kind':'parcel', 'add_url':'operations:parcel_add'})

@role_required('ADMIN','COMMITTEE','SECURITY')
def parcel_add(request): return _save_form(request, ParcelForm, 'Log Parcel / Delivery', 'operations:parcels', 'received_by')

@role_required('ADMIN','COMMITTEE')
def vendor_list(request):
    return render(request, 'operations/list.html', {'items':VendorAMC.objects.all(), 'title':'Vendors & AMC', 'kind':'vendor', 'add_url':'operations:vendor_add'})

@role_required('ADMIN','COMMITTEE')
def vendor_add(request): return _save_form(request, VendorAMCForm, 'Add Vendor / AMC', 'operations:vendors')

@role_required('ADMIN','COMMITTEE')
def expense_list(request):
    return render(request, 'operations/list.html', {'items':Expense.objects.all(), 'title':'Society Expenses', 'kind':'expense', 'add_url':'operations:expense_add'})

@role_required('ADMIN','COMMITTEE')
def expense_add(request): return _save_form(request, ExpenseForm, 'Record Expense', 'operations:expenses', 'created_by')

@login_required
def move_list(request):
    qs = MoveRequest.objects.select_related('flat','requested_by').order_by('-created_at')
    if not request.user.is_admin_or_committee(): qs = qs.filter(requested_by=request.user)
    return render(request, 'operations/list.html', {'items':qs, 'title':'Move In / Move Out', 'kind':'move', 'add_url':'operations:move_add'})

@login_required
def move_add(request): return _save_form(request, MoveRequestForm, 'Request Move In / Move Out', 'operations:moves', 'requested_by')
