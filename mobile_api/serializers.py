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