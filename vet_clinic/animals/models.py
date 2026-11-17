"""Модель животного (ПР9–ПР11)."""
from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode

# Возраст (лет), начиная с которого животное считается пожилым.
SENIOR_AGE = 8


class Animal(models.Model):
    """Животное, состоящее на учёте в клинике."""

    name = models.CharField(
        max_length=100,
        verbose_name="Кличка",
    )
    species = models.CharField(
        max_length=50,
        verbose_name="Вид",
        help_text="Например: кошка, собака, попугай.",
    )
    age = models.PositiveSmallIntegerField(
        verbose_name="Возраст (лет)",
    )
    owner = models.CharField(
        max_length=150,
        verbose_name="Владелец",
    )
    # Фотография хранится в MEDIA_ROOT/animals/ (ПР11).
    photo = models.ImageField(
        upload_to="animals/",
        blank=True,
        null=True,
        verbose_name="Фотография",
    )
    # Адрес страницы животного: латиница + первичный ключ (ПР10).
    slug = models.SlugField(
        max_length=180,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )
    # Вычисляемое поле: значение считает сама база данных (ПР10).
    is_senior = models.GeneratedField(
        expression=Case(
            When(age__gte=SENIOR_AGE, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Пожилое животное",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Животное"
        verbose_name_plural = "Животные"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Сохранить животное; slug формируется один раз при создании."""
        if not self.slug:
            base_slug = slugify(unidecode(self.name)) or "animal"
            if self.pk:
                self.slug = f"{base_slug}-{self.pk}"
            else:
                # Первичного ключа ещё нет: сначала сохраняем объект,
                # затем дописываем идентификатор к slug.
                super().save(*args, **kwargs)
                self.slug = f"{base_slug}-{self.pk}"
                super().save(
                    update_fields=["slug"],
                    using=kwargs.get("using"),
                )
                return
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Адрес страницы животного, например /animals/barsik-1/."""
        return reverse("animals:detail", kwargs={"slug": self.slug})
