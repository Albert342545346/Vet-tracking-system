"""View-функции приложения homepage (ПР6: на основе шаблонов)."""
from django.shortcuts import render


def index(request):
    """Главная страница: описание системы и ссылки на разделы."""
    return render(
        request,
        "homepage/index.html",
    )


def page_not_found(request, exception):
    """Собственная страница ошибки 404 (handler404)."""
    return render(
        request,
        "404.html",
        status=404,
    )
