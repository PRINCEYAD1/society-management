from rest_framework import serializers
from notices.models import Notice
from rest_framework import serializers
from amenities.models import Amenity, AmenityBooking
from complaints.models import Complaint
from operations.models import Expense, EmergencyContact
from visitors.models import Visitor
from billing.models import Invoice, Payment
from operations.models import SocietyAsset, VendorAMC
from operations.models import Parcel
from operations.models import Vehicle
from operations.models import Poll, PollOption, PollVote
from operations.models import CertificateRequest
from operations.models import SocietyEvent, SocietyMeeting
from operations.models import MoveRequest
from operations.models import DomesticWorker, StaffAttendance

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

        read_only_fields = [
            "id",
            "flat_name",
            "charge_name",
            "issue_date",
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

        read_only_fields = [
            "id",
            "invoice_title",
            "flat_name",
            "paid_on",
            "recorded_by",
            "recorded_by_name",
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
class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = [
            "id",
            "name",
            "description",
            "capacity",
            "booking_fee",
            "open_time",
            "close_time",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]


class AmenityBookingSerializer(serializers.ModelSerializer):
    amenity_name = serializers.SerializerMethodField()
    booked_by_name = serializers.SerializerMethodField()
    booking_fee = serializers.SerializerMethodField()

    class Meta:
        model = AmenityBooking
        fields = [
            "id",
            "amenity",
            "amenity_name",
            "booking_fee",
            "booked_by",
            "booked_by_name",
            "booking_date",
            "start_time",
            "end_time",
            "status",
            "notes",
            "created_on",
        ]

        read_only_fields = [
            "id",
            "amenity_name",
            "booking_fee",
            "booked_by",
            "booked_by_name",
            "status",
            "created_on",
        ]

    def get_amenity_name(self, obj):
        return obj.amenity.name if obj.amenity else None

    def get_booking_fee(self, obj):
        return obj.amenity.booking_fee if obj.amenity else None

    def get_booked_by_name(self, obj):
        if obj.booked_by:
            return obj.booked_by.get_full_name() or obj.booked_by.username
        return None

    def validate(self, data):
        amenity = data.get(
            "amenity",
            getattr(self.instance, "amenity", None)
        )

        booking_date = data.get(
            "booking_date",
            getattr(self.instance, "booking_date", None)
        )

        start_time = data.get(
            "start_time",
            getattr(self.instance, "start_time", None)
        )

        end_time = data.get(
            "end_time",
            getattr(self.instance, "end_time", None)
        )

        if amenity and not amenity.is_active:
            raise serializers.ValidationError(
                {
                    "amenity": "This amenity is currently inactive."
                }
            )

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                {
                    "end_time": "End time must be later than start time."
                }
            )

        if amenity and start_time and amenity.open_time:
            if start_time < amenity.open_time:
                raise serializers.ValidationError(
                    {
                        "start_time": (
                            f"Booking cannot start before "
                            f"{amenity.open_time}."
                        )
                    }
                )

        if amenity and end_time and amenity.close_time:
            if end_time > amenity.close_time:
                raise serializers.ValidationError(
                    {
                        "end_time": (
                            f"Booking cannot end after "
                            f"{amenity.close_time}."
                        )
                    }
                )

        # Prevent overlapping active bookings
        if amenity and booking_date and start_time and end_time:
            overlapping = AmenityBooking.objects.filter(
                amenity=amenity,
                booking_date=booking_date,
                status__in=["REQUESTED", "CONFIRMED"],
                start_time__lt=end_time,
                end_time__gt=start_time,
            )

            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError(
                    "This amenity is already booked/requested during the selected time."
                )

        return data
class ParcelSerializer(serializers.ModelSerializer):
    flat_name = serializers.SerializerMethodField()
    received_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Parcel
        fields = [
            "id",
            "flat",
            "flat_name",
            "recipient_name",
            "courier_name",
            "tracking_number",
            "photo",
            "status",
            "received_at",
            "collected_at",
            "received_by",
            "received_by_name",
        ]

        read_only_fields = [
            "id",
            "flat_name",
            "status",
            "received_at",
            "collected_at",
            "received_by",
            "received_by_name",
        ]

    def get_flat_name(self, obj):
        return str(obj.flat) if obj.flat else None

    def get_received_by_name(self, obj):
        if obj.received_by:
            return obj.received_by.get_full_name() or obj.received_by.username
        return None
class ParcelSerializer(serializers.ModelSerializer):
    flat_name = serializers.SerializerMethodField()
    received_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Parcel
        fields = [
            "id",
            "flat",
            "flat_name",
            "recipient_name",
            "courier_name",
            "tracking_number",
            "photo",
            "status",
            "received_at",
            "collected_at",
            "received_by",
            "received_by_name",
        ]

        read_only_fields = [
            "id",
            "flat_name",
            "status",
            "received_at",
            "collected_at",
            "received_by",
            "received_by_name",
        ]

    def get_flat_name(self, obj):
        return str(obj.flat) if obj.flat else None

    def get_received_by_name(self, obj):
        if obj.received_by:
            return obj.received_by.get_full_name() or obj.received_by.username
        return None
class VehicleSerializer(serializers.ModelSerializer):
    flat_name = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "flat",
            "flat_name",
            "owner_name",
            "vehicle_number",
            "vehicle_type",
            "parking_slot",
            "photo",
            "is_active",
        ]

        read_only_fields = [
            "id",
            "flat_name",
        ]

    def get_flat_name(self, obj):
        return str(obj.flat) if obj.flat else None
