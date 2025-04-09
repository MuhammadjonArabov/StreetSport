from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomerUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
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
    regex=r"^\+998\d{9}$", message=_("Phone number format should be +998 followed by 9 digits"), code='invalid'
)

class User(AbstractBaseUser, PermissionsMixin):
    REQUIRED_FIELDS = []
    email = None
    username = None

    class RoleType(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        OWNER = 'owner', _('Owner')
        MANAGER = 'manager', _('Manager')
        USER = 'user', _('User')

    phone_number = models.CharField(max_length=15, unique=True, validators=[phone_validator])
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=10, choices=RoleType.choices, default=RoleType.USER)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = CustomerUserManager()

    USERNAME_FIELD = "phone_number"

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
    )

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def __str__(self):
        return self.phone_number
