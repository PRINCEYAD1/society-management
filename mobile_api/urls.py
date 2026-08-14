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
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
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