# Generated by Django 3.2.23 on 2024-01-15 06:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_tag"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(to="core.Tag"),
        ),
    ]
