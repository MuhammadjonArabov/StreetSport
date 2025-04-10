import uuid
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from apps.user.models import User
from apps.user.permissions import IsAdminUser, IsOwnerUser, IsManager


class DummyObject:
    def __init__(self, owner):
        self.owner = owner


class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_user(
            phone_number=f"+99890{uuid.uuid4().int % 10000000:07d}",
            password="adminpass",
            role="admin"
        )

        self.owner_user = User.objects.create_user(
            phone_number=f"+99891{uuid.uuid4().int % 10000000:07d}",
            password="ownerpass",
            role="owner"
        )

        self.manager_user = User.objects.create_user(
            phone_number=f"+99893{uuid.uuid4().int % 10000000:07d}",
            password="managerpass",
            role="manager"
        )

    def test_is_admin_permission(self):
        request = self.factory.get("/")
        request.user = self.admin_user
        permission = IsAdminUser()
        self.assertTrue(permission.has_permission(request, None))

    def test_is_owner_user_permission(self):
        request = self.factory.get("/")
        request.user = self.owner_user
        permission = IsOwnerUser()
        self.assertTrue(permission.has_permission(request, None))

    def test_is_owner_user_object_permission(self):
        request = self.factory.get("/")
        request.user = self.owner_user
        obj = DummyObject(owner=self.owner_user)
        permission = IsOwnerUser()
        self.assertTrue(permission.has_object_permission(request, None, obj))

    def test_is_manager_permission(self):
        request = self.factory.get("/")
        request.user = self.manager_user
        permission = IsManager()
        self.assertTrue(permission.has_permission(request, None))
