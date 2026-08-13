from django.contrib.auth import authenticate
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Flat, ResidentProfile
from billing.models import Invoice, Payment
from complaints.models import Complaint
from visitors.models import Visitor
from amenities.models import AmenityBooking
from notices.models import Notice

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