"""ПР9: модель Animal (без slug, вычисляемого поля и фотографии)."""
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Animal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Кличка"),
                ),
                (
                    "species",
                    models.CharField(
                        help_text="Например: кошка, собака, попугай.",
                        max_length=50,
                        verbose_name="Вид",
                    ),
                ),
                (
                    "age",
                    models.PositiveSmallIntegerField(
                        verbose_name="Возраст (лет)"
                    ),
                ),
                (
                    "owner",
                    models.CharField(
                        max_length=150, verbose_name="Владелец"
                    ),
                ),
            ],
            options={
                "verbose_name": "Животное",
                "verbose_name_plural": "Животные",
                "ordering": ["name"],
            },
        ),
    ]
