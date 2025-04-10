from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.models import Stadium
from rest_framework.permissions import IsAdminUser
from django.urls import reverse

User = get_user_model()


class StadiumStatsCountAPIViewTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            phone_number='+998977777777',
            password='password07',
            role='admin'
        )
        self.regular_user = User.objects.create_user(
            phone_number='+998911111111',
            password='password01',
            role='user'
        )

        self.stadium_data = {
            'latitude': '12.3459',
            'longitude': '-34.9876',
            'price_hour': '13000.00'
        }

        Stadium.objects.create(
            owner=self.regular_user,
            name='Active Stadium 1',
            is_active=True,
            **self.stadium_data
        )
        Stadium.objects.create(
            owner=self.regular_user,
            name='Active Stadium 2',
            is_active=True,
            **self.stadium_data
        )
        Stadium.objects.create(
            owner=self.regular_user,
            name='Inactive Stadium',
            is_active=False,
            **self.stadium_data
        )

        self.client = APIClient()
        self.url = reverse('status-count')

    def test_stadium_stats_admin_access(self):
        """Test that admin can access the stats endpoint and gets correct counts"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_stadiums'], 3)
        self.assertEqual(response.data['active_stadiums'], 2)
        self.assertEqual(response.data['inactive_stadiums'], 1)

        # Verify response contains all expected fields
        expected_fields = ['total_stadiums', 'active_stadiums', 'inactive_stadiums']
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_stadium_stats_non_admin_access(self):
        """Test that non-admin user gets 403 Forbidden"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stadium_stats_unauthenticated_access(self):
        """Test that unauthenticated user gets 401 Unauthorized"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stadium_stats_empty_database(self):
        """Test stats when no stadiums exist"""
        Stadium.objects.all().delete()

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_stadiums'], 0)
        self.assertEqual(response.data['active_stadiums'], 0)
        self.assertEqual(response.data['inactive_stadiums'], 0)