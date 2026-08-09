from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from core.decorators import role_required
from core.models import Flat
from .forms import InvoiceForm, PaymentForm, MaintenanceChargeTemplateForm
from .models import Invoice, MaintenanceChargeTemplate


@login_required
def invoice_list(request):
    user = request.user
    if user.is_admin_or_committee():
        invoices = Invoice.objects.select_related('flat', 'flat__building')
    else:
        flat = getattr(getattr(user, 'resident_profile', None), 'flat', None)
        invoices = Invoice.objects.filter(flat=flat) if flat else Invoice.objects.none()
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    user = request.user
    if not user.is_admin_or_committee():
        flat = getattr(getattr(user, 'resident_profile', None), 'flat', None)
        if invoice.flat_id != getattr(flat, 'id', None):
            messages.error(request, "You don't have access to that invoice.")
            return redirect('billing:invoice_list')
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})


@role_required('ADMIN', 'COMMITTEE')
def invoice_create(request):
    form = InvoiceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Invoice created.')
        return redirect('billing:invoice_list')
    return render(request, 'core/form.html', {'form': form, 'title': 'Create Invoice'})


@role_required('ADMIN', 'COMMITTEE')
def record_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = PaymentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        payment = form.save(commit=False)
        payment.invoice = invoice
        payment.recorded_by = request.user
        payment.save()
        messages.success(request, 'Payment recorded.')
        return redirect('billing:invoice_detail', pk=pk)
    return render(request, 'core/form.html', {'form': form, 'title': f'Record Payment for {invoice}'})


@role_required('ADMIN', 'COMMITTEE')
def template_list(request):
    templates = MaintenanceChargeTemplate.objects.all()
    return render(request, 'billing/template_list.html', {'templates': templates})


@role_required('ADMIN', 'COMMITTEE')
def template_add(request):
    form = MaintenanceChargeTemplateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Charge template created.')
        return redirect('billing:template_list')
    return render(request, 'core/form.html', {'form': form, 'title': 'Add Maintenance Charge Template'})


@role_required('ADMIN', 'COMMITTEE')
def generate_monthly(request):
    """Bulk-generate an invoice for every flat using an active charge template."""
    if request.method == 'POST':
        template_id = request.POST.get('template')
        template = get_object_or_404(MaintenanceChargeTemplate, pk=template_id)
        due_date = timezone.localdate() + timedelta(days=10)
        created = 0
        for flat in Flat.objects.all():
            Invoice.objects.create(
                flat=flat,
                charge_template=template,
                title=f"{template.name} - {timezone.localdate().strftime('%B %Y')}",
                amount=template.amount,
                due_date=due_date,
            )
            created += 1
        messages.success(request, f'Generated {created} invoices.')
        return redirect('billing:invoice_list')
    templates = MaintenanceChargeTemplate.objects.filter(is_active=True)
    return render(request, 'billing/generate_monthly.html', {'templates': templates})
