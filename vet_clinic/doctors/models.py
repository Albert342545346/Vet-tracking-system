"""Модель врача (ПР9)."""
from django.db import models


class Doctor(models.Model):
    """Ветеринарный врач клиники."""

    name = models.CharField(
        max_length=150,
        verbose_name="ФИО врача",
    )
    specialization = models.CharField(
        max_length=100,
        verbose_name="Специализация",
        help_text="Например: терапевт, хирург, дерматолог.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"

    def __str__(self):
        return self.name
