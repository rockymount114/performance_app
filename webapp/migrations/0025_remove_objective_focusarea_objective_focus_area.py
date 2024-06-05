# Generated by Django 4.2.11 on 2024-05-24 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0024_alter_objective_focusarea'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='objective',
            name='focusarea',
        ),
        migrations.AddField(
            model_name='objective',
            name='focus_area',
            field=models.ManyToManyField(to='webapp.focusarea'),
        ),
    ]