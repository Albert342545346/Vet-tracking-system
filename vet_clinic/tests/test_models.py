"""Тесты моделей Django: slug, вычисляемое поле, менеджер, правила."""
from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

pytestmark = pytest.mark.django_db


def test_slug_is_built_from_transliterated_name(clinic):
    assert clinic.barsik.slug == f"barsik-{clinic.barsik.pk}"


def test_slug_fallback_for_name_without_letters(db):
    from animals.models import Animal

    animal = Animal.objects.create(
        name="???", species="кошка", age=1, owner="Тест Т.Т.")
    assert animal.slug == f"animal-{animal.pk}"


def test_slug_does_not_change_on_rename(clinic):
    old_slug = clinic.barsik.slug
    clinic.barsik.name = "Другое имя"
    clinic.barsik.save()
    clinic.barsik.refresh_from_db()
    assert clinic.barsik.slug == old_slug


def test_slug_is_unique_for_same_names(db):
    from animals.models import Animal

    first = Animal.objects.create(
        name="Шарик", species="собака", age=1, owner="А")
    second = Animal.objects.create(
        name="Шарик", species="собака", age=2, owner="Б")
    assert first.slug != second.slug


def test_get_absolute_url(clinic):
    assert clinic.rex.get_absolute_url() == (
        f"/animals/rex-{clinic.rex.pk}/"
    )


def test_is_senior_generated_by_database(db):
    from animals.models import Animal

    young = Animal.objects.create(
        name="Юный", species="кошка", age=3, owner="А")
    old = Animal.objects.create(
        name="Старый", species="кошка", age=9, owner="Б")
    young.refresh_from_db()
    old.refresh_from_db()
    assert young.is_senior is False
    assert old.is_senior is True


def test_is_senior_is_recalculated_after_age_change(clinic):
    clinic.murka.age = 10
    clinic.murka.save()
    clinic.murka.refresh_from_db()
    assert clinic.murka.is_senior is True


def test_manager_active_cancelled_completed(clinic):
    from visits.models import Visit

    assert Visit.objects.count() == 3
    assert Visit.objects.active().count() == 2
    assert Visit.objects.cancelled().count() == 1
    assert Visit.objects.completed().count() == 0


def test_manager_all_keeps_history(clinic):
    from visits.models import Visit

    clinic.visit1.cancel()
    assert Visit.objects.all().count() == 3
    assert Visit.objects.active().count() == 1


def test_manager_for_date_and_chaining(clinic):
    from visits.models import Visit

    visits = Visit.objects.active().for_date(date(2026, 10, 15))
    assert visits.count() == 2
    assert Visit.objects.for_date(date(2026, 10, 16)).count() == 1
    assert Visit.objects.active().for_date(date(2026, 10, 16)).count() == 0


def test_cancel_and_complete_change_status(clinic):
    from visits.models import Visit

    clinic.visit1.cancel()
    clinic.visit3.complete()
    clinic.visit1.refresh_from_db()
    clinic.visit3.refresh_from_db()
    assert clinic.visit1.status == Visit.Status.CANCELLED
    assert clinic.visit3.status == Visit.Status.COMPLETED
    assert clinic.visit1.is_active is False


def test_clean_rejects_second_active_visit_of_doctor(clinic):
    from visits.models import Visit

    duplicate = Visit(
        animal=clinic.rex, doctor=clinic.sidorov,
        visit_date=date(2026, 10, 15))
    with pytest.raises(ValidationError):
        duplicate.clean()
    assert Visit.objects.active().count() == 2


def test_clean_allows_other_doctor_or_date(clinic):
    from visits.models import Visit

    Visit(animal=clinic.rex, doctor=clinic.kuznetsova,
          visit_date=date(2026, 10, 16)).clean()
    Visit(animal=clinic.rex, doctor=clinic.sidorov,
          visit_date=date(2026, 10, 20)).clean()


def test_cancelled_visit_does_not_block_doctor(clinic):
    from visits.models import Visit

    # У Сидорова на 16.10 есть только отменённое посещение.
    Visit(animal=clinic.barsik, doctor=clinic.sidorov,
          visit_date=date(2026, 10, 16)).clean()


def test_clean_ignores_visit_itself(clinic):
    clinic.visit1.clean()


def test_protected_relations(clinic):
    with pytest.raises(ProtectedError):
        clinic.barsik.delete()
    with pytest.raises(ProtectedError):
        clinic.sidorov.delete()


def test_prescriptions_deleted_with_visit(clinic):
    from visits.models import Prescription

    assert Prescription.objects.count() == 1
    clinic.visit1.delete()
    assert Prescription.objects.count() == 0


def test_str_methods(clinic):
    assert str(clinic.barsik) == "Барсик"
    assert str(clinic.sidorov) == "Сидоров П.П."
    assert "Барсик" in str(clinic.visit1)
    assert "Омепразол" in str(clinic.visit1.prescriptions.first())


def test_related_names(clinic):
    assert clinic.sidorov.visits.count() == 2
    assert clinic.barsik.visits.count() == 1
    assert clinic.visit1.prescriptions.count() == 1


def test_migrations_match_models():
    from django.core.management import call_command

    call_command("makemigrations", "--check", "--dry-run")
