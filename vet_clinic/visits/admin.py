"""Административная панель для посещений и назначений (ПР10)."""
from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Prescription, Visit


class PrescriptionInline(admin.TabularInline):
    """Назначения на странице посещения."""

    model = Prescription
    extra = 0


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "animal",
        "doctor",
        "doctor_specialization",
        "visit_date",
        "status",
    )
    list_display_links = ("id",)
    list_select_related = ("animal", "doctor")
    search_fields = ("animal__name", "doctor__name", "diagnosis")
    list_filter = ("status", "visit_date", "doctor")
    date_hierarchy = "visit_date"
    ordering = ("-visit_date",)
    list_per_page = 20
    autocomplete_fields = ("animal", "doctor")
    inlines = (PrescriptionInline,)
    actions = ("cancel_visits", "complete_visits", "restore_visits")

    @admin.display(
        description="Специализация", ordering="doctor__specialization"
    )
    def doctor_specialization(self, obj):
        return obj.doctor.specialization

    @admin.action(description="Отменить выбранные посещения")
    def cancel_visits(self, request, queryset):
        count = 0
        for visit in queryset.active():
            visit.cancel()
            count += 1
        self.message_user(
            request, f"Отменено посещений: {count}.", messages.SUCCESS
        )

    @admin.action(description="Отметить завершёнными")
    def complete_visits(self, request, queryset):
        count = 0
        for visit in queryset.active():
            visit.complete()
            count += 1
        self.message_user(
            request, f"Завершено посещений: {count}.", messages.SUCCESS
        )

    @admin.action(description="Вернуть в активные")
    def restore_visits(self, request, queryset):
        restored = skipped = 0
        for visit in queryset.exclude(status=Visit.Status.ACTIVE):
            visit.status = Visit.Status.ACTIVE
            try:
                # Проверяем правило «один активный приём у врача на дату».
                visit.clean()
            except ValidationError:
                skipped += 1
                continue
            visit.save(update_fields=["status"])
            restored += 1
        self.message_user(
            request,
            f"Возвращено: {restored}; пропущено из-за занятости "
            f"врача: {skipped}.",
            messages.SUCCESS if not skipped else messages.WARNING,
        )


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "medication", "dosage", "duration", "visit")
    search_fields = ("medication",)
    list_select_related = (
        "visit__animal",
        "visit__doctor",
    )
