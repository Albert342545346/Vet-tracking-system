"""ПР10: вычисляемое поле is_senior (GeneratedField)."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("animals", "0004_alter_animal_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="animal",
            name="is_senior",
            field=models.GeneratedField(
                db_persist=True,
                expression=models.Case(
                    models.When(age__gte=8, then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                ),
                output_field=models.BooleanField(),
                verbose_name="Пожилое животное",
            ),
        ),
    ]
