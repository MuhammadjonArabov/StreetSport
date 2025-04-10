from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.models import Stadium, Bron, Team
from django.urls import reverse
import datetime

User = get_user_model()

class BronUpdateAPIViewTest(APITestCase):
    def setUp(self):
        # Create users
        self.manager_user = User.objects.create_user(
            phone_number='+998911111111',
            password='password01',
            role='manager'  # Assuming 'manager' role is required for IsManager
        )
        self.regular_user = User.objects.create_user(
            phone_number='+998922222222',
            password='password02',
            role='user'
        )

        # Create a stadium
        self.stadium = Stadium.objects.create(
            owner=self.manager_user,
            name='Test Stadium',
            latitude='12.3459',
            longitude='-34.9876',
            price_hour='13000.00'
        )

        # Create a team
        self.team = Team.objects.create(
            name='Test Team',
            owner=self.manager_user
        )

        # Create a bron instance with a user
        self.bron = Bron.objects.create(
            stadium=self.stadium,
            user=self.manager_user,  # Added required user field
            start_time=datetime.datetime(2025, 4, 15, 10, 0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2025, 4, 15, 11, 0, tzinfo=datetime.timezone.utc),
            order_type='REGULAR',  # Adjust based on your model's valid choices
            is_paid=False
        )

        self.client = APIClient()
        self.url = reverse('bron-update', kwargs={'pk': self.bron.pk})

        # Valid update data
        self.valid_data = {
            'is_paid': True
        }

    def test_update_bron_as_manager(self):
        """Test updating a bron as a manager"""
        self.client.force_authenticate(user=self.manager_user)

        response = self.client.patch(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.bron.refresh_from_db()
        self.assertTrue(self.bron.is_paid)
        self.assertIn('id', response.data)
        self.assertIn('is_paid', response.data)

    def test_update_bron_as_non_manager(self):
        """Test updating a bron as a non-manager user"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.patch(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.bron.refresh_from_db()
        self.assertFalse(self.bron.is_paid)  # Ensure it wasn't updated

    def test_update_bron_unauthenticated(self):
        """Test updating a bron without authentication"""
        response = self.client.patch(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.bron.refresh_from_db()
        self.assertFalse(self.bron.is_paid)  # Ensure it wasn't updated

    def test_update_bron_invalid_data(self):
        """Test updating a bron with invalid data"""
        self.client.force_authenticate(user=self.manager_user)

        invalid_data = {'is_paid': 'not_a_boolean'}  # Invalid type for boolean field

        response = self.client.patch(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.bron.refresh_from_db()
        self.assertFalse(self.bron.is_paid)  # Ensure it wasn't updated

    def test_update_nonexistent_bron(self):
        """Test updating a bron that doesn't exist"""
        self.client.force_authenticate(user=self.manager_user)

        nonexistent_url = reverse('bron-update', kwargs={'pk': 9999})  # Assuming 9999 doesn't exist
        response = self.client.patch(nonexistent_url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)