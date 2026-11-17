"""View-функции приложения animals (ПР9–ПР11: Django ORM)."""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from vetclinic.sqlite_functions import PyLower

from .forms import AnimalForm
from .models import Animal


def animals(request):
    """Страница /animals/: список, поиск по кличке и владельцу, вид."""
    query = request.GET.get("q", "").strip()
    species = request.GET.get("species", "").strip()

    animals_list = Animal.objects.all()
    if query:
        needle = query.lower()
        animals_list = animals_list.annotate(
            name_lower=PyLower("name"),
            owner_lower=PyLower("owner"),
        ).filter(
            Q(name_lower__contains=needle)
            | Q(owner_lower__contains=needle)
        )
    if species:
        animals_list = animals_list.filter(species=species)

    species_list = (
        Animal.objects.order_by("species")
        .values_list("species", flat=True)
        .distinct()
    )

    context = {
        "animals": animals_list,
        "species_list": species_list,
        "query": query,
        "species": species,
    }
    return render(request, "animals/animal_list.html", context)


def animal_detail(request, slug):
    """Страница /animals/<slug>/: животное и история посещений."""
    animal = get_object_or_404(Animal, slug=slug)
    animal_visits = animal.visits.select_related("doctor").order_by(
        "-visit_date", "-pk"
    )
    context = {
        "animal": animal,
        "visits": animal_visits,
    }
    return render(request, "animals/animal_detail.html", context)


def animal_create(request):
    """Страница /animals/create/: новое животное с фотографией."""
    if request.method == "POST":
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save()
            messages.success(request, f"Животное «{animal}» добавлено.")
            return redirect(animal.get_absolute_url())
    else:
        form = AnimalForm()
    return render(request, "animals/animal_form.html", {"form": form})
