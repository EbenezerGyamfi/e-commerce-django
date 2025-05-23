# Generated by Django 5.1.7 on 2025-03-25 06:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0006_remove_product_model_remove_product_modified_date_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Variation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "variation_category",
                    models.CharField(
                        choices=[("color", "color"), ("size", "size")], max_length=100
                    ),
                ),
                ("variation_value", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="store.product"
                    ),
                ),
            ],
        ),
    ]
