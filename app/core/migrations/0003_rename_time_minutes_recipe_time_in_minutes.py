# Generated by Django 3.2.23 on 2024-01-14 11:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_recipe"),
    ]

    operations = [
        migrations.RenameField(
            model_name="recipe",
            old_name="time_in_minutes",
            new_name="time_in_minutes",
        ),
    ]
