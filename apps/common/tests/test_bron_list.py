from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.models import Stadium, Bron, Team
from django.urls import reverse
import datetime

User = get_user_model()

class OwnerBronListAPIViewTest(APITestCase):
    def setUp(self):
        # Clear all relevant tables to ensure isolation
        Bron.objects.all().delete()
        Stadium.objects.all().delete()
        Team.objects.all().delete()
        User.objects.all().delete()

        # Create users
        self.owner_user = User.objects.create_user(
            phone_number='+998911111111',
            password='password01',
            role='owner'
        )
        self.regular_user = User.objects.create_user(
            phone_number='+998922222222',
            password='password02',
            role='user'
        )

        # Create stadiums owned by owner_user
        self.stadium1 = Stadium.objects.create(
            owner=self.owner_user,
            name='Stadium A',
            latitude='12.3459',
            longitude='-34.9876',
            price_hour='13000.00'
        )
        self.stadium2 = Stadium.objects.create(
            owner=self.owner_user,
            name='Stadium B',
            latitude='12.3459',
            longitude='-34.9876',
            price_hour='15000.00'
        )

        # Create a team
        self.team = Team.objects.create(
            name='Test Team',
            owner=self.owner_user
        )

        # Create bron instances (times in UTC)
        self.bron1 = Bron.objects.create(
            stadium=self.stadium1,
            user=self.owner_user,
            start_time=datetime.datetime(2025, 4, 15, 10, 0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2025, 4, 15, 11, 0, tzinfo=datetime.timezone.utc),
            order_type='REGULAR',
            is_paid=True
        )
        self.bron2 = Bron.objects.create(
            stadium=self.stadium2,
            user=self.owner_user,
            team=self.team,
            start_time=datetime.datetime(2025, 4, 15, 12, 0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2025, 4, 15, 13, 0, tzinfo=datetime.timezone.utc),
            order_type='REGULAR',
            is_paid=False
        )

        # Verify only 2 Bron objects exist
        self.assertEqual(Bron.objects.count(), 2, f"Expected 2 Bron objects, got {Bron.objects.count()}")

        self.client = APIClient()
        self.url = reverse('owner-bron-list')

    def test_list_brons_as_owner(self):
        """Test listing brons as an owner"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2, f"Expected 2 items, got {len(response.data['results'])}")
        self.assertEqual(response.data['results'][0]['stadium_name'], 'Stadium A')
        self.assertEqual(response.data['results'][1]['stadium_name'], 'Stadium B')
        self.assertEqual(response.data['results'][0]['start_time'], '2025-04-15 15:00:00')  # Adjusted to UTC+5
        self.assertIsNone(response.data['results'][0]['team_name'])
        self.assertEqual(response.data['results'][1]['team_name'], 'Test Team')

    def test_list_brons_as_non_owner(self):
        """Test listing brons as a non-owner user"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_brons_unauthenticated(self):
        """Test listing brons without authentication"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_stadium_name(self):
        """Test filtering brons by stadium name"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.get(self.url, {'stadium__name': 'Stadium A'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1, f"Expected 1 item, got {len(response.data['results'])}")
        self.assertEqual(response.data['results'][0]['stadium_name'], 'Stadium A')

    def test_filter_by_is_paid(self):
        """Test filtering brons by is_paid"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.get(self.url, {'is_paid': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1, f"Expected 1 item, got {len(response.data['results'])}")
        self.assertTrue(response.data['results'][0]['is_paid'])

    def test_search_by_stadium_name(self):
        """Test searching brons by stadium name"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.get(self.url, {'search': 'Stadium B'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1, f"Expected 1 item, got {len(response.data['results'])}")
        self.assertEqual(response.data['results'][0]['stadium_name'], 'Stadium B')

    def test_order_by_end_time(self):
        """Test ordering brons by end_time"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.get(self.url, {'ordering': 'end_time'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2, f"Expected 2 items, got {len(response.data['results'])}")
        self.assertEqual(response.data['results'][0]['end_time'], '2025-04-15 16:00:00')  # Adjusted to UTC+5
        self.assertEqual(response.data['results'][1]['end_time'], '2025-04-15 18:00:00')  # Adjusted to UTC+5