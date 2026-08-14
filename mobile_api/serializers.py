from rest_framework import serializers
from notices.models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "content",
            "category",
            "posted_by",
            "posted_by_name",
            "posted_on",
            "pinned",
            "attachment",
        ]

        read_only_fields = [
            "id",
            "posted_by",
            "posted_by_name",
            "posted_on",
        ]

    def get_posted_by_name(self, obj):
        if obj.posted_by:
            return obj.posted_by.get_full_name() or obj.posted_by.username
        return None
from complaints.models import Complaint


class ComplaintSerializer(serializers.ModelSerializer):
    raised_by_name = serializers.SerializerMethodField()
    flat_name = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            "id",
            "raised_by",
            "raised_by_name",
            "flat",
            "flat_name",
            "category",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
            "created_on",
            "updated_on",
        ]

        read_only_fields = [
            "id",
            "raised_by",
            "raised_by_name",
            "flat_name",
            "created_on",
            "updated_on",
        ]

    def get_raised_by_name(self, obj):
        if obj.raised_by:
            return obj.raised_by.get_full_name() or obj.raised_by.username
        return None

    def get_flat_name(self, obj):
        return str(obj.flat) if obj.flat else None
from billing.models import Invoice, Payment


class InvoiceSerializer(serializers.ModelSerializer):
    flat_name = serializers.SerializerMethodField()
    charge_name = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "flat",
            "flat_name",
            "charge_template",
            "charge_name",
            "title",
            "amount",
            "due_date",
            "issue_date",
            "status",
            "notes",
        ]

    def get_flat_name(self, obj):
        return str(obj.flat) if obj.flat else None

    def get_charge_name(self, obj):
        return obj.charge_template.name if obj.charge_template else None


class PaymentSerializer(serializers.ModelSerializer):
    invoice_title = serializers.SerializerMethodField()
    flat_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "invoice_title",
            "flat_name",
            "amount",
            "method",
            "paid_on",
            "recorded_by",
            "recorded_by_name",
            "reference_number",
        ]

    def get_invoice_title(self, obj):
        return obj.invoice.title if obj.invoice else None

    def get_flat_name(self, obj):
        if obj.invoice and obj.invoice.flat:
            return str(obj.invoice.flat)
        return None

    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return obj.recorded_by.get_full_name() or obj.recorded_by.username
        return None
from visitors.models import Visitor


class VisitorSerializer(serializers.ModelSerializer):
    flat_name = serializers.SerializerMethodField()
    logged_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Visitor
        fields = [
            "id",
            "name",
            "phone_number",
            "purpose",
            "visiting_flat",
            "flat_name",
            "vehicle_number",
            "photo",
            "status",
            "logged_by",
            "logged_by_name",
            "check_in_time",
            "check_out_time",
            "created_on",
        ]

        read_only_fields = [
            "id",
            "logged_by",
            "logged_by_name",
            "check_in_time",
            "check_out_time",
            "created_on",
        ]

    def get_flat_name(self, obj):
        return str(obj.visiting_flat) if obj.visiting_flat else None

    def get_logged_by_name(self, obj):
        if obj.logged_by:
            return obj.logged_by.get_full_name() or obj.logged_by.username
        return None