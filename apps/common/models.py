from django.db import models
from apps.user.models import CustomUser
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        abstract = True


class Team(BaseModel):
    name = models.CharField(max_length=225)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    members = models.ForeignKey(CustomUser, related_name="team_members")

    def __str__(self):
        return self.name


class Stadium(BaseModel):
    name = models.CharField(max_length=225)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True)
    price_hour = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="stadium_owner")
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="stadium_manager")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Bron(BaseModel):
    class ProviderType(models.TextChoices):
        CLICK = 'click', _('Click')
        PAYME = 'payme', _('Payme')
        CASH = 'cash', _('Cash')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bron_user")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="bron_team")
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name="bron_stadium")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    order_type = models.CharField(
        max_length=25,
        choices=ProviderType.choices, default=ProviderType.CASH
    )

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bron"
        constraints = [
            models.UniqueConstraint(
                fields=['stadium', 'start_time', 'end_time'],
                name='unique_bron_per_time'
            )
        ]

    def __str__(self):
        return f"{self.stadium.name} | {self.start_time}-{self.end_time}"


