from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.models import Stadium

User = get_user_model()

class StadiumListTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(phone_number='+998977777777', password='password07', role='admin')
        self.owner_user = User.objects.create_user(phone_number='+998911111111', password='password01', role='owner')
        self.other_user = User.objects.create_user(phone_number='+998922222222', password='password02', role='user')

        self.stadium_data = {
            'latitude': '12.3459',
            'longitude': '-34.9876',
            'price_hour': '13000.00'
        }

        self.client = APIClient()

    def test_list_stadiums_authenticated_user(self):
        self.client.force_authenticate(user=self.owner_user)
        Stadium.objects.create(owner=self.owner_user, name='Test Stadium', **self.stadium_data)

        response = self.client.get('/api/v1/common/stadium-list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_list_stadiums_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        Stadium.objects.create(owner=self.owner_user, name='Test Stadium', **self.stadium_data)

        response = self.client.get('/api/v1/common/stadium-list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_list_stadiums_non_authenticated(self):
        response = self.client.get('/api/v1/common/stadium-list/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_stadium_by_name(self):
        self.client.force_authenticate(user=self.owner_user)
        Stadium.objects.create(owner=self.owner_user, name='Searchable Stadium', **self.stadium_data)
        Stadium.objects.create(owner=self.owner_user, name='Other Stadium', **self.stadium_data)

        response = self.client.get('/api/v1/common/stadium-list/', {'search': 'Searchable'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Searchable Stadium')

    def test_filter_stadium_by_price_hour(self):
        self.client.force_authenticate(user=self.owner_user)
        Stadium.objects.create(owner=self.owner_user, name='Stadium 1', **self.stadium_data)
        Stadium.objects.create(owner=self.owner_user, name='Stadium 2', price_hour='15000.00',
                             latitude='12.3459', longitude='-34.9876')

        response = self.client.get('/api/v1/common/stadium-list/', {'price_hour': '13000.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['price_hour'], '13000.00')

    def test_order_stadiums_by_name(self):
        self.client.force_authenticate(user=self.owner_user)
        Stadium.objects.create(owner=self.owner_user, name='Z Stadium', **self.stadium_data)
        Stadium.objects.create(owner=self.owner_user, name='A Stadium', **self.stadium_data)

        response = self.client.get('/api/v1/common/stadium-list/', {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'A Stadium')
        self.assertEqual(response.data['results'][1]['name'], 'Z Stadium')

    def test_check_stadium_serializer_fields(self):
        self.client.force_authenticate(user=self.owner_user)
        Stadium.objects.create(owner=self.owner_user, name='Test Stadium', **self.stadium_data)

        response = self.client.get('/api/v1/common/stadium-list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertGreater(len(response.data['results']), 0, "Response contains no stadiums.")
        stadium_data = response.data['results'][0]

        self.assertIn('id', stadium_data)
        self.assertIn('name', stadium_data)
        self.assertIn('latitude', stadium_data)
        self.assertIn('longitude', stadium_data)
        self.assertIn('description', stadium_data)
        self.assertIn('price_hour', stadium_data)
        self.assertIn('manager', stadium_data)
        self.assertIn('is_active', stadium_data)
        self.assertIn('image', stadium_data)

    def test_stadium_manager_info_in_response(self):
        self.client.force_authenticate(user=self.owner_user)
        Stadium.objects.create(owner=self.owner_user, manager=self.owner_user,
                             name='Test Stadium', **self.stadium_data)

        response = self.client.get('/api/v1/common/stadium-list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stadium_data = response.data['results'][0]
        self.assertIn('manager', stadium_data)
        self.assertIn('id', stadium_data['manager'])
        self.assertIn('phone_number', stadium_data['manager'])