"""ПР10: добавлено поле slug (пока без ограничения уникальности)."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("animals", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="animal",
            name="slug",
            field=models.SlugField(
                blank=True,
                editable=False,
                max_length=180,
                verbose_name="URL-идентификатор",
            ),
        ),
    ]
