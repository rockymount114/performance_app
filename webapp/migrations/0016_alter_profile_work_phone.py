# Generated by Django 4.2.11 on 2024-04-30 16:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0015_alter_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='work_phone',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[django.core.validators.RegexValidator(message='Work phone number must be entered in the format: xxx-xxx-xxxx.', regex='^\\d{3}-\\d{3}-\\d{4}$')]),
        ),
    ]
