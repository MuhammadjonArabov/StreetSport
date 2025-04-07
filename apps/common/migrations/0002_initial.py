# Generated by Django 5.1.4 on 2025-04-07 12:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("common", "0001_initial"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="bron",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bron_user",
                to="user.customuser",
            ),
        ),
        migrations.AddField(
            model_name="stadium",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="stadium_manager",
                to="user.customuser",
            ),
        ),
        migrations.AddField(
            model_name="stadium",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="stadium_owner",
                to="user.customuser",
            ),
        ),
        migrations.AddField(
            model_name="bron",
            name="stadium",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bron_stadium",
                to="common.stadium",
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="members",
            field=models.ManyToManyField(
                blank=True, related_name="team_members", to="user.customuser"
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="user.customuser"
            ),
        ),
        migrations.AddField(
            model_name="bron",
            name="team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bron_team",
                to="common.team",
            ),
        ),
        migrations.AddConstraint(
            model_name="bron",
            constraint=models.UniqueConstraint(
                fields=("stadium", "start_time", "end_time"),
                name="unique_bron_per_time",
            ),
        ),
    ]
