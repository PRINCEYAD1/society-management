from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.decorators import role_required
from .forms import NoticeForm
from .models import Notice


@login_required
def notice_list(request):
    notices = Notice.objects.all()
    return render(request, 'notices/notice_list.html', {'notices': notices})


@login_required
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    return render(request, 'notices/notice_detail.html', {'notice': notice})


@role_required('ADMIN', 'COMMITTEE')
def notice_add(request):
    form = NoticeForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        notice = form.save(commit=False)
        notice.posted_by = request.user
        notice.save()
        messages.success(request, 'Notice posted.')
        return redirect('notices:list')
    return render(request, 'core/form.html', {'form': form, 'title': 'Post Notice'})


@role_required('ADMIN', 'COMMITTEE')
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.delete()
    messages.success(request, 'Notice deleted.')
    return redirect('notices:list')
