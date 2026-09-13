from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.models import Invoice
from core.models import Building, Flat


def _is_admin(user):
    return bool(
        getattr(user, "role", "") == "ADMIN"
        or getattr(user, "is_superuser", False)
    )


def _admin_required_response():
    return Response(
        {
            "success": False,
            "message": "Admin access required.",
        },
        status=status.HTTP_403_FORBIDDEN,
    )


class BuildingLookupView(APIView):
    """Small, read-only payload used by Admin mobile dropdowns."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return _admin_required_response()

        buildings = Building.objects.select_related("society").order_by(
            "society__name", "name"
        )
        return Response(
            {
                "success": True,
                "buildings": [
                    {
                        "id": building.id,
                        "label": f"{building.name} - {building.society.name}",
                    }
                    for building in buildings
                ],
            },
            status=status.HTTP_200_OK,
        )


class FlatLookupView(APIView):
    """Read-only flat choices for residents, visitors, billing and operations."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return _admin_required_response()

        flats = Flat.objects.select_related("building").order_by(
            "building__name", "floor", "flat_number"
        )
        return Response(
            {
                "success": True,
                "flats": [
                    {
                        "id": flat.id,
                        "label": str(flat),
                    }
                    for flat in flats
                ],
            },
            status=status.HTTP_200_OK,
        )


class InvoiceLookupView(APIView):
    """Read-only invoice choices for payment recording.

    Only unpaid/partially-paid invoices are returned so an Admin cannot
    accidentally record another payment against an already-paid invoice.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return _admin_required_response()

        invoices = (
            Invoice.objects.select_related("flat", "flat__building")
            .exclude(status=Invoice.Status.PAID)
            .order_by("due_date", "id")
        )
        return Response(
            {
                "success": True,
                "invoices": [
                    {
                        "id": invoice.id,
                        "label": (
                            f"#{invoice.id} • {invoice.flat} • "
                            f"{invoice.title} • ₹{invoice.balance()}"
                        ),
                        "amount": str(invoice.amount),
                        "balance": str(invoice.balance()),
                        "status": invoice.status,
                    }
                    for invoice in invoices
                ],
            },
            status=status.HTTP_200_OK,
        )
