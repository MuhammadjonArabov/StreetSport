from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.models import Stadium, Bron, Team
from django.urls import reverse
from django.utils import timezone
import datetime

User = get_user_model()

class BronCreateAPIViewTest(APITestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(phone_number='+998911111111', password='password01', role='user')
        self.manager = User.objects.create_user(phone_number='+998922222222', password='password02', role='manager')
        self.other_user = User.objects.create_user(phone_number='+998933333333', password='password03', role='user')

        # Create a stadium
        self.stadium = Stadium.objects.create(
            owner=self.manager,
            name='Test Stadium',
            latitude='12.3459',
            longitude='-34.9876',
            price_hour='13000.00'
        )

        # Create a team
        self.team = Team.objects.create(name='User Team', owner=self.user)
        self.other_team = Team.objects.create(name='Other Team', owner=self.other_user)

        self.client = APIClient()
        self.url = reverse('bron-create')

        # Valid data for a user booking (1 hour from now)
        now = timezone.now()
        self.valid_data = {
            'stadium': self.stadium.id,
            'start_time': (now + datetime.timedelta(hours=1)).isoformat(),
            'end_time': (now + datetime.timedelta(hours=2)).isoformat(),
            'order_type': 'cash',  # Updated to a valid choice from ProviderType
            'is_team': False,
            'team': None
        }

    def test_create_bron_authenticated_user(self):
        """Test creating a bron as an authenticated regular user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bron.objects.count(), 1)
        bron = Bron.objects.first()
        self.assertEqual(bron.user, self.user)
        self.assertEqual(bron.stadium, self.stadium)
        self.assertEqual(bron.order_type, 'cash')  # Updated to match
        self.assertIsNone(bron.team)

    def test_create_bron_with_team(self):
        """Test creating a bron with a team as the team owner"""
        self.client.force_authenticate(user=self.user)
        team_data = self.valid_data.copy()
        team_data['is_team'] = True
        team_data['team'] = self.team.id
        response = self.client.post(self.url, team_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bron.objects.count(), 1)
        bron = Bron.objects.first()
        self.assertEqual(bron.team, self.team)

    def test_create_bron_unauthenticated(self):
        """Test creating a bron without authentication"""
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Bron.objects.count(), 0)

    def test_create_bron_as_manager(self):
        """Test creating a bron as a manager (should fail)"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Admins and Managers cannot book stadiums', str(response.data))
        self.assertEqual(Bron.objects.count(), 0)

    def test_create_bron_invalid_time(self):
        """Test creating a bron with invalid time (end before start)"""
        self.client.force_authenticate(user=self.user)
        invalid_data = self.valid_data.copy()
        invalid_data['end_time'] = (timezone.now() + datetime.timedelta(minutes=30)).isoformat()  # Before start_time

        response = self.client.post(self.url, invalid_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('The time was entered incorrectly', str(response.data))
        self.assertEqual(Bron.objects.count(), 0)

    def test_create_bron_time_slot_already_booked(self):
        """Test creating a bron when the time slot is already booked"""
        self.client.force_authenticate(user=self.user)
        # Create an existing booking
        Bron.objects.create(
            stadium=self.stadium,
            user=self.user,
            start_time=timezone.now() + datetime.timedelta(hours=1),
            end_time=timezone.now() + datetime.timedelta(hours=2),
            order_type='cash'  # Updated to match
        )

        response = self.client.post(self.url, self.valid_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This time slot is already booked', str(response.data))
        self.assertEqual(Bron.objects.count(), 1)  # Only the first booking exists

    def test_create_bron_team_without_permission(self):
        """Test creating a bron with a team the user doesn't own or belong to"""
        self.client.force_authenticate(user=self.user)
        invalid_team_data = self.valid_data.copy()
        invalid_team_data['is_team'] = True
        invalid_team_data['team'] = self.other_team.id

        response = self.client.post(self.url, invalid_team_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You are not allowed to book on behalf of this team', str(response.data))
        self.assertEqual(Bron.objects.count(), 0)

    def test_create_bron_is_team_true_no_team(self):
        """Test creating a bron with is_team=True but no team provided"""
        self.client.force_authenticate(user=self.user)
        no_team_data = self.valid_data.copy()
        no_team_data['is_team'] = True
        no_team_data['team'] = None

        response = self.client.post(self.url, no_team_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Team must be provided for team bookings', str(response.data))
        self.assertEqual(Bron.objects.count(), 0)

    def test_create_bron_is_team_false_with_team(self):
        """Test creating a bron with is_team=False but team provided"""
        self.client.force_authenticate(user=self.user)
        invalid_team_data = self.valid_data.copy()
        invalid_team_data['is_team'] = False
        invalid_team_data['team'] = self.team.id

        response = self.client.post(self.url, invalid_team_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Team should not be provided for user bookings', str(response.data))
        self.assertEqual(Bron.objects.count(), 0)

    def test_create_bron_invalid_duration(self):
        """Test creating a bron with invalid duration (less than 1 hour)"""
        self.client.force_authenticate(user=self.user)
        invalid_duration_data = self.valid_data.copy()
        invalid_duration_data['end_time'] = (timezone.now() + datetime.timedelta(hours=1, minutes=30)).isoformat()  # 1.5 hours

        response = self.client.post(self.url, invalid_duration_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('The booking time was not available', str(response.data))
        self.assertEqual(Bron.objects.count(), 0)