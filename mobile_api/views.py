from django.contrib.auth import authenticate
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from operations.models import Parcel

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Flat, ResidentProfile
from billing.models import Invoice, Payment
from complaints.models import Complaint
from visitors.models import Visitor
from notices.models import Notice

from amenities.models import Amenity, AmenityBooking

from operations.models import (
    Vehicle,
    Parcel,
    VendorAMC,
    Expense,
    MoveRequest,
    DomesticWorker,
    StaffAttendance,
    CertificateRequest,
    SocietyMeeting,
    Poll,
    SocietyAsset,
    LostFoundItem,
    SocietyEvent,
)

from .serializers import (
    NoticeSerializer,
    ComplaintSerializer,
    VisitorSerializer,
    InvoiceSerializer,
    PaymentSerializer,
    SocietyAssetSerializer,
    ExpenseSerializer,
    EmergencyContactSerializer,
    VendorAMCSerializer,
    AmenitySerializer,
    CertificateRequestSerializer,
    AmenityBookingSerializer,
    ParcelSerializer,
    DomesticWorkerSerializer,
    StaffAttendanceSerializer,
    VehicleSerializer,
    MoveRequestSerializer,
    SocietyEventSerializer,
    SocietyMeetingSerializer,
)
# ============================================================
# AUTHENTICATION
# ============================================================

