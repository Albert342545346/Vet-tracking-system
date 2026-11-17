"""Формы приложения visits (ПР11)."""
from django import forms
from django.utils import timezone

from animals.models import Animal
from doctors.models import Doctor

from .models import Visit

SORT_CHOICES = [
    ("date", "По дате"),
    ("animal", "По животному"),
    ("doctor", "По врачу"),
]


class VisitFilterForm(forms.Form):
    """Фильтры и сортировка списка посещений (GET-параметры)."""

    date = forms.DateField(
        required=False,
        label="Дата",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
    )
    animal = forms.ModelChoiceField(
        queryset=Animal.objects.order_by("name"),
        required=False,
        label="Животное",
        empty_label="Все животные",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.order_by("name"),
        required=False,
        label="Врач",
        empty_label="Все врачи",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    specialization = forms.ChoiceField(
        required=False,
        label="Специализация врача",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        required=False,
        label="Статус",
        choices=[("", "Все статусы")] + Visit.Status.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        required=False,
        label="Сортировка",
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, only_active=False, **kwargs):
        super().__init__(*args, **kwargs)
        specs = (
            Doctor.objects.order_by("specialization")
            .values_list("specialization", flat=True)
            .distinct()
        )
        self.fields["specialization"].choices = [
            ("", "Все специализации")
        ] + [(spec, spec) for spec in specs]
        if only_active:
            # На странице «Только активные» фильтр по статусу не нужен.
            del self.fields["status"]


class VisitForm(forms.ModelForm):
    """Создание и редактирование посещения.

    Статус в форму не входит: новое посещение всегда активно.
    Правило «у врача одно активное посещение на дату» проверяет
    Visit.clean(), которое вызывается при is_valid().
    """

    class Meta:
        model = Visit
        fields = ["animal", "doctor", "visit_date", "diagnosis"]
        widgets = {
            "animal": forms.Select(attrs={"class": "form-select"}),
            "doctor": forms.Select(attrs={"class": "form-select"}),
            # format нужен, чтобы <input type="date"> получил ISO-дату.
            "visit_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date", "class": "form-control"},
            ),
            "diagnosis": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }
        help_texts = {
            "visit_date": "Нельзя выбрать прошедшую дату.",
        }

    def clean_visit_date(self):
        """Новую или изменённую дату нельзя ставить в прошлое."""
        visit_date = self.cleaned_data["visit_date"]
        changed = (
            self.instance.pk is None
            or visit_date != self.instance.visit_date
        )
        if changed and visit_date < timezone.localdate():
            raise forms.ValidationError(
                "Нельзя назначить посещение на прошедшую дату."
            )
        return visit_date
