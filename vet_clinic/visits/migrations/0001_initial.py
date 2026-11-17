"""ПР9: модели Visit (с признаком is_cancelled) и Prescription."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("animals", "0001_initial"),
        ("doctors", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Visit",
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
                    "visit_date",
                    models.DateField(verbose_name="Дата посещения"),
                ),
                (
                    "diagnosis",
                    models.CharField(
                        blank=True,
                        help_text="Можно оставить пустым до приёма.",
                        max_length=255,
                        verbose_name="Диагноз",
                    ),
                ),
                (
                    "is_cancelled",
                    models.BooleanField(
                        default=False,
                        verbose_name="Посещение отменено",
                    ),
                ),
                (
                    "animal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="visits",
                        to="animals.animal",
                        verbose_name="Животное",
                    ),
                ),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="visits",
                        to="doctors.doctor",
                        verbose_name="Врач",
                    ),
                ),
            ],
            options={
                "verbose_name": "Посещение",
                "verbose_name_plural": "Посещения",
                "ordering": ["visit_date", "pk"],
            },
        ),
        migrations.CreateModel(
            name="Prescription",
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
                    "medication",
                    models.CharField(
                        max_length=100, verbose_name="Препарат"
                    ),
                ),
                (
                    "dosage",
                    models.CharField(
                        max_length=100, verbose_name="Дозировка"
                    ),
                ),
                (
                    "duration",
                    models.CharField(
                        max_length=50, verbose_name="Длительность"
                    ),
                ),
                (
                    "visit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prescriptions",
                        to="visits.visit",
                        verbose_name="Посещение",
                    ),
                ),
            ],
            options={
                "verbose_name": "Назначение",
                "verbose_name_plural": "Назначения",
                "ordering": ["pk"],
            },
        ),
    ]