class MoveRequestSerializer(serializers.ModelSerializer):
    flat_name = serializers.SerializerMethodField()
    requested_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MoveRequest
        fields = [
            "id",
            "flat",
            "flat_name",
            "requested_by",
            "requested_by_name",
            "move_type",
            "requested_date",
            "status",
            "document",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "flat",
            "flat_name",
            "requested_by",
            "requested_by_name",
            "status",
            "created_at",
        ]

    def get_flat_name(self, obj):
        return str(obj.flat) if obj.flat else None

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return obj.requested_by.get_full_name() or obj.requested_by.username
        return None
class DomesticWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomesticWorker
        fields = [
            "id",
            "name",
            "service_type",
            "phone",
            "id_number",
            "photo",
            "id_document",
            "police_verified",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]


class StaffAttendanceSerializer(serializers.ModelSerializer):
    worker_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StaffAttendance
        fields = [
            "id",
            "worker",
            "worker_name",
            "check_in",
            "check_out",
            "gate_note",
            "recorded_by",
            "recorded_by_name",
        ]

        read_only_fields = [
            "id",
            "worker_name",
            "check_in",
            "check_out",
            "recorded_by",
            "recorded_by_name",
        ]

    def get_worker_name(self, obj):
        return obj.worker.name if obj.worker else None

    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return obj.recorded_by.get_full_name() or obj.recorded_by.username
        return None
class CertificateRequestSerializer(serializers.ModelSerializer):
    flat_name = serializers.SerializerMethodField()
    requested_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CertificateRequest
        fields = [
            "id",
            "requested_by",
            "requested_by_name",
            "flat",
            "flat_name",
            "request_type",
            "purpose",
            "supporting_document",
            "status",
            "requested_at",
        ]

        read_only_fields = [
            "id",
            "requested_by",
            "requested_by_name",
            "flat",
            "flat_name",
            "status",
            "requested_at",
        ]

    def get_flat_name(self, obj):
        return str(obj.flat) if obj.flat else None

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return obj.requested_by.get_full_name() or obj.requested_by.username
        return None
class SocietyEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocietyEvent
        fields = [
            "id",
            "title",
            "event_date",
            "venue",
            "description",
            "poster",
            "registration_required",
            "contribution_amount",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]


class SocietyMeetingSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SocietyMeeting
        fields = [
            "id",
            "title",
            "meeting_date",
            "venue",
            "agenda",
            "minutes",
            "attachment",
            "created_by",
            "created_by_name",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_by_name",
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
class SocietyAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocietyAsset
        fields = [
            "id",
            "name",
            "category",
            "asset_code",
            "location",
            "purchase_date",
            "warranty_until",
            "next_service_date",
            "document",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]


class VendorAMCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAMC
        fields = [
            "id",
            "service_name",
            "vendor_name",
            "contact_person",
            "phone",
            "amount",
            "start_date",
            "renewal_date",
            "document",
            "notes",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]
class ExpenseSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id",
            "title",
            "category",
            "amount",
            "expense_date",
            "vendor",
            "receipt",
            "notes",
            "created_by",
            "created_by_name",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_by_name",
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "name",
            "category",
            "phone",
            "secondary_phone",
            "notes",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]
class PollOptionSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model = PollOption
        fields = [
            "id",
            "poll",
            "label",
            "vote_count",
        ]

        read_only_fields = [
            "id",
            "poll",
            "vote_count",
        ]

    def get_vote_count(self, obj):
        return obj.pollvote_set.count()


class PollSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    user_has_voted = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = [
            "id",
            "question",
            "description",
            "closes_at",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "options",
            "total_votes",
            "user_has_voted",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_by_name",
            "created_at",
            "options",
            "total_votes",
            "user_has_voted",
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None

    def get_options(self, obj):
        options = PollOption.objects.filter(
            poll=obj
        ).order_by("id")

        return PollOptionSerializer(
            options,
            many=True
        ).data

    def get_total_votes(self, obj):
        return PollVote.objects.filter(
            poll=obj
        ).count()

    def get_user_has_voted(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return PollVote.objects.filter(
            poll=obj,
            user=request.user
        ).exists()


class PollVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollVote
        fields = [
            "id",
            "poll",
            "option",
            "user",
            "voted_at",
        ]

        read_only_fields = [
            "id",
            "poll",
            "user",
            "voted_at",
        ]