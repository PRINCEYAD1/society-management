from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Flat, ResidentProfile
from operations.models import LostFoundItem


User = get_user_model()


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


class FlatAdminSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(
        source="building.name",
        read_only=True,
    )
    society_name = serializers.CharField(
        source="building.society.name",
        read_only=True,
    )
    resident_count = serializers.SerializerMethodField()

    class Meta:
        model = Flat
        fields = [
            "id",
            "building",
            "building_name",
            "society_name",
            "flat_number",
            "floor",
            "area_sqft",
            "ownership_type",
            "resident_count",
        ]
        read_only_fields = [
            "id",
            "building_name",
            "society_name",
            "resident_count",
        ]

    def get_resident_count(self, obj):
        return obj.residents.count()


class ResidentAdminSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )
    username = serializers.CharField(
        source="user.username",
    )
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
        allow_blank=True,
    )
    email = serializers.EmailField(
        source="user.email",
        required=False,
        allow_blank=True,
    )
    phone_number = serializers.CharField(
        source="user.phone_number",
        required=False,
        allow_blank=True,
    )
    is_active = serializers.BooleanField(
        source="user.is_active",
        required=False,
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        min_length=6,
    )
    flat_name = serializers.SerializerMethodField()

    class Meta:
        model = ResidentProfile
        fields = [
            "id",
            "user_id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_active",
            "flat",
            "flat_name",
            "is_primary_contact",
            "move_in_date",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]
        read_only_fields = [
            "id",
            "user_id",
            "flat_name",
        ]

    def get_flat_name(self, obj):
        return str(obj.flat) if obj.flat else None

    def validate_username(self, value):
        queryset = User.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.user_id)
        if queryset.exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user_data = validated_data.pop("user")

        user = User(
            role="RESIDENT",
            **user_data,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        return ResidentProfile.objects.create(
            user=user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user_data = validated_data.pop("user", {})

        for field, value in user_data.items():
            setattr(instance.user, field, value)

        instance.user.role = "RESIDENT"
        if password:
            instance.user.set_password(password)
        instance.user.save()

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        return instance


class LostFoundAdminSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LostFoundItem
        fields = [
            "id",
            "item_type",
            "title",
            "description",
            "location",
            "photo",
            "status",
            "reported_by",
            "reported_by_name",
            "reported_at",
        ]
        read_only_fields = [
            "id",
            "reported_by",
            "reported_by_name",
            "reported_at",
        ]

    def get_reported_by_name(self, obj):
        if not obj.reported_by:
            return None
        return (
            obj.reported_by.get_full_name()
            or obj.reported_by.username
        )


class FlatListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return _admin_required_response()

        flats = Flat.objects.select_related(
            "building",
            "building__society",
        ).prefetch_related("residents")

        serializer = FlatAdminSerializer(
            flats,
            many=True,
            context={"request": request},
        )
        return Response(
            {
                "success": True,
                "count": flats.count(),
                "flats": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if not _is_admin(request.user):
            return _admin_required_response()

        serializer = FlatAdminSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Flat created successfully.",
                    "flat": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class FlatDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Flat, pk=pk)

    def get(self, request, pk):
        if not _is_admin(request.user):
            return _admin_required_response()

        serializer = FlatAdminSerializer(
            self.get_object(pk),
            context={"request": request},
        )
        return Response(
            {
                "success": True,
                "flat": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        if not _is_admin(request.user):
            return _admin_required_response()

        serializer = FlatAdminSerializer(
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
                    "message": "Flat updated successfully.",
                    "flat": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResidentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return _admin_required_response()

        residents = ResidentProfile.objects.select_related(
            "user",
            "flat",
            "flat__building",
        )
        serializer = ResidentAdminSerializer(
            residents,
            many=True,
            context={"request": request},
        )
        return Response(
            {
                "success": True,
                "count": residents.count(),
                "residents": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if not _is_admin(request.user):
            return _admin_required_response()

        serializer = ResidentAdminSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Resident created successfully.",
                    "resident": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResidentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(
            ResidentProfile.objects.select_related("user", "flat"),
            pk=pk,
        )

    def get(self, request, pk):
        if not _is_admin(request.user):
            return _admin_required_response()

        serializer = ResidentAdminSerializer(
            self.get_object(pk),
            context={"request": request},
        )
        return Response(
            {
                "success": True,
                "resident": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        if not _is_admin(request.user):
            return _admin_required_response()

        serializer = ResidentAdminSerializer(
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
                    "message": "Resident updated successfully.",
                    "resident": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LostFoundListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = LostFoundItem.objects.select_related(
            "reported_by"
        ).all()

        serializer = LostFoundAdminSerializer(
            items,
            many=True,
            context={"request": request},
        )
        return Response(
            {
                "success": True,
                "count": items.count(),
                "lost_found": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = LostFoundAdminSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save(reported_by=request.user)
            return Response(
                {
                    "success": True,
                    "message": "Lost & found item created successfully.",
                    "lost_found_item": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LostFoundDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(LostFoundItem, pk=pk)

    def get(self, request, pk):
        serializer = LostFoundAdminSerializer(
            self.get_object(pk),
            context={"request": request},
        )
        return Response(
            {
                "success": True,
                "lost_found_item": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        item = self.get_object(pk)

        if not (
            _is_admin(request.user)
            or item.reported_by_id == request.user.id
        ):
            return Response(
                {
                    "success": False,
                    "message": "You are not allowed to update this item.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = LostFoundAdminSerializer(
            item,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Lost & found item updated successfully.",
                    "lost_found_item": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
