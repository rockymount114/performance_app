# Generated by Django 4.2.11 on 2024-05-31 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0025_remove_objective_focusarea_objective_focus_area"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="focusarea",
            name="approved",
        ),
        migrations.RemoveField(
            model_name="focusarea",
            name="department",
        ),
        migrations.RemoveField(
            model_name="focusarea",
            name="fiscal_year",
        ),
    ]
