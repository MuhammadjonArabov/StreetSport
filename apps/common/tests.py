import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from apps.user.models import User
from apps.common import models as stadium_models
from django.utils import timezone
timedelta = timezone.timedelta

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def owner_user(db):
    return User.objects.create_user(phone_number="998911112233", password="test1234", role="owner")

@pytest.fixture
def manager_user(db):
    return User.objects.create_user(phone_number="998933334455", password="test1234", role="manager")

@pytest.fixture
def auth_client(api_client, owner_user):
    api_client.force_authenticate(user=owner_user)
    return api_client

@pytest.fixture
def stadium(owner_user):
    return stadium_models.Stadium.objects.create(
        name="Test Stadium",
        latitude=41.3111,
        longitude=69.2797,
        price_hour=100000,
        owner=owner_user
    )


def test_create_stadium(auth_client):
    url = reverse("stadium-list")
    data = {
        "name": "New Stadium",
        "latitude": 41.0,
        "longitude": 69.0,
        "description": "Test description",
        "price_hour": "150000.00",
        "is_active": True
    }
    response = auth_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


def test_stadium_list(api_client, stadium):
    url = reverse("stadium-list")
    api_client.force_authenticate(user=stadium.owner)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert any([s['name'] == stadium.name for s in response.data])


def test_bron_create(auth_client, stadium):
    url = reverse("bron-create")
    now = timezone.now()
    data = {
        "stadium": stadium.id,
        "start_time": (now + timedelta(hours=2)).isoformat(),
        "end_time": (now + timedelta(hours=3)).isoformat(),
        "order_type": "cash",
        "is_team": False
    }
    response = auth_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


def test_bron_update_status(manager_user, stadium):
    bron = stadium_models.Bron.objects.create(
        user=stadium.owner,
        stadium=stadium,
        start_time=timezone.now() + timedelta(hours=5),
        end_time=timezone.now() + timedelta(hours=6),
        order_type="cash",
    )
    client = APIClient()
    client.force_authenticate(user=manager_user)
    url = reverse("bron-update", kwargs={"pk": bron.pk})
    response = client.patch(url, {"is_paid": True}, format="json")
    assert response.status_code == status.HTTP_200_OK
    bron.refresh_from_db()
    assert bron.is_paid is True


def test_owner_bron_list(auth_client, stadium):
    stadium_models.Bron.objects.create(
        user=stadium.owner,
        stadium=stadium,
        start_time=timezone.now() + timedelta(hours=1),
        end_time=timezone.now() + timedelta(hours=2),
        order_type="cash"
    )
    url = reverse("owner-bron-list")
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1


def test_owner_stadium_stats(auth_client, stadium):
    stadium_models.Bron.objects.create(
        user=stadium.owner,
        stadium=stadium,
        start_time=timezone.now() + timedelta(hours=1),
        end_time=timezone.now() + timedelta(hours=2),
        order_type="cash",
        is_paid=True
    )
    url = reverse("owner-stadium-statistic")
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['total_income'] is not None


def test_stadium_status_count(admin_user, stadium):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    url = reverse("status-count")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "total_stadiums" in response.data
