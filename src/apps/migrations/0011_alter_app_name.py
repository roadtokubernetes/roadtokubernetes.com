# Generated by Django 4.1.2 on 2022-11-02 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0010_rename_label_app_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="app",
            name="name",
            field=models.CharField(blank=True, default="sample", max_length=120),
            preserve_default=False,
        ),
    ]