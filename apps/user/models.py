from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomerUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Not found phone number!")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(phone_number, password, **extra_fields)


phone_validator = RegexValidator(
    regex=r"^\+998\d{9}$", message=_("Phone number don't match"), code='invalid'
)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class RoleType(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        OWNER = 'owner', _('Owner')
        MANAGER = 'manager', _('Manager')
        USER = 'user', _('User')

    phone_number = models.CharField(max_length=15, unique=True, validators=phone_validator)
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=RoleType, default=RoleType.USER)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomerUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number
