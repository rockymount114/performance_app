# Generated by Django 4.2.11 on 2024-07-26 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0034_remove_department_created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="department",
            name="extension_duration",
            field=models.IntegerField(default=0),
        ),
    ]
