from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('accounts.urls')),
    path('billing/', include('billing.urls')),
    path('notices/', include('notices.urls')),
    path('complaints/', include('complaints.urls')),
    path('visitors/', include('visitors.urls')),
    path('amenities/', include('amenities.urls')),
    path('staff/', include('staffmgmt.urls')),
    path('operations/', include('operations.urls')),
    path('', include('core.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("mobile_api.urls")),

    # your existing urls...
]