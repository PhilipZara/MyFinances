# Generated by Django 5.0.2 on 2024-02-25 11:42

from django.db import migrations, models

import backend.models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0021_alter_verificationcodes_expiry_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="loginlog",
            name="service",
            field=models.CharField(choices=[("manual", "Manual"), ("magic_link", "Magic Link")], default="manual", max_length=14),
        ),
        migrations.AlterField(
            model_name="verificationcodes",
            name="expiry",
            field=models.DateTimeField(default=backend.core.models.add_3hrs_from_now),
        ),
        migrations.AlterField(
            model_name="verificationcodes",
            name="token",
            field=models.TextField(default=backend.core.models.RandomCode, editable=False),
        ),
    ]
