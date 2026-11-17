"""ПР11: поле фотографии животного."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("animals", "0005_animal_is_senior"),
    ]

    operations = [
        migrations.AddField(
            model_name="animal",
            name="photo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="animals/",
                verbose_name="Фотография",
            ),
        ),
    ]
