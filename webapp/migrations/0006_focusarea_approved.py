# Generated by Django 4.2 on 2024-04-15 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_measure_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='focusarea',
            name='approved',
            field=models.BooleanField(default=False, verbose_name='Approved'),
        ),
    ]
