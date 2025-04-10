from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='+998932004877', password='test2004')
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.logout_url = reverse('logout')
        self.change_password_url = reverse('change-password')

    def test_user_register(self):
        data = {
            'phone_number': '+998924441133',
            'full_name': 'Jon Bron',
            'password': 'password04',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)

    def test_user_login(self):
        data = {
            'phone_number': '+998932004877',
            'password': 'test2004',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.access_token = response.data['tokens']['access']
        self.refresh_tokens = response.data['tokens']['refresh']

    def test_user_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer' + self.access_token)
        response = self.client.post(self.logout_url, data={'refresh': self.refresh_tokens})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_change_password(self):
        new_password = 'password02'
        data = {
            'old_password': 'password04',
            'new_password': new_password,
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer' + self.access_token)
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        login_data={
            'phone_number': '+998932004877',
            'password': new_password,
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_user_login_invalid_password(self):
        data = {
            'phone_number': '+998932004877',
            'password': 'password09',
        }
        response = self.client.post(self.login_url, data, fromat='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_register_phone_number_exists(self):
        data = {
            'phone_number': '+998932004877',
            'full_name': 'Toms Jared',
            'password': 'password98',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'][0], "This phone number is already registered")
