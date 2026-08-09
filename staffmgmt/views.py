from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from core.decorators import role_required
from .forms import StaffMemberForm, AttendanceForm
from .models import StaffMember


@role_required('ADMIN', 'COMMITTEE')
def staff_list(request):
    staff = StaffMember.objects.all()
    return render(request, 'staffmgmt/staff_list.html', {'staff': staff})


@role_required('ADMIN', 'COMMITTEE')
def staff_add(request):
    form = StaffMemberForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Staff member added.')
        return redirect('staffmgmt:list')
    return render(request, 'core/form.html', {'form': form, 'title': 'Add Staff Member'})


@role_required('ADMIN', 'COMMITTEE')
def staff_detail(request, pk):
    staff = get_object_or_404(StaffMember, pk=pk)
    records = staff.attendance_records.all()[:30]
    return render(request, 'staffmgmt/staff_detail.html', {'staff': staff, 'records': records})


@role_required('ADMIN', 'COMMITTEE')
def mark_attendance(request, pk):
    staff = get_object_or_404(StaffMember, pk=pk)
    form = AttendanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        attendance = form.save(commit=False)
        attendance.staff = staff
        attendance.save()
        messages.success(request, 'Attendance marked.')
        return redirect('staffmgmt:detail', pk=pk)
    return render(request, 'core/form.html', {'form': form, 'title': f'Mark Attendance - {staff.name}'})
