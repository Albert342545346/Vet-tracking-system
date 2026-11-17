"""ПР10: заполнение slug у уже существующих животных."""
from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_animal_slugs(apps, schema_editor):
    """Сформировать slug вида «barsik-1» (латиница + первичный ключ)."""
    Animal = apps.get_model("animals", "Animal")
    for animal in Animal.objects.all().order_by("pk"):
        base_slug = slugify(unidecode(animal.name)) or "animal"
        animal.slug = f"{base_slug}-{animal.pk}"
        animal.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("animals", "0002_animal_slug"),
    ]

    operations = [
        migrations.RunPython(
            populate_animal_slugs,
            migrations.RunPython.noop,
        ),
    ]
