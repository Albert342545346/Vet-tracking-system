"""ПР9: модель Doctor."""
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Doctor",
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
                    models.CharField(
                        max_length=150, verbose_name="ФИО врача"
                    ),
                ),
                (
                    "specialization",
                    models.CharField(
                        help_text=(
                            "Например: терапевт, хирург, дерматолог."
                        ),
                        max_length=100,
                        verbose_name="Специализация",
                    ),
                ),
            ],
            options={
                "verbose_name": "Врач",
                "verbose_name_plural": "Врачи",
                "ordering": ["name"],
            },
        ),
    ]
