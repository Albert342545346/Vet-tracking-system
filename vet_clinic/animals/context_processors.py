"""Контекстный процессор: общие данные для всех шаблонов (ПР10)."""
from .models import Animal


def clinic_context(request):
    """Передать название клиники и число животных в base.html."""
    return {
        "site_name": "VetClinic",
        "animals_count": Animal.objects.count(),
    }
