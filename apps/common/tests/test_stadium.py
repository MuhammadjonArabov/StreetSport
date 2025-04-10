from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.models import Stadium



User = get_user_model()

class StadiumTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(phone_number='+998977777777', password='password07', role='admin')
        self.owner_user = User.objects.create_user(phone_number='+998911111111', password='password01', role='owner')
        self.other_user = User.objects.create_user(phone_number='+998922222222', password='password02', role='user')

        self.stadium_data = {
            'name': 'Test Stadium',
            'latitude': '12.3459',
            'longitude': '-34.9876',
            'price_hour': '13000.00'
        }

        self.client = APIClient()

    def test_create_stadium_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        self.stadium_data_admin = {
            'name': 'Test Stadium',
            'latitude': '12.3459',
            'longitude': '-34.9876',
            'price_hour': '13000.00',
            'owner': self.owner_user.id
        }

        response = self.client.post('/api/v1/common/stadium/', self.stadium_data_admin, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.stadium_data_admin['name'])

    def test_create_stadium_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.post('/api/v1/common/stadium/', self.stadium_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.stadium_data['name'])

    def test_create_stadium_non_owner_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post('/api/v1/common/stadium/', self.stadium_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_stadium_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        stadium = Stadium.objects.create(owner=self.owner_user, **self.stadium_data)
        updated_data = {
            'name': 'Updated Stadium',
            'latitude': '41.7128',
            'longitude': '-73.0060',
            'price_hour': '150.00'
        }
        response = self.client.patch(f'/api/v1/common/stadium/{stadium.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], updated_data['name'])

    def test_update_stadium_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        stadium = Stadium.objects.create(owner=self.owner_user, **self.stadium_data)
        updated_data = {
            'name': 'Updated by Owner',
            'latitude': '41.7128',
            'longitude': '-73.0060',
            'price_hour': '150.00'
        }
        response = self.client.patch(f'/api/v1/common/stadium/{stadium.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], updated_data['name'])

    def test_update_stadium_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        stadium = Stadium.objects.create(owner=self.owner_user, **self.stadium_data)
        updated_data = {
            'name': 'Updated by Non-Owner',
            'latitude': '42.7128',
            'longitude': '-72.0060',
            'price_hour': '200.00'
        }
        response = self.client.patch(f'/api/v1/common/stadium/{stadium.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_stadium_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        stadium = Stadium.objects.create(owner=self.owner_user, **self.stadium_data)
        response = self.client.delete(f'/api/v1/common/stadium/{stadium.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Stadium.objects.filter(id=stadium.id).exists())

    def test_delete_stadium_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        stadium = Stadium.objects.create(owner=self.owner_user, **self.stadium_data)
        response = self.client.delete(f'/api/v1/common/stadium/{stadium.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Stadium.objects.filter(id=stadium.id).exists())

    def test_delete_stadium_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        stadium = Stadium.objects.create(owner=self.owner_user, **self.stadium_data)
        response = self.client.delete(f'/api/v1/common/stadium/{stadium.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_stadiums_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        stadium = Stadium.objects.create(owner=self.owner_user, **self.stadium_data)
        response = self.client.get('/api/v1/common/stadium/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_stadiums_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        stadium = Stadium.objects.create(owner=self.owner_user, **self.stadium_data)
        response = self.client.get('/api/v1/common/stadium/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
