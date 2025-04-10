from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

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


