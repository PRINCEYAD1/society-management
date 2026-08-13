from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MobileLoginView,
    ComplaintListCreateView,
    ComplaintDetailView,
    ProfileView,
    NoticeListCreateView,
    NoticeDetailView,
    AdminDashboardView,
    SecurityDashboardView,
    ResidentDashboardView,
)

app_name = "mobile_api"

urlpatterns = [
    path(
        "auth/login/",
        MobileLoginView.as_view(),
        name="mobile_login"
    ),
    path(
    "notices/",
    NoticeListCreateView.as_view(),
    name="notice_list_create"
    ),
    path(
    "complaints/",
    ComplaintListCreateView.as_view(),
    name="complaint_list_create"
    ),

    path(
    "complaints/<int:pk>/",
    ComplaintDetailView.as_view(),
    name="complaint_detail"
    ),

    path(
    "notices/<int:pk>/",
    NoticeDetailView.as_view(),
    name="notice_detail"
    ),
    path(
    "dashboard/resident/",
    ResidentDashboardView.as_view(),
    name="resident_dashboard"
    ),

    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile"
    ),

    path(
        "dashboard/admin/",
        AdminDashboardView.as_view(),
        name="admin_dashboard"
    ),

    path(
        "dashboard/security/",
        SecurityDashboardView.as_view(),
        name="security_dashboard"
    ),
]