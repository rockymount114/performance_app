# Generated by Django 4.2.11 on 2024-05-06 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0018_alter_profile_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]