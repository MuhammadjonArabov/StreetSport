from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.models import Stadium, Bron
from django.urls import reverse
from django.utils import timezone
import datetime
import decimal

User = get_user_model()

class OwnerStadiumStatsViewTest(APITestCase):
    def setUp(self):
        Stadium.objects.all().delete()
        User.objects.all().delete()
        Bron.objects.all().delete()

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
        self.stadium1 = Stadium.objects.create(
            owner=self.owner_user,
            name='Stadium A',
            latitude='12.3459',
            longitude='-34.9876',
            price_hour=decimal.Decimal('13000.00')
        )
        self.stadium2 = Stadium.objects.create(
            owner=self.owner_user,
            name='Stadium B',
            latitude='12.3459',
            longitude='-34.9876',
            price_hour=decimal.Decimal('15000.00')
        )
        now = timezone.now()
        Bron.objects.create(
            stadium=self.stadium1,
            user=self.regular_user,
            start_time=now + datetime.timedelta(hours=1),
            end_time=now + datetime.timedelta(hours=2),
            order_type='cash',
            is_paid=True
        )
        Bron.objects.create(
            stadium=self.stadium1,
            user=self.regular_user,
            start_time=now + datetime.timedelta(hours=3),
            end_time=now + datetime.timedelta(hours=4),
            order_type='cash',
            is_paid=False
        )
        Bron.objects.create(
            stadium=self.stadium2,
            user=self.regular_user,
            start_time=now + datetime.timedelta(hours=1),
            end_time=now + datetime.timedelta(hours=2),
            order_type='cash',
            is_paid=True
        )

        self.client = APIClient()
        self.url = reverse('owner-stadium-statistic')

    def test_stadium_stats_as_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']),
            2,
            f"Expected 2 stadiums, got {len(response.data['results'])}: {response.data['results']}"
        )

    def test_stadium_stats_no_bookings(self):
        empty_stadium = Stadium.objects.create(
            owner=self.owner_user,
            name='Empty Stadium',
            latitude='12.3459',
            longitude='-34.9876',
            price_hour=decimal.Decimal('10000.00')
        )
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']),
            3,
            f"Expected 3 stadiums, got {len(response.data['results'])}: {response.data['results']}"
        )

    def test_stadium_stats_only_unpaid_bookings(self):
        unpaid_stadium = Stadium.objects.create(
            owner=self.owner_user,
            name='Unpaid Stadium',
            latitude='12.3459',
            longitude='-34.9876',
            price_hour=decimal.Decimal('20000.00')
        )
        Bron.objects.create(
            stadium=unpaid_stadium,
            user=self.regular_user,
            start_time=timezone.now() + datetime.timedelta(hours=1),
            end_time=timezone.now() + datetime.timedelta(hours=2),
            order_type='cash',
            is_paid=False
        )
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']),
            3,
            f"Expected 3 stadiums, got {len(response.data['results'])}: {response.data['results']}"
        )

    def test_stadium_stats_as_non_owner(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stadium_stats_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)