from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MobileLoginView,
    ProfileView,

    AdminDashboardView,
    SecurityDashboardView,
    ResidentDashboardView,

    NoticeListCreateView,
    NoticeDetailView,

    ComplaintListCreateView,
    ComplaintDetailView,

    VisitorListCreateView,
    VisitorDetailView,

    InvoiceListView,
    InvoiceDetailView,
    PaymentListView,
    SocietyAssetListCreateView,
    SocietyAssetDetailView,
    VendorAMCListCreateView,
    VendorAMCDetailView,

    AmenityListView,
    AmenityBookingListCreateView,
    AmenityBookingDetailView,

    ParcelListCreateView,
    ParcelDetailView,
    ExpenseListCreateView,
    ExpenseDetailView,
    EmergencyContactListCreateView,
    EmergencyContactDetailView,

    VehicleListCreateView,
    VehicleDetailView,

    MoveRequestListCreateView,
    MoveRequestDetailView,

    DomesticWorkerListCreateView,
    DomesticWorkerDetailView,
    StaffAttendanceListCreateView,
    StaffAttendanceDetailView,

    CertificateRequestListCreateView,
    CertificateRequestDetailView,
    SocietyEventListCreateView,
    SocietyEventDetailView,
    SocietyMeetingListCreateView,
    SocietyMeetingDetailView,
)

app_name = "mobile_api"


urlpatterns = [

    # =========================================================
    # AUTHENTICATION
    # =========================================================

    path(
        "auth/login/",
        MobileLoginView.as_view(),
        name="mobile_login",
    ),
    path(
    "events/",
    SocietyEventListCreateView.as_view(),
    name="society_event_list_create",
    ), 
    path(
    "assets/",
    SocietyAssetListCreateView.as_view(),
    name="society_asset_list_create",
    ),

    path(
    "assets/<int:pk>/",
    SocietyAssetDetailView.as_view(),
    name="society_asset_detail",
    ),
    path(
    "expenses/",
    ExpenseListCreateView.as_view(),
    name="expense_list_create",
    ),

    path(
    "expenses/<int:pk>/",
    ExpenseDetailView.as_view(),
    name="expense_detail",
    ),

    path(
    "emergency-contacts/",
    EmergencyContactListCreateView.as_view(),
    name="emergency_contact_list_create",
    ),

    path(
    "emergency-contacts/<int:pk>/",
    EmergencyContactDetailView.as_view(),
    name="emergency_contact_detail",
    ),

    path(
    "vendor-amc/",
    VendorAMCListCreateView.as_view(),
    name="vendor_amc_list_create",
    ),

    path(
    "vendor-amc/<int:pk>/",
    VendorAMCDetailView.as_view(),
    name="vendor_amc_detail",
    ),


    path(
    "events/<int:pk>/",
    SocietyEventDetailView.as_view(),
    name="society_event_detail",
    ),

    path(
    "meetings/",
    SocietyMeetingListCreateView.as_view(),
    name="society_meeting_list_create",
    ),

    path(
    "meetings/<int:pk>/",
    SocietyMeetingDetailView.as_view(),
    name="society_meeting_detail",
    ),
    path(
    "parcels/",
    ParcelListCreateView.as_view(),
    name="parcel_list_create",
    ),
    path(
    "move-requests/",
    MoveRequestListCreateView.as_view(),
    name="move_request_list_create",
    ),
    path(
    "domestic-workers/",
    DomesticWorkerListCreateView.as_view(),
    name="domestic_worker_list_create",
    ),

    path(
    "domestic-workers/<int:pk>/",
    DomesticWorkerDetailView.as_view(),
    name="domestic_worker_detail",
    ),

    path(
    "domestic-workers/attendance/",
    StaffAttendanceListCreateView.as_view(),
    name="staff_attendance_list_create",
    ),

    path(
    "domestic-workers/attendance/<int:pk>/",
    StaffAttendanceDetailView.as_view(),
    name="staff_attendance_detail",
    ),
    path(
    "move-requests/<int:pk>/",
    MoveRequestDetailView.as_view(),
    name="move_request_detail",
    ),
    path(
    "vehicles/",
    VehicleListCreateView.as_view(),
    name="vehicle_list_create",
    ),

    path(
    "vehicles/<int:pk>/",
    VehicleDetailView.as_view(),
    name="vehicle_detail",
    ),

    path(
    "parcels/<int:pk>/",
    ParcelDetailView.as_view(),
    name="parcel_detail",
    ),

    path(
    "amenities/",
    AmenityListView.as_view(),
    name="amenity_list",
    ),

    path(
    "amenities/bookings/",
    AmenityBookingListCreateView.as_view(),
    name="amenity_booking_list_create",
    ),

    path(
    "amenities/bookings/<int:pk>/",
    AmenityBookingDetailView.as_view(),
    name="amenity_booking_detail",
    ),

    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
    "certificate-requests/",
    CertificateRequestListCreateView.as_view(),
    name="certificate_request_list_create",
    ),

    path(
    "certificate-requests/<int:pk>/",
    CertificateRequestDetailView.as_view(),
    name="certificate_request_detail",
    ),


    # =========================================================
    # USER PROFILE
    # =========================================================

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),


    # =========================================================
    # DASHBOARDS
    # =========================================================

    path(
        "dashboard/admin/",
        AdminDashboardView.as_view(),
        name="admin_dashboard",
    ),

    path(
        "dashboard/security/",
        SecurityDashboardView.as_view(),
        name="security_dashboard",
    ),

    path(
        "dashboard/resident/",
        ResidentDashboardView.as_view(),
        name="resident_dashboard",
    ),


    # =========================================================
    # NOTICES
    # =========================================================

    path(
        "notices/",
        NoticeListCreateView.as_view(),
        name="notice_list_create",
    ),

    path(
        "notices/<int:pk>/",
        NoticeDetailView.as_view(),
        name="notice_detail",
    ),


    # =========================================================
    # COMPLAINTS
    # =========================================================

    path(
        "complaints/",
        ComplaintListCreateView.as_view(),
        name="complaint_list_create",
    ),

    path(
        "complaints/<int:pk>/",
        ComplaintDetailView.as_view(),
        name="complaint_detail",
    ),


    # =========================================================
    # VISITORS
    # =========================================================

    path(
        "visitors/",
        VisitorListCreateView.as_view(),
        name="visitor_list_create",
    ),

    path(
        "visitors/<int:pk>/",
        VisitorDetailView.as_view(),
        name="visitor_detail",
    ),


    # =========================================================
    # BILLING
    # =========================================================

    path(
        "billing/invoices/",
        InvoiceListView.as_view(),
        name="invoice_list",
    ),

    path(
        "billing/invoices/<int:pk>/",
        InvoiceDetailView.as_view(),
        name="invoice_detail",
    ),

    path(
        "billing/payments/",
        PaymentListView.as_view(),
        name="payment_list",
    ),
]