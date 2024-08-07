# Generated by Django 4.2.11 on 2024-07-30 10:15

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0038_alter_measure_target_number_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="measure",
            name="current_year_rate",
            field=models.DecimalField(
                decimal_places=0, default=Decimal("0"), max_digits=15
            ),
        ),
    ]
