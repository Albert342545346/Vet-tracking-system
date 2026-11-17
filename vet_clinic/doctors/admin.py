"""Административная панель для врачей (ПР10)."""
from django.contrib import admin
from django.db.models import Count, Q

from visits.models import Visit

from .models import Doctor


class DoctorVisitInline(admin.TabularInline):
    """Посещения врача на странице врача."""

    model = Visit
    fields = ("animal", "visit_date", "status")
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "specialization",
        "active_visits_count",
    )
    list_display_links = ("name",)
    search_fields = ("name", "specialization")
    list_filter = ("specialization",)
    ordering = ("name",)
    list_per_page = 20
    inlines = (DoctorVisitInline,)

    def get_queryset(self, request):
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
