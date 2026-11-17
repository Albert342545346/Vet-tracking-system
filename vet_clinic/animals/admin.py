"""Административная панель для животных (ПР10)."""
from django.contrib import admin, messages
from django.db.models import Count, F, Q

from visits.models import Visit

from .models import Animal


class AnimalVisitInline(admin.TabularInline):
    """Посещения животного на странице животного."""

    model = Visit
    fields = ("doctor", "visit_date", "status")
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "species",
        "age",
        "owner",
        "is_senior",
        "active_visits_count",
    )
    list_display_links = ("name",)
    list_editable = ("age",)
    search_fields = ("name", "owner", "species")
    list_filter = ("species", "is_senior")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id", "slug", "is_senior")
    inlines = (AnimalVisitInline,)
    actions = ("add_year",)

    def get_queryset(self, request):
        """Число активных посещений считается одним запросом."""
        return super().get_queryset(request).annotate(
            active_visits=Count(
                "visits",
                filter=Q(visits__status=Visit.Status.ACTIVE),
            )
        )

    @admin.display(
        description="Активных посещений", ordering="active_visits"
    )
    def active_visits_count(self, obj):
        return obj.active_visits

    @admin.action(description="Увеличить возраст на 1 год")
    def add_year(self, request, queryset):
        updated = queryset.update(age=F("age") + 1)
        self.message_user(
            request,
            f"Возраст увеличен у животных: {updated}.",
            messages.SUCCESS,
        )
