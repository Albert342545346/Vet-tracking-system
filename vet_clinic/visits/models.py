"""Модели посещения и назначения (ПР9–ПР10)."""
from django.core.exceptions import ValidationError
from django.db import models

from animals.models import Animal
from doctors.models import Doctor


class VisitQuerySet(models.QuerySet):
    """Набор запросов для работы с посещениями."""

    def active(self):
        """Только активные посещения."""
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        """Только отменённые посещения."""
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        """Только завершённые посещения."""
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, selected_date):
        """Посещения на указанную дату (объект datetime.date)."""
        return self.filter(visit_date=selected_date)


class VisitManager(models.Manager.from_queryset(VisitQuerySet)):
    """Менеджер посещений: objects.all() возвращает и историю."""


class Visit(models.Model):
    """Посещение клиники: животное приходит к врачу на дату."""

    class Status(models.TextChoices):
        """Состояние посещения."""

        ACTIVE = "active", "Активно"
        CANCELLED = "cancelled", "Отменено"
        COMPLETED = "completed", "Завершено"

    animal = models.ForeignKey(
        Animal,
        on_delete=models.PROTECT,
        related_name="visits",
        verbose_name="Животное",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.PROTECT,
        related_name="visits",
        verbose_name="Врач",
    )
    visit_date = models.DateField(
        verbose_name="Дата посещения",
    )
    diagnosis = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Диагноз",
        help_text="Можно оставить пустым до приёма.",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус посещения",
    )

    objects = VisitManager()

    class Meta:
        ordering = ["visit_date", "pk"]
        verbose_name = "Посещение"
        verbose_name_plural = "Посещения"

    def __str__(self):
        return f"{self.animal} — {self.doctor}, {self.visit_date}"

    @property
    def is_active(self):
        """Посещение активно (блокирует врача на дату)."""
        return self.status == self.Status.ACTIVE

    def clean(self):
        """Правило предметной области: у врача одно активное посещение
        на дату. Отменённые и завершённые посещения врача не блокируют.
        """
        super().clean()
        if self.status != self.Status.ACTIVE:
            return
        if not self.doctor_id or not self.visit_date:
            return
        conflicts = Visit.objects.active().filter(
            doctor_id=self.doctor_id,
            visit_date=self.visit_date,
        )
        if self.pk:
            conflicts = conflicts.exclude(pk=self.pk)
        if conflicts.exists():
            raise ValidationError(
                "У выбранного врача уже есть активное посещение "
                "на эту дату."
            )

    def cancel(self):
        """Отменить посещение (запись остаётся в базе)."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def complete(self):
        """Отметить посещение завершённым."""
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status"])


class Prescription(models.Model):
    """Назначение (лечение) в составе посещения."""

    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name="prescriptions",
        verbose_name="Посещение",
    )
    medication = models.CharField(
        max_length=100,
        verbose_name="Препарат",
    )
    dosage = models.CharField(
        max_length=100,
        verbose_name="Дозировка",
    )
    duration = models.CharField(
        max_length=50,
        verbose_name="Длительность",
    )

    class Meta:
        ordering = ["pk"]
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"

    def __str__(self):
        return f"{self.medication} ({self.dosage})"
