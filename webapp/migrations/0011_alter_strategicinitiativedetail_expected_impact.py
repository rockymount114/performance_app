# Generated by Django 4.2 on 2024-04-26 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0010_alter_profile_image_alter_profile_work_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategicinitiativedetail',
            name='expected_impact',
            field=models.TextField(blank=True, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('Moderate', 'Moderate'), ('High Impact', 'High Impact')], max_length=255, null=True),
        ),
    ]
