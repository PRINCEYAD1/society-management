from django.shortcuts import get_object_or_404

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from amenities.models import Amenity


class AdminAmenitySerializer(serializers.ModelSerializer):
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
        read_only_fields = ["id"]


def _is_admin(user):
    return bool(
        getattr(user, "role", "") == "ADMIN"
        or getattr(user, "is_superuser", False)
    )


def _denied():
    return Response(
        {"success": False, "message": "Admin access required."},
        status=status.HTTP_403_FORBIDDEN,
    )


class AdminAmenityListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return _denied()
        amenities = Amenity.objects.all().order_by("name")
        return Response(
            {
                "success": True,
                "count": amenities.count(),
                "amenities": AdminAmenitySerializer(
                    amenities,
                    many=True,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if not _is_admin(request.user):
            return _denied()
        serializer = AdminAmenitySerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Amenity created successfully.",
                    "amenity": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AdminAmenityDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Amenity, pk=pk)

    def get(self, request, pk):
        if not _is_admin(request.user):
            return _denied()
        serializer = AdminAmenitySerializer(
            self.get_object(pk),
            context={"request": request},
        )
        return Response(
            {"success": True, "amenity": serializer.data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        if not _is_admin(request.user):
            return _denied()
        serializer = AdminAmenitySerializer(
            self.get_object(pk),
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Amenity updated successfully.",
                    "amenity": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
