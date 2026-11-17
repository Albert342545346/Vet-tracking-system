"""Маршрутизация верхнего уровня проекта vetclinic."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("animals/", include("animals.urls")),
    path("doctors/", include("doctors.urls")),
    path("visits/", include("visits.urls")),
]

if settings.DEBUG:
    # ПР11: раздача загруженных файлов в режиме разработки.
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    # ПР10: панель отладки (если подключена в settings.py).
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("__debug__/", include("debug_toolbar.urls")),
        ]

handler404 = "homepage.views.page_not_found"
