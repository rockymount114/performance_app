# Generated by Django 4.2.11 on 2024-06-04 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0029_department_extension_granted_at"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="department",
            name="grant_ext",
        ),
    ]
