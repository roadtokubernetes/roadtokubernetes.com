# Generated by Django 4.1.2 on 2022-10-17 18:51

from django.db import migrations, models
import profiles.utils


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0002_profile_timestamp_profile_updated"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=profiles.utils.get_profile_storage,
                upload_to=profiles.utils.get_profile_image_upload_to,
            ),
        ),
    ]