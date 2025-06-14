# Generated by Django 5.1.1 on 2025-03-09 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shorten", "0003_clickevent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="url",
            name="long_url",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="url",
            name="short_code",
            field=models.TextField(blank=True, unique=True),
        ),
    ]
