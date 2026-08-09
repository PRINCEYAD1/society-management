from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.decorators import role_required
from .forms import ComplaintForm, ComplaintCommentForm, ComplaintStatusForm
from .models import Complaint


@login_required
def complaint_list(request):
    user = request.user
    if user.is_admin_or_committee() or user.role == 'STAFF':
        complaints = Complaint.objects.all()
    else:
        complaints = Complaint.objects.filter(raised_by=user)
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints})


@login_required
def complaint_add(request):
    form = ComplaintForm(request.POST or None)
    if request.user.is_admin_or_committee():
        pass
    else:
        flat = getattr(getattr(request.user, 'resident_profile', None), 'flat', None)
        form.fields['flat'].initial = flat

    if request.method == 'POST' and form.is_valid():
        complaint = form.save(commit=False)
        complaint.raised_by = request.user
        complaint.save()
        messages.success(request, 'Complaint submitted.')
        return redirect('complaints:list')
    return render(request, 'core/form.html', {'form': form, 'title': 'Raise a Complaint'})


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    user = request.user
    if not (user.is_admin_or_committee() or user.role == 'STAFF') and complaint.raised_by_id != user.id:
        messages.error(request, "You don't have access to that complaint.")
        return redirect('complaints:list')

    comment_form = ComplaintCommentForm(request.POST or None)
    if request.method == 'POST' and comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.complaint = complaint
        comment.author = user
        comment.save()
        return redirect('complaints:detail', pk=pk)

    status_form = ComplaintStatusForm(instance=complaint) if user.is_admin_or_committee() else None
    return render(request, 'complaints/complaint_detail.html', {
        'complaint': complaint,
        'comment_form': comment_form,
        'status_form': status_form,
    })


@role_required('ADMIN', 'COMMITTEE')
def update_status(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        form = ComplaintStatusForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, 'Complaint status updated.')
    return redirect('complaints:detail', pk=pk)
