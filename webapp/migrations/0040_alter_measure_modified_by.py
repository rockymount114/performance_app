# Generated by Django 4.2.11 on 2024-07-31 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0039_alter_measure_current_year_rate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="measure",
            name="modified_by",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
