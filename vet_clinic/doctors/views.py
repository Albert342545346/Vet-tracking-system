"""View-функции приложения doctors (ПР9: Django ORM)."""
from django.db.models import Count, Q
from django.shortcuts import render

from vetclinic.sqlite_functions import PyLower
from visits.models import Visit

from .models import Doctor


def doctors(request):
    """Страница /doctors/: врачи и число их активных посещений."""
    specialization = request.GET.get("spec", "").strip()
    query = request.GET.get("q", "").strip()

    doctors_list = Doctor.objects.annotate(
        active_visits=Count(
            "visits",
            filter=Q(visits__status=Visit.Status.ACTIVE),
        )
    )
    if query:
        needle = query.lower()
        doctors_list = doctors_list.annotate(
            name_lower=PyLower("name"),
            spec_lower=PyLower("specialization"),
        ).filter(
            Q(name_lower__contains=needle)
            | Q(spec_lower__contains=needle)
        )
    if specialization:
        doctors_list = doctors_list.filter(
            specialization=specialization
        )

    specializations = (
        Doctor.objects.order_by("specialization")
        .values_list("specialization", flat=True)
        .distinct()
    )

    context = {
        "doctors": doctors_list,
        "specializations": specializations,
        "specialization": specialization,
        "query": query,
    }
    return render(request, "doctors/doctor_list.html", context)
