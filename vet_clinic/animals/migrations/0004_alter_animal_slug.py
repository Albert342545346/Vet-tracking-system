"""ПР10: slug стал уникальным (все значения уже заполнены)."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("animals", "0003_populate_animal_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="animal",
            name="slug",
            field=models.SlugField(
                editable=False,
                max_length=180,
                unique=True,
                verbose_name="URL-идентификатор",
            ),
        ),
    ]
