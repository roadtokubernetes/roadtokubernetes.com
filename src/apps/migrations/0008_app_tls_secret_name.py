# Generated by Django 4.1.2 on 2022-11-02 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0007_appenvvariable_appsecretvariable_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="app",
            name="tls_secret_name",
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
