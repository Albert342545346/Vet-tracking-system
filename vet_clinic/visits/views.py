"""View-функции приложения visits (ПР9–ПР11: Django ORM и формы)."""
from datetime import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min, Q
from django.db.models.functions import Round
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from animals.models import Animal
from doctors.models import Doctor

from .forms import VisitFilterForm, VisitForm
from .models import Prescription, Visit

DEFAULT_MIN_VISITS = 1
PAGE_SIZE = 5

# Допустимые значения параметра sort -> поля сортировки (не передаём
# произвольный ввод пользователя в order_by()).
SORT_FIELDS = {
    "date": ("visit_date", "id"),
    "animal": ("animal__name", "id"),
    "doctor": ("doctor__name", "id"),
}


def _visit_list(request, only_active):
    """Общая логика списка посещений: фильтры, сортировка, страницы."""
    form = VisitFilterForm(request.GET or None, only_active=only_active)
    form_valid = form.is_bound and form.is_valid()
    error = None
    if form.is_bound and not form_valid:
        error = "Проверьте корректность параметров фильтрации."

    visits_qs = Visit.objects.active() if only_active else Visit.objects.all()
    sort = "date"
    if form_valid:
        data = form.cleaned_data
        if data.get("date"):
            visits_qs = visits_qs.for_date(data["date"])
        if data.get("animal"):
            visits_qs = visits_qs.filter(animal=data["animal"])
        if data.get("doctor"):
            visits_qs = visits_qs.filter(doctor=data["doctor"])
        if data.get("specialization"):
            visits_qs = visits_qs.filter(
                doctor__specialization=data["specialization"]
            )
        if data.get("status"):
            visits_qs = visits_qs.filter(status=data["status"])
        sort = data.get("sort") or "date"

    visits_qs = (
        visits_qs.annotate(
            animal_name=F("animal__name"),
            doctor_name=F("doctor__name"),
        )
        .order_by(*SORT_FIELDS.get(sort, SORT_FIELDS["date"]))
        .values(
            "id",
            "visit_date",
            "diagnosis",
            "status",
            "animal_id",
            "animal_name",
            "doctor_id",
            "doctor_name",
        )
    )
    paginator = Paginator(visits_qs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "visits": page_obj,
        "page_obj": page_obj,
        "form": form,
        "error": error,
        "only_active": only_active,
    }
    return render(request, "visits/visit_list.html", context)


def visits(request):
    """Страница /visits/: все посещения (включая историю)."""
    return _visit_list(request, only_active=False)


def active_visits(request):
    """Страница /visits/active/: только активные посещения."""
    return _visit_list(request, only_active=True)


def visit_detail(request, visit_id):
    """Страница /visits/<id>/: данные посещения и назначения."""
    visit = get_object_or_404(
        Visit.objects.select_related("animal", "doctor"),
        pk=visit_id,
    )
    prescriptions = visit.prescriptions.all()
    doctor_busy_today = (
        Visit.objects.active()
        .for_date(timezone.localdate())
        .filter(doctor=visit.doctor)
        .exists()
    )
    context = {
        "visit": visit,
        "prescriptions": prescriptions,
        "doctor_available": not doctor_busy_today,
    }
    return render(request, "visits/visit_detail.html", context)


def available_doctors(request):
    """Страница /visits/available/?date=...: свободные врачи на дату."""
    visit_date = request.GET.get("date", "").strip()
    doctors_list = []
    error = ""
    searched = False

    if visit_date:
        try:
            selected = datetime.strptime(visit_date, "%Y-%m-%d").date()
        except ValueError:
            error = "Введите дату в формате ГГГГ-ММ-ДД."
        else:
            busy_ids = (
                Visit.objects.active()
                .for_date(selected)
                .values_list("doctor_id", flat=True)
            )
            doctors_list = Doctor.objects.exclude(
                pk__in=busy_ids
            ).order_by("name")
            searched = True

    context = {
        "doctors": doctors_list,
        "visit_date": visit_date,
        "error": error,
        "searched": searched,
    }
    return render(request, "visits/available.html", context)


def _parse_min_visits(value):
    """Преобразовать порог из параметра URL в целое число >= 1."""
    try:
        return max(int(value), 1)
    except (TypeError, ValueError):
        return DEFAULT_MIN_VISITS


def statistics(request):
    """Страница /visits/statistics/: сводные показатели клиники."""
    min_visits = _parse_min_visits(request.GET.get("min"))

    active_filter = Q(visits__status=Visit.Status.ACTIVE)
    doctors_with_counts = Doctor.objects.annotate(
        visits_count=Count("visits", filter=active_filter),
        doctor_name=F("name"),
    )

    context = {
        "active_count": Visit.objects.active().count(),
        "cancelled_count": Visit.objects.cancelled().count(),
        "completed_count": Visit.objects.completed().count(),
        "age_stats": Animal.objects.aggregate(
            animals_count=Count("id"),
            avg_age=Round(Avg("age"), 1),
            min_age=Min("age"),
            max_age=Max("age"),
        ),
        "species_stats": (
            Animal.objects.values("species")
            .annotate(
                animals_count=Count("id"),
                avg_age=Round(Avg("age"), 1),
            )
            .order_by("-animals_count", "species")
        ),
        "doctor_stats": (
            doctors_with_counts.values(
                "doctor_name", "specialization", "visits_count"
            ).order_by("-visits_count", "name")
        ),
        "busy_doctors": (
            doctors_with_counts.filter(visits_count__gte=min_visits)
            .values("doctor_name", "visits_count")
            .order_by("-visits_count", "name")
        ),
        "specialization_stats": (
            Visit.objects.active()
            .values("doctor__specialization")
            .annotate(visits_count=Count("id"))
            .order_by("-visits_count", "doctor__specialization")
        ),
        "medication_stats": (
            Prescription.objects.values("medication")
            .annotate(prescriptions_count=Count("id"))
            .order_by("-prescriptions_count", "medication")[:5]
        ),
        "min_visits": min_visits,
    }
    return render(request, "visits/statistics.html", context)


def visit_create(request):
    """Страница /visits/create/: новое посещение."""
    if request.method == "POST":
        form = VisitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Посещение создано.")
            return redirect("visits:list")
    else:
        form = VisitForm(initial={"visit_date": timezone.localdate()})
    return render(request, "visits/visit_form.html", {"form": form})


def visit_update(request, visit_id):
    """Страница /visits/<id>/edit/: редактирование активного посещения."""
    visit = get_object_or_404(Visit.objects.active(), pk=visit_id)
    if request.method == "POST":
        form = VisitForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()
            messages.success(request, "Изменения сохранены.")
            return redirect("visits:list")
    else:
        form = VisitForm(instance=visit)
    context = {"form": form, "visit": visit}
    return render(request, "visits/visit_form.html", context)


@require_POST
def visit_cancel(request, visit_id):
    """Отмена активного посещения (запись остаётся в базе)."""
    visit = get_object_or_404(Visit.objects.active(), pk=visit_id)
    visit.cancel()
    messages.warning(request, f"Посещение №{visit.pk} отменено.")
    return redirect("visits:list")
