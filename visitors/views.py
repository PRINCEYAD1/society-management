from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from core.decorators import role_required
from .forms import VisitorForm
from .models import Visitor


@login_required
def visitor_list(request):
    user = request.user
    if user.is_admin_or_committee() or user.role == 'SECURITY':
        visitors = Visitor.objects.all()
    else:
        flat = getattr(getattr(user, 'resident_profile', None), 'flat', None)
        visitors = Visitor.objects.filter(visiting_flat=flat) if flat else Visitor.objects.none()
    return render(request, 'visitors/visitor_list.html', {'visitors': visitors})


@role_required('ADMIN', 'COMMITTEE', 'SECURITY')
def visitor_add(request):
    form = VisitorForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        visitor = form.save(commit=False)
        visitor.logged_by = request.user
        visitor.save()
        messages.success(request, 'Visitor entry logged. Awaiting resident approval.')
        return redirect('visitors:list')
    return render(request, 'core/form.html', {'form': form, 'title': 'Log New Visitor'})


@login_required
def visitor_approve(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    visitor.status = Visitor.Status.APPROVED
    visitor.save()
    messages.success(request, f'{visitor.name} approved.')
    return redirect('visitors:list')


@login_required
def visitor_deny(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    visitor.status = Visitor.Status.DENIED
    visitor.save()
    messages.warning(request, f'{visitor.name} denied entry.')
    return redirect('visitors:list')


@role_required('ADMIN', 'COMMITTEE', 'SECURITY')
def visitor_checkin(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    visitor.status = Visitor.Status.CHECKED_IN
    visitor.check_in_time = timezone.now()
    visitor.save()
    messages.success(request, f'{visitor.name} checked in.')
    return redirect('visitors:list')


@role_required('ADMIN', 'COMMITTEE', 'SECURITY')
def visitor_checkout(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    visitor.status = Visitor.Status.CHECKED_OUT
    visitor.check_out_time = timezone.now()
    visitor.save()
    messages.success(request, f'{visitor.name} checked out.')
    return redirect('visitors:list')
