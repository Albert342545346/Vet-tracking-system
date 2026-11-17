"""ПР10: поле status (TextChoices); is_cancelled пока сохраняется."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("visits", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="visit",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Активно"),
                    ("cancelled", "Отменено"),
                    ("completed", "Завершено"),
                ],
                default="active",
                max_length=12,
                verbose_name="Статус посещения",
            ),
        ),
    ]
