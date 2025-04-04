# Generated by Django 5.1.7 on 2025-03-23 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_product_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="model",
            field=models.CharField(
                choices=[("S", "Small"), ("M", "Medium"), ("L", "Large")],
                default="S",
                max_length=1,
            ),
        ),
    ]
