"""ПР10: перенос is_cancelled -> status."""
from django.db import migrations


def migrate_visit_statuses(apps, schema_editor):
    """Отменённые посещения получают статус cancelled."""
    Visit = apps.get_model("visits", "Visit")
    Visit.objects.filter(is_cancelled=True).update(status="cancelled")
    Visit.objects.filter(is_cancelled=False).update(status="active")


def reverse_visit_statuses(apps, schema_editor):
    """Откат: восстановить булев признак из статуса."""
    Visit = apps.get_model("visits", "Visit")
    Visit.objects.filter(status="cancelled").update(is_cancelled=True)
    Visit.objects.exclude(status="cancelled").update(is_cancelled=False)


class Migration(migrations.Migration):

    dependencies = [
        ("visits", "0002_visit_status"),
    ]

    operations = [
        migrations.RunPython(
            migrate_visit_statuses,
            reverse_visit_statuses,
        ),
    ]
