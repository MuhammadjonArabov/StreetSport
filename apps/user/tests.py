import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.user.models import User
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        return User.objects.create_user(**kwargs)
    return make_user

@pytest.fixture
def registered_user(api_client):
    user = User.objects.create_user(
        phone_number="+998911112233",
        full_name="Test User",
        password="StrongPassword123"
    )
    refresh = RefreshToken.for_user(user)
    return {
        "user": user,
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }

# 1. Register
@pytest.mark.django_db
def test_user_register(api_client):
    url = reverse('register')  # URL name django.urls.da belgilangan bo‘lishi kerak
    payload = {
        "full_name": "New User",
        "phone_number": "+998901234567",
        "password": "SecurePass123"
    }
    response = api_client.post(url, payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert "tokens" in response.data

@pytest.mark.django_db
def test_register_existing_user(api_client, create_user):
    create_user(phone_number="+998901234567", password="Test123")
    url = reverse('register')
    response = api_client.post(url, {
        "full_name": "Duplicate User",
        "phone_number": "+998901234567",
        "password": "NewPass123"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# 2. Login
@pytest.mark.django_db
def test_user_login_success(api_client, create_user):
    user = create_user(phone_number="+998911112233", password="SecretPass1")
    url = reverse('login')
    response = api_client.post(url, {
        "phone_number": "+998911112233",
        "password": "SecretPass1"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "tokens" in response.data

@pytest.mark.django_db
def test_user_login_wrong_password(api_client, create_user):
    create_user(phone_number="+998911112233", password="SecretPass1")
    url = reverse('login')
    response = api_client.post(url, {
        "phone_number": "+998911112233",
        "password": "WrongPass"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "message" in response.data

@pytest.mark.django_db
def test_user_login_not_found(api_client):
    url = reverse('login')
    response = api_client.post(url, {
        "phone_number": "+998999999999",
        "password": "AnyPassword"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# 3. Logout
@pytest.mark.django_db
def test_logout_success(api_client, registered_user):
    url = reverse('logout')
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    response = api_client.post(url, {"refresh": registered_user["refresh"]})
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_logout_invalid_token(api_client, registered_user):
    url = reverse('logout')
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    response = api_client.post(url, {"refresh": "invalid.token.here"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# 4. Change password
@pytest.mark.django_db
def test_change_password_success(api_client, registered_user):
    url = reverse('change-password')
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    response = api_client.post(url, {
        "old_password": "StrongPassword123",
        "new_password": "NewSecurePass123"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "Password updated successfully" in response.data["detail"]

@pytest.mark.django_db
def test_change_password_wrong_old(api_client, registered_user):
    url = reverse('change-password')
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    response = api_client.post(url, {
        "old_password": "WrongOldPass",
        "new_password": "AnotherPass123"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_change_password_missing_fields(api_client, registered_user):
    url = reverse('change-password')
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    response = api_client.post(url, {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# 5. Token Refresh
@pytest.mark.django_db
def test_token_refresh_success(api_client, registered_user):
    url = reverse('token-refresh')
    response = api_client.post(url, {"refresh": registered_user["refresh"]})
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data

@pytest.mark.django_db
def test_token_refresh_invalid(api_client):
    url = reverse('token-refresh')
    response = api_client.post(url, {"refresh": "invalid.token"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
