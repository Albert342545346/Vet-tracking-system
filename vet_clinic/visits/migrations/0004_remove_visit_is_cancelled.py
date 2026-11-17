"""ПР10: поле is_cancelled удалено, состояние хранит status."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("visits", "0003_migrate_visit_statuses"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="visit",
            name="is_cancelled",
        ),
    ]
