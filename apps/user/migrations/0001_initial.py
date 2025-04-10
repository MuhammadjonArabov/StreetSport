# Generated by Django 5.1.4 on 2025-04-08 14:00

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        max_length=15,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message="Phone number format should be +998 followed by 9 digits",
                                regex="^\\+998\\d{9}$",
                            )
                        ],
                    ),
                ),
                ("full_name", models.CharField(blank=True, max_length=255)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("owner", "Owner"),
                            ("manager", "Manager"),
                            ("user", "User"),
                        ],
                        default="user",
                        max_length=10,
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True, related_name="customuser_set", to="auth.group"
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True, related_name="customuser_set", to="auth.permission"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
