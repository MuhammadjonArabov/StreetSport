from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.models import Stadium, Bron, Team
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
import datetime

User = get_user_model()


class BronCreateAPIViewTest(APITestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            phone_number='+998911111111',
            password='password01',
            role='user'
        )

        # Create a stadium
        self.stadium = Stadium.objects.create(
            owner=self.user,
            name='Test Stadium',
            latitude='12.3459',
            longitude='-34.9876',
            price_hour='13000.00'
        )

        # Create a team
        self.team = Team.objects.create(
            name='Test Team',
            captain=self.user
        )

        self.client = APIClient()
        self.url = reverse('bron-create')

        # Valid data for creating a bron
        self.valid_data = {
            'stadium': self.stadium.id,
            'start_time': '2025-04-15T10:00:00Z',
            'end_time': '2025-04-15T11:00:00Z',
            'order_type': 'regular',
            'is_team': False,
            'team': None
        }

    def test_create_bron_authenticated(self):
        """Test creating a bron with valid data as authenticated user"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bron.objects.count(), 1)

        bron = Bron.objects.first()
        self.assertEqual(bron.stadium, self.stadium)
        self.assertEqual(bron.order_type, 'regular')
        self.assertIsNone(bron.team)

    def test_create_bron_with_team(self):
        """Test creating a bron with a team"""
        self.client.force_authenticate(user=self.user)

        team_data = self.valid_data.copy()
        team_data['is_team'] = True
        team_data['team'] = self.team.id

        response = self.client.post(self.url, team_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bron.objects.count(), 1)

        bron = Bron.objects.first()
        self.assertEqual(bron.team, self.team)
        self.assertEqual(bron.stadium, self.stadium)

    def test_create_bron_unauthenticated(self):
        """Test creating a bron without authentication"""
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Bron.objects.count(), 0)

    def test_create_bron_invalid_data(self):
        """Test creating a bron with invalid data"""
        self.client.force_authenticate(user=self.user)

        invalid_data = self.valid_data.copy()
        invalid_data['end_time'] = '2025-04-15T09:00:00Z'  # End time before start time

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Bron.objects.count(), 0)

    def test_create_bron_missing_required_field(self):
        """Test creating a bron with missing required field"""
        self.client.force_authenticate(user=self.user)

        incomplete_data = self.valid_data.copy()
        del incomplete_data['stadium']

        response = self.client.post(self.url, incomplete_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Bron.objects.count(), 0)

    def test_create_bron_team_required_when_is_team_true(self):
        """Test that team is required when is_team is True"""
        self.client.force_authenticate(user=self.user)

        invalid_team_data = self.valid_data.copy()
        invalid_team_data['is_team'] = True
        # team field is None by default in valid_data

        response = self.client.post(self.url, invalid_team_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('team', response.data)
        self.assertEqual(Bron.objects.count(), 0)