class MobileLoginView(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {
                    "success": False,
                    "message": "Username and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            return Response(
                {
                    "success": False,
                    "message": "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {
                    "success": False,
                    "message": "This account is inactive."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": getattr(user, "role", ""),
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                }
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# PROFILE
# ============================================================

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        flat = None
        resident_profile = getattr(
            user,
            "resident_profile",
            None
        )

        if resident_profile and resident_profile.flat:
            flat = str(resident_profile.flat)

        return Response(
            {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "full_name": user.get_full_name(),
                    "email": user.email,
                    "role": getattr(user, "role", ""),
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "flat": flat,
                }
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if (
            getattr(user, "role", "") != "ADMIN"
            and not user.is_superuser
        ):
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        today = timezone.localdate()

        total_flats = Flat.objects.count()
        total_residents = ResidentProfile.objects.count()

        pending_invoices = Invoice.objects.exclude(
            status=Invoice.Status.PAID
        )

        outstanding_amount = pending_invoices.aggregate(
            total=Sum("amount")
        )["total"] or 0

        collection_this_month = Payment.objects.filter(
            paid_on__year=today.year,
            paid_on__month=today.month
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        monthly_expenses = Expense.objects.filter(
            expense_date__year=today.year,
            expense_date__month=today.month
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        open_complaints = Complaint.objects.exclude(
            status__in=["RESOLVED", "CLOSED"]
        ).count()

        visitors_today = Visitor.objects.filter(
            created_on__date=today
        ).count()

        parcels_waiting = Parcel.objects.exclude(
            status=Parcel.Status.COLLECTED
        ).count()

        active_vehicles = Vehicle.objects.filter(
            is_active=True
        ).count()

        active_domestic_workers = DomesticWorker.objects.filter(
            is_active=True
        ).count()

        pending_certificate_requests = CertificateRequest.objects.filter(
            status="PENDING"
        ).count()

        pending_move_requests = MoveRequest.objects.filter(
            status=MoveRequest.Status.REQUESTED
        ).count()

        active_amcs = VendorAMC.objects.filter(
            is_active=True
        ).count()

        active_assets = SocietyAsset.objects.filter(
            is_active=True
        ).count()

        active_polls = Poll.objects.filter(
            is_active=True
        ).count()

        upcoming_events = SocietyEvent.objects.filter(
            is_active=True,
            event_date__gte=timezone.now()
        ).count()

        open_lost_found = LostFoundItem.objects.filter(
            status="OPEN"
        ).count()

        upcoming_meetings = SocietyMeeting.objects.filter(
            meeting_date__gte=timezone.now()
        ).count()

        pending_amenity_bookings = AmenityBooking.objects.filter(
            status="REQUESTED"
        ).count()

        return Response(
            {
                "success": True,
                "role": "ADMIN",
                "dashboard": {
                    "total_flats": total_flats,
                    "total_residents": total_residents,
                    "pending_invoices": pending_invoices.count(),
                    "outstanding_amount": float(outstanding_amount),
                    "collection_this_month": float(collection_this_month),
                    "monthly_expenses": float(monthly_expenses),
                    "open_complaints": open_complaints,
                    "visitors_today": visitors_today,
                    "parcels_waiting": parcels_waiting,
                    "active_vehicles": active_vehicles,
                    "active_domestic_workers": active_domestic_workers,
                    "pending_certificate_requests":
                        pending_certificate_requests,
                    "pending_move_requests": pending_move_requests,
                    "active_amcs": active_amcs,
                    "active_assets": active_assets,
                    "active_polls": active_polls,
                    "upcoming_events": upcoming_events,
                    "open_lost_found": open_lost_found,
                    "upcoming_meetings": upcoming_meetings,
                    "pending_amenity_bookings":
                        pending_amenity_bookings,
                }
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# SECURITY DASHBOARD
# ============================================================

class SecurityDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if getattr(user, "role", "") != "SECURITY":
            return Response(
                {
                    "success": False,
                    "message": "Security access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        today = timezone.localdate()

        visitors_today = Visitor.objects.filter(
            created_on__date=today
        ).count()

        pending_visitors = Visitor.objects.filter(
            status=Visitor.Status.PENDING_APPROVAL
        ).count()

        checked_in_visitors = Visitor.objects.filter(
            check_in_time__date=today,
            check_out_time__isnull=True
        ).count()

        parcels_waiting = Parcel.objects.exclude(
            status=Parcel.Status.COLLECTED
        ).count()

        active_domestic_workers = DomesticWorker.objects.filter(
            is_active=True
        ).count()

        staff_inside = StaffAttendance.objects.filter(
            check_out__isnull=True
        ).count()

        active_vehicles = Vehicle.objects.filter(
            is_active=True
        ).count()

        recent_visitors = Visitor.objects.order_by(
            "-created_on"
        )[:5]

        recent_parcels = Parcel.objects.select_related(
            "flat"
        ).order_by(
            "-received_at"
        )[:5]

        return Response(
            {
                "success": True,
                "role": "SECURITY",
                "dashboard": {
                    "visitors_today": visitors_today,
                    "pending_visitors": pending_visitors,
                    "checked_in_visitors": checked_in_visitors,
                    "parcels_waiting": parcels_waiting,
                    "active_domestic_workers":
                        active_domestic_workers,
                    "staff_inside": staff_inside,
                    "active_vehicles": active_vehicles,
                },
                "recent_visitors": [
                    {
                        "id": visitor.id,
                        "name": visitor.name,
                        "phone_number": visitor.phone_number,
                        "purpose": visitor.purpose,
                        "flat": str(visitor.visiting_flat),
                        "status": visitor.status,
                    }
                    for visitor in recent_visitors
                ],
                "recent_parcels": [
                    {
                        "id": parcel.id,
                        "recipient_name": parcel.recipient_name,
                        "flat": str(parcel.flat),
                        "courier_name": parcel.courier_name,
                        "status": parcel.status,
                    }
                    for parcel in recent_parcels
                ]
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# RESIDENT DASHBOARD
# ============================================================

class ResidentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if getattr(user, "role", "") != "RESIDENT":
            return Response(
                {
                    "success": False,
                    "message": "Resident access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        resident_profile = getattr(
            user,
            "resident_profile",
            None
        )

        flat = getattr(
            resident_profile,
            "flat",
            None
        )

        if not flat:
            return Response(
                {
                    "success": False,
                    "message": "No flat is linked with this resident."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        today = timezone.localdate()

        pending_invoices = Invoice.objects.filter(
            flat=flat
        ).exclude(
            status=Invoice.Status.PAID
        )

        outstanding_amount = pending_invoices.aggregate(
            total=Sum("amount")
        )["total"] or 0

        my_complaints = Complaint.objects.filter(
            raised_by=user
        )

        open_complaints = my_complaints.exclude(
            status__in=["RESOLVED", "CLOSED"]
        ).count()

        my_parcels = Parcel.objects.filter(
            flat=flat
        ).exclude(
            status=Parcel.Status.COLLECTED
        )

        upcoming_bookings = AmenityBooking.objects.filter(
            booked_by=user,
            booking_date__gte=today
        ).count()

        my_vehicles = Vehicle.objects.filter(
            flat=flat,
            is_active=True
        ).count()

        pending_certificates = CertificateRequest.objects.filter(
            requested_by=user,
            status="PENDING"
        ).count()

        pending_move_requests = MoveRequest.objects.filter(
            requested_by=user,
            status=MoveRequest.Status.REQUESTED
        ).count()

        recent_notices = Notice.objects.order_by(
            "-posted_on"
        )[:5]

        upcoming_events = SocietyEvent.objects.filter(
            is_active=True,
            event_date__gte=timezone.now()
        ).order_by(
            "event_date"
        )[:5]

        return Response(
            {
                "success": True,
                "role": "RESIDENT",
                "resident": {
                    "username": user.username,
                    "name": user.get_full_name(),
                    "flat": str(flat),
                },
                "dashboard": {
                    "pending_invoices": pending_invoices.count(),
                    "outstanding_amount":
                        float(outstanding_amount),
                    "open_complaints": open_complaints,
                    "parcels_waiting": my_parcels.count(),
                    "upcoming_amenity_bookings":
                        upcoming_bookings,
                    "active_vehicles": my_vehicles,
                    "pending_certificates":
                        pending_certificates,
                    "pending_move_requests":
                        pending_move_requests,
                },
                "recent_notices": [
                    {
                        "id": notice.id,
                        "title": notice.title,
                        "category": notice.category,
                        "posted_on": notice.posted_on,
                        "pinned": notice.pinned,
                    }
                    for notice in recent_notices
                ],
                "upcoming_events": [
                    {
                        "id": event.id,
                        "title": event.title,
                        "event_date": event.event_date,
                        "venue": event.venue,
                    }
                    for event in upcoming_events
                ]
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# NOTICES
# ============================================================

class NoticeListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notices = Notice.objects.select_related(
            "posted_by"
        ).order_by(
            "-pinned",
            "-posted_on"
        )

        serializer = NoticeSerializer(
            notices,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": notices.count(),
                "notices": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user

        if (
            getattr(user, "role", "") != "ADMIN"
            and not user.is_superuser
        ):
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = NoticeSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(posted_by=user)

            return Response(
                {
                    "success": True,
                    "message": "Notice created successfully.",
                    "notice": serializer.data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class NoticeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(
            Notice,
            pk=pk
        )

    def get(self, request, pk):
        notice = self.get_object(pk)

        serializer = NoticeSerializer(
            notice,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "notice": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        user = request.user

        if (
            getattr(user, "role", "") != "ADMIN"
            and not user.is_superuser
        ):
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        notice = self.get_object(pk)

        serializer = NoticeSerializer(
            notice,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Notice updated successfully.",
                    "notice": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        user = request.user

        if (
            getattr(user, "role", "") != "ADMIN"
            and not user.is_superuser
        ):
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        notice = self.get_object(pk)
        notice.delete()

        return Response(
            {
                "success": True,
                "message": "Notice deleted successfully."
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# COMPLAINTS
# ============================================================

class ComplaintListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if (
            getattr(user, "role", "") == "ADMIN"
            or user.is_superuser
        ):
            complaints = Complaint.objects.select_related(
                "raised_by",
                "flat",
                "assigned_to"
            ).order_by(
                "-created_on"
            )
        else:
            complaints = Complaint.objects.filter(
                raised_by=user
            ).select_related(
                "raised_by",
                "flat",
                "assigned_to"
            ).order_by(
                "-created_on"
            )

        serializer = ComplaintSerializer(
            complaints,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": complaints.count(),
                "complaints": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user

        if getattr(user, "role", "") != "RESIDENT":
            return Response(
                {
                    "success": False,
                    "message": "Only residents can raise complaints."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        resident_profile = getattr(
            user,
            "resident_profile",
            None
        )

        flat = getattr(
            resident_profile,
            "flat",
            None
        )

        if not flat:
            return Response(
                {
                    "success": False,
                    "message": "No flat is linked with this resident."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ComplaintSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(
                raised_by=user,
                flat=flat
            )

            return Response(
                {
                    "success": True,
                    "message": "Complaint raised successfully.",
                    "complaint": serializer.data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ComplaintDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user

        complaint = get_object_or_404(
            Complaint,
            pk=pk
        )

        if (
            getattr(user, "role", "") != "ADMIN"
            and not user.is_superuser
            and complaint.raised_by != user
        ):
            return Response(
                {
                    "success": False,
                    "message":
                        "You do not have permission to view this complaint."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ComplaintSerializer(
            complaint,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "complaint": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        user = request.user

        if (
            getattr(user, "role", "") != "ADMIN"
            and not user.is_superuser
        ):
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        complaint = get_object_or_404(
            Complaint,
            pk=pk
        )

        serializer = ComplaintSerializer(
            complaint,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Complaint updated successfully.",
                    "complaint": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )
class VisitorListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role in ["ADMIN", "SECURITY"] or user.is_superuser:
            visitors = Visitor.objects.select_related(
                "visiting_flat",
                "logged_by"
            ).order_by("-created_on")

        elif role == "RESIDENT":
            profile = getattr(user, "resident_profile", None)
            flat = getattr(profile, "flat", None)

            if not flat:
                return Response(
                    {
                        "success": False,
                        "message": "No flat is linked with this resident."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            visitors = Visitor.objects.filter(
                visiting_flat=flat
            ).select_related(
                "visiting_flat",
                "logged_by"
            ).order_by("-created_on")

        else:
            return Response(
                {
                    "success": False,
                    "message": "Access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = VisitorSerializer(
            visitors,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": visitors.count(),
                "visitors": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "SECURITY", "RESIDENT"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()

        if role == "RESIDENT":
            profile = getattr(user, "resident_profile", None)
            flat = getattr(profile, "flat", None)

            if not flat:
                return Response(
                    {
                        "success": False,
                        "message": "No flat is linked with this resident."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            data["visiting_flat"] = flat.id

        serializer = VisitorSerializer(
            data=data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(logged_by=user)

            return Response(
                {
                    "success": True,
                    "message": "Visitor created successfully.",
                    "visitor": serializer.data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class VisitorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "SECURITY"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Security or Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        visitor = get_object_or_404(
            Visitor,
            pk=pk
        )

        new_status = request.data.get("status")

        if new_status:
            visitor.status = new_status

            if new_status == "CHECKED_IN":
                visitor.check_in_time = timezone.now()

            elif new_status == "CHECKED_OUT":
                visitor.check_out_time = timezone.now()

            visitor.save()

        serializer = VisitorSerializer(
            visitor,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "message": "Visitor updated successfully.",
                "visitor": serializer.data,
            },
            status=status.HTTP_200_OK
        )
class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role == "ADMIN" or user.is_superuser:
            invoices = Invoice.objects.select_related(
                "flat",
                "charge_template"
            ).order_by("-issue_date")

        elif role == "RESIDENT":
            profile = getattr(user, "resident_profile", None)
            flat = getattr(profile, "flat", None)

            if not flat:
                return Response(
                    {
                        "success": False,
                        "message": "No flat is linked with this resident."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            invoices = Invoice.objects.filter(
                flat=flat
            ).select_related(
                "flat",
                "charge_template"
            ).order_by("-issue_date")

        else:
            return Response(
                {
                    "success": False,
                    "message": "Billing access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = InvoiceSerializer(
            invoices,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": invoices.count(),
                "invoices": serializer.data,
            },
            status=status.HTTP_200_OK
        )
    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        # Only Admin can create invoices
        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = InvoiceSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            invoice = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Invoice created successfully.",
                    "invoice": InvoiceSerializer(
                        invoice,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

# ============================================================
# BILLING
# ============================================================

class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        # Admin can see all invoices
        if role == "ADMIN" or user.is_superuser:
            invoices = Invoice.objects.select_related(
                "flat",
                "charge_template"
            ).order_by("-issue_date")

        # Resident can see only invoices for their own flat
        elif role == "RESIDENT":
            profile = getattr(user, "resident_profile", None)
            flat = getattr(profile, "flat", None)

            if not flat:
                return Response(
                    {
                        "success": False,
                        "message": "No flat is linked with this resident."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            invoices = Invoice.objects.filter(
                flat=flat
            ).select_related(
                "flat",
                "charge_template"
            ).order_by("-issue_date")

        else:
            return Response(
                {
                    "success": False,
                    "message": "Billing access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = InvoiceSerializer(
            invoices,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": invoices.count(),
                "invoices": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        # Only Admin can create invoices
        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = InvoiceSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            invoice = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Invoice created successfully.",
                    "invoice": InvoiceSerializer(
                        invoice,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class InvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        invoice = get_object_or_404(
            Invoice.objects.select_related(
                "flat",
                "charge_template"
            ),
            pk=pk
        )

        # Resident can see only their own flat invoice
        if role == "RESIDENT":
            profile = getattr(user, "resident_profile", None)
            flat = getattr(profile, "flat", None)

            if not flat or invoice.flat != flat:
                return Response(
                    {
                        "success": False,
                        "message": "You do not have permission to view this invoice."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        # Security and other roles cannot access billing
        elif role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Billing access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = InvoiceSerializer(
            invoice,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "invoice": serializer.data,
                "payment_summary": {
                    "invoice_amount": float(invoice.amount),
                    "amount_paid": float(invoice.amount_paid()),
                    "balance": float(invoice.balance()),
                }
            },
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        # Only Admin can modify invoices
        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        invoice = get_object_or_404(
            Invoice,
            pk=pk
        )

        serializer = InvoiceSerializer(
            invoice,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            invoice = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Invoice updated successfully.",
                    "invoice": InvoiceSerializer(
                        invoice,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        # Admin can see all payments
        if role == "ADMIN" or user.is_superuser:
            payments = Payment.objects.select_related(
                "invoice",
                "invoice__flat",
                "recorded_by"
            ).order_by("-paid_on", "-id")

        # Resident sees only payments for their flat
        elif role == "RESIDENT":
            profile = getattr(user, "resident_profile", None)
            flat = getattr(profile, "flat", None)

            if not flat:
                return Response(
                    {
                        "success": False,
                        "message": "No flat is linked with this resident."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            payments = Payment.objects.filter(
                invoice__flat=flat
            ).select_related(
                "invoice",
                "invoice__flat",
                "recorded_by"
            ).order_by("-paid_on", "-id")

        else:
            return Response(
                {
                    "success": False,
                    "message": "Billing access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PaymentSerializer(
            payments,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": payments.count(),
                "payments": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        # Only Admin can record payments
        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PaymentSerializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        invoice = serializer.validated_data["invoice"]
        payment_amount = serializer.validated_data["amount"]

        # Payment must be greater than zero
        if payment_amount <= 0:
            return Response(
                {
                    "success": False,
                    "message": "Payment amount must be greater than zero."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        current_balance = invoice.balance()

        # Prevent payment on fully paid invoice
        if current_balance <= 0:
            return Response(
                {
                    "success": False,
                    "message": "This invoice is already fully paid."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent overpayment
        if payment_amount > current_balance:
            return Response(
                {
                    "success": False,
                    "message": (
                        f"Payment amount cannot exceed the outstanding "
                        f"balance of ₹{current_balance}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = serializer.save(
            recorded_by=user
        )

        # Payment.save() automatically updates invoice status
        invoice.refresh_from_db()

        return Response(
            {
                "success": True,
                "message": "Payment recorded successfully.",
                "payment": PaymentSerializer(
                    payment,
                    context={"request": request}
                ).data,
                "invoice_summary": {
                    "invoice_id": invoice.id,
                    "invoice_amount": float(invoice.amount),
                    "amount_paid": float(invoice.amount_paid()),
                    "balance": float(invoice.balance()),
                    "status": invoice.status,
                }
            },
            status=status.HTTP_201_CREATED
        )
# ============================================================
# AMENITIES
# ============================================================

class AmenityListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "RESIDENT"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Amenity access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        amenities = Amenity.objects.filter(
            is_active=True
        ).order_by("name")

        serializer = AmenitySerializer(
            amenities,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": amenities.count(),
                "amenities": serializer.data,
            },
            status=status.HTTP_200_OK
        )


class AmenityBookingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role == "ADMIN" or user.is_superuser:
            bookings = AmenityBooking.objects.select_related(
                "amenity",
                "booked_by"
            ).order_by("-booking_date", "-start_time")

        elif role == "RESIDENT":
            bookings = AmenityBooking.objects.filter(
                booked_by=user
            ).select_related(
                "amenity",
                "booked_by"
            ).order_by("-booking_date", "-start_time")

        else:
            return Response(
                {
                    "success": False,
                    "message": "Amenity booking access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AmenityBookingSerializer(
            bookings,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": bookings.count(),
                "bookings": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "RESIDENT":
            return Response(
                {
                    "success": False,
                    "message": "Only residents can request amenity bookings."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AmenityBookingSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            booking = serializer.save(
                booked_by=user,
                status="REQUESTED"
            )

            return Response(
                {
                    "success": True,
                    "message": "Amenity booking requested successfully.",
                    "booking": AmenityBookingSerializer(
                        booking,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class AmenityBookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        booking = get_object_or_404(
            AmenityBooking.objects.select_related(
                "amenity",
                "booked_by"
            ),
            pk=pk
        )

        if (
            role != "ADMIN"
            and not user.is_superuser
            and booking.booked_by != user
        ):
            return Response(
                {
                    "success": False,
                    "message": "You do not have permission to view this booking."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AmenityBookingSerializer(
            booking,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "booking": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        booking = get_object_or_404(
            AmenityBooking,
            pk=pk
        )

        new_status = request.data.get("status")

        allowed_statuses = [
            "REQUESTED",
            "CONFIRMED",
            "CANCELLED",
            "COMPLETED",
        ]

        if new_status not in allowed_statuses:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Invalid status. Use REQUESTED, CONFIRMED, "
                        "CANCELLED or COMPLETED."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = new_status
        booking.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "message": "Amenity booking status updated successfully.",
                "booking": AmenityBookingSerializer(
                    booking,
                    context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK
        )
# ============================================================
# PARCELS
# ============================================================

class ParcelListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role in ["ADMIN", "SECURITY"] or user.is_superuser:
            parcels = Parcel.objects.select_related(
                "flat",
                "received_by"
            ).order_by("-received_at")

        elif role == "RESIDENT":
            profile = getattr(user, "resident_profile", None)
            flat = getattr(profile, "flat", None)

            if not flat:
                return Response(
                    {
                        "success": False,
                        "message": "No flat is linked with this resident."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            parcels = Parcel.objects.filter(
                flat=flat
            ).select_related(
                "flat",
                "received_by"
            ).order_by("-received_at")

        else:
            return Response(
                {
                    "success": False,
                    "message": "Parcel access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ParcelSerializer(
            parcels,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": parcels.count(),
                "parcels": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "SECURITY"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Security or Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ParcelSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            parcel = serializer.save(
                status="RECEIVED",
                received_by=user
            )

            return Response(
                {
                    "success": True,
                    "message": "Parcel received successfully.",
                    "parcel": ParcelSerializer(
                        parcel,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ParcelDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "SECURITY"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Security or Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        parcel = get_object_or_404(
            Parcel,
            pk=pk
        )

        new_status = request.data.get("status")

        allowed_statuses = [
            "RECEIVED",
            "NOTIFIED",
            "COLLECTED",
        ]

        if new_status not in allowed_statuses:
            return Response(
                {
                    "success": False,
                    "message": "Invalid parcel status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        parcel.status = new_status

        if new_status == "COLLECTED":
            parcel.collected_at = timezone.now()

        parcel.save()

        return Response(
            {
                "success": True,
                "message": "Parcel status updated successfully.",
                "parcel": ParcelSerializer(
                    parcel,
                    context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK
        )
# ============================================================
# VEHICLES
# ============================================================

class VehicleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role in ["ADMIN", "SECURITY"] or user.is_superuser:
            vehicles = Vehicle.objects.select_related(
                "flat"
            ).order_by("vehicle_number")

        elif role == "RESIDENT":
            profile = getattr(user, "resident_profile", None)
            flat = getattr(profile, "flat", None)

            if not flat:
                return Response(
                    {
                        "success": False,
                        "message": "No flat is linked with this resident."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            vehicles = Vehicle.objects.filter(
                flat=flat
            ).select_related(
                "flat"
            ).order_by("vehicle_number")

        else:
            return Response(
                {
                    "success": False,
                    "message": "Vehicle access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = VehicleSerializer(
            vehicles,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": vehicles.count(),
                "vehicles": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "RESIDENT"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin or Resident access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()

        if role == "RESIDENT":
            profile = getattr(user, "resident_profile", None)
            flat = getattr(profile, "flat", None)

            if not flat:
                return Response(
                    {
                        "success": False,
                        "message": "No flat is linked with this resident."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            data["flat"] = flat.id

        serializer = VehicleSerializer(
            data=data,
            context={"request": request}
        )

        if serializer.is_valid():
            vehicle = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Vehicle registered successfully.",
                    "vehicle": VehicleSerializer(
                        vehicle,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class VehicleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        vehicle = get_object_or_404(
            Vehicle,
            pk=pk
        )

        serializer = VehicleSerializer(
            vehicle,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Vehicle updated successfully.",
                    "vehicle": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )
# ============================================================
# MOVE REQUESTS
# ============================================================

class MoveRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role == "ADMIN" or user.is_superuser:
            requests_qs = MoveRequest.objects.select_related(
                "flat",
                "requested_by"
            ).order_by("-created_at")

        elif role == "RESIDENT":
            requests_qs = MoveRequest.objects.filter(
                requested_by=user
            ).select_related(
                "flat",
                "requested_by"
            ).order_by("-created_at")

        else:
            return Response(
                {
                    "success": False,
                    "message": "Move request access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MoveRequestSerializer(
            requests_qs,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": requests_qs.count(),
                "move_requests": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "RESIDENT":
            return Response(
                {
                    "success": False,
                    "message": "Only residents can create move requests."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        profile = getattr(user, "resident_profile", None)
        flat = getattr(profile, "flat", None)

        if not flat:
            return Response(
                {
                    "success": False,
                    "message": "No flat is linked with this resident."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = MoveRequestSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            move_request = serializer.save(
                flat=flat,
                requested_by=user,
                status="REQUESTED"
            )

            return Response(
                {
                    "success": True,
                    "message": "Move request submitted successfully.",
                    "move_request": MoveRequestSerializer(
                        move_request,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class MoveRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        move_request = get_object_or_404(
            MoveRequest,
            pk=pk
        )

        new_status = request.data.get("status")

        allowed_statuses = [
            "REQUESTED",
            "APPROVED",
            "COMPLETED",
            "REJECTED",
        ]

        if new_status not in allowed_statuses:
            return Response(
                {
                    "success": False,
                    "message": "Invalid move request status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        move_request.status = new_status
        move_request.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "message": "Move request status updated successfully.",
                "move_request": MoveRequestSerializer(
                    move_request,
                    context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK
        )
# ============================================================
# DOMESTIC WORKERS
# ============================================================

class DomesticWorkerListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "SECURITY", "RESIDENT"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Domestic worker access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        workers = DomesticWorker.objects.all().order_by("name")

        serializer = DomesticWorkerSerializer(
            workers,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": workers.count(),
                "workers": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DomesticWorkerSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            worker = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Domestic worker registered successfully.",
                    "worker": DomesticWorkerSerializer(
                        worker,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class DomesticWorkerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        worker = get_object_or_404(
            DomesticWorker,
            pk=pk
        )

        serializer = DomesticWorkerSerializer(
            worker,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Domestic worker updated successfully.",
                    "worker": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# DOMESTIC WORKER ATTENDANCE
# ============================================================

class StaffAttendanceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "SECURITY"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Attendance access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        attendance = StaffAttendance.objects.select_related(
            "worker",
            "recorded_by"
        ).order_by("-check_in")

        serializer = StaffAttendanceSerializer(
            attendance,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": attendance.count(),
                "attendance": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "SECURITY" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Security access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        worker_id = request.data.get("worker")
        gate_note = request.data.get("gate_note", "")

        worker = get_object_or_404(
            DomesticWorker,
            pk=worker_id
        )

        if not worker.is_active:
            return Response(
                {
                    "success": False,
                    "message": "This worker is inactive."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        existing = StaffAttendance.objects.filter(
            worker=worker,
            check_out__isnull=True
        ).first()

        if existing:
            return Response(
                {
                    "success": False,
                    "message": "Worker is already checked in."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance = StaffAttendance.objects.create(
            worker=worker,
            check_in=timezone.now(),
            gate_note=gate_note,
            recorded_by=user
        )

        return Response(
            {
                "success": True,
                "message": "Worker checked in successfully.",
                "attendance": StaffAttendanceSerializer(
                    attendance,
                    context={"request": request}
                ).data,
            },
            status=status.HTTP_201_CREATED
        )


class StaffAttendanceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "SECURITY" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Security access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        attendance = get_object_or_404(
            StaffAttendance,
            pk=pk
        )

        if attendance.check_out:
            return Response(
                {
                    "success": False,
                    "message": "Worker is already checked out."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.check_out = timezone.now()

        if "gate_note" in request.data:
            attendance.gate_note = request.data.get("gate_note", "")

        attendance.save(
            update_fields=[
                "check_out",
                "gate_note",
            ]
        )

        return Response(
            {
                "success": True,
                "message": "Worker checked out successfully.",
                "attendance": StaffAttendanceSerializer(
                    attendance,
                    context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK
        )
# ============================================================
# CERTIFICATE REQUESTS
# ============================================================

class CertificateRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role == "ADMIN" or user.is_superuser:
            requests_qs = CertificateRequest.objects.select_related(
                "requested_by",
                "flat"
            ).order_by("-requested_at")

        elif role == "RESIDENT":
            requests_qs = CertificateRequest.objects.filter(
                requested_by=user
            ).select_related(
                "requested_by",
                "flat"
            ).order_by("-requested_at")

        else:
            return Response(
                {
                    "success": False,
                    "message": "Certificate request access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CertificateRequestSerializer(
            requests_qs,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": requests_qs.count(),
                "certificate_requests": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "RESIDENT":
            return Response(
                {
                    "success": False,
                    "message": "Only residents can submit certificate requests."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        profile = getattr(user, "resident_profile", None)
        flat = getattr(profile, "flat", None)

        if not flat:
            return Response(
                {
                    "success": False,
                    "message": "No flat is linked with this resident."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CertificateRequestSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            certificate_request = serializer.save(
                requested_by=user,
                flat=flat,
                status="PENDING"
            )

            return Response(
                {
                    "success": True,
                    "message": "Certificate request submitted successfully.",
                    "certificate_request": CertificateRequestSerializer(
                        certificate_request,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class CertificateRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        certificate_request = get_object_or_404(
            CertificateRequest,
            pk=pk
        )

        new_status = request.data.get("status")

        allowed_statuses = [
            "PENDING",
            "APPROVED",
            "REJECTED",
            "ISSUED",
        ]

        if new_status not in allowed_statuses:
            return Response(
                {
                    "success": False,
                    "message": "Invalid certificate request status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        certificate_request.status = new_status
        certificate_request.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "message": "Certificate request status updated successfully.",
                "certificate_request": CertificateRequestSerializer(
                    certificate_request,
                    context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK
        )
# ============================================================
# SOCIETY EVENTS
# ============================================================

class SocietyEventListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "RESIDENT"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Event access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        events = SocietyEvent.objects.filter(
            is_active=True
        ).order_by("event_date")

        serializer = SocietyEventSerializer(
            events,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": events.count(),
                "events": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SocietyEventSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            event = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Society event created successfully.",
                    "event": SocietyEventSerializer(
                        event,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class SocietyEventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        event = get_object_or_404(
            SocietyEvent,
            pk=pk
        )

        serializer = SocietyEventSerializer(
            event,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Society event updated successfully.",
                    "event": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# SOCIETY MEETINGS
# ============================================================

class SocietyMeetingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "RESIDENT"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Meeting access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        meetings = SocietyMeeting.objects.select_related(
            "created_by"
        ).order_by("-meeting_date")

        serializer = SocietyMeetingSerializer(
            meetings,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": meetings.count(),
                "meetings": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SocietyMeetingSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            meeting = serializer.save(
                created_by=user
            )

            return Response(
                {
                    "success": True,
                    "message": "Society meeting created successfully.",
                    "meeting": SocietyMeetingSerializer(
                        meeting,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class SocietyMeetingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        meeting = get_object_or_404(
            SocietyMeeting,
            pk=pk
        )

        serializer = SocietyMeetingSerializer(
            meeting,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Society meeting updated successfully.",
                    "meeting": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )
# ============================================================
# SOCIETY ASSETS
# ============================================================

class SocietyAssetListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        assets = SocietyAsset.objects.all().order_by("name")

        serializer = SocietyAssetSerializer(
            assets,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": assets.count(),
                "assets": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SocietyAssetSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            asset = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Society asset created successfully.",
                    "asset": SocietyAssetSerializer(
                        asset,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class SocietyAssetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        asset = get_object_or_404(
            SocietyAsset,
            pk=pk
        )

        serializer = SocietyAssetSerializer(
            asset,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Society asset updated successfully.",
                    "asset": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# VENDOR / AMC
# ============================================================

class VendorAMCListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        vendors = VendorAMC.objects.all().order_by(
            "renewal_date"
        )

        serializer = VendorAMCSerializer(
            vendors,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": vendors.count(),
                "vendors": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = VendorAMCSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            vendor = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Vendor/AMC created successfully.",
                    "vendor": VendorAMCSerializer(
                        vendor,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class VendorAMCDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        vendor = get_object_or_404(
            VendorAMC,
            pk=pk
        )

        serializer = VendorAMCSerializer(
            vendor,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Vendor/AMC updated successfully.",
                    "vendor": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )
# ============================================================
# EXPENSES
# ============================================================

class ExpenseListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        expenses = Expense.objects.select_related(
            "created_by"
        ).order_by("-expense_date", "-id")

        serializer = ExpenseSerializer(
            expenses,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": expenses.count(),
                "expenses": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ExpenseSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            expense = serializer.save(
                created_by=user
            )

            return Response(
                {
                    "success": True,
                    "message": "Expense created successfully.",
                    "expense": ExpenseSerializer(
                        expense,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ExpenseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        expense = get_object_or_404(
            Expense,
            pk=pk
        )

        serializer = ExpenseSerializer(
            expense,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Expense updated successfully.",
                    "expense": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# EMERGENCY CONTACTS
# ============================================================

class EmergencyContactListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role not in ["ADMIN", "SECURITY", "RESIDENT"] and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Emergency contact access denied."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        contacts = EmergencyContact.objects.filter(
            is_active=True
        ).order_by("category", "name")

        serializer = EmergencyContactSerializer(
            contacts,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": contacts.count(),
                "contacts": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EmergencyContactSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            contact = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Emergency contact created successfully.",
                    "contact": EmergencyContactSerializer(
                        contact,
                        context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class EmergencyContactDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        role = getattr(user, "role", "")

        if role != "ADMIN" and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        contact = get_object_or_404(
            EmergencyContact,
            pk=pk
        )

        serializer = EmergencyContactSerializer(
            contact,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Emergency contact updated successfully.",
                    "contact": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )