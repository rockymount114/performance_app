# Generated by Django 4.2 on 2024-04-15 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_alter_strategicinitiative_proposed_completion_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='measure',
            name='approved',
            field=models.BooleanField(default=False, verbose_name='Approved'),
        ),
    ]
