from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import Building, Flat, Society


User = get_user_model()


class AdminLookupSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="lookup_admin",
            password="Strong-Test-Password-2026!",
            role="ADMIN",
        )
        self.resident = User.objects.create_user(
            username="lookup_resident",
            password="Strong-Test-Password-2026!",
            role="RESIDENT",
        )
        society = Society.objects.create(
            name="Test Society",
            address="Test Address",
        )
        building = Building.objects.create(
            society=society,
            name="Tower A",
            total_floors=10,
        )
        Flat.objects.create(
            building=building,
            flat_number="101",
            floor=1,
            area_sqft=900,
        )

    def test_unauthenticated_lookup_is_rejected(self):
        response = self.client.get(reverse("mobile_api:flat_lookup"))
        self.assertEqual(response.status_code, 401)

    def test_non_admin_lookup_is_forbidden(self):
        self.client.force_authenticate(self.resident)
        response = self.client.get(reverse("mobile_api:flat_lookup"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_read_building_choices(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse("mobile_api:building_lookup"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["buildings"]), 1)

    def test_admin_can_read_flat_choices(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse("mobile_api:flat_lookup"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["flats"]), 1)
