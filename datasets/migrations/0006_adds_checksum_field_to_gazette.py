# Generated by Django 3.0.3 on 2020-03-30 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0005_auto_20200327_1348"),
    ]

    operations = [
        migrations.AddField(
            model_name="gazette",
            name="checksum",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
