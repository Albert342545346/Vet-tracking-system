"""Тесты административной панели Django."""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_models_registered_in_admin(admin_client, clinic):
    body = admin_client.get("/admin/").content.decode("utf-8")
    for title in ("Животные", "Врачи", "Посещения", "Назначения"):
        assert title in body


@pytest.mark.parametrize(
    "name",
    [
        "animals_animal_changelist",
        "doctors_doctor_changelist",
        "visits_visit_changelist",
        "visits_prescription_changelist",
        "animals_animal_add",
        "doctors_doctor_add",
        "visits_visit_add",
    ],
)
def test_admin_pages_open(admin_client, clinic, name):
    assert admin_client.get(reverse(f"admin:{name}")).status_code == 200


def test_admin_change_pages_with_inlines(admin_client, clinic):
    for name, obj in (
        ("animals_animal_change", clinic.barsik),
        ("doctors_doctor_change", clinic.sidorov),
        ("visits_visit_change", clinic.visit1),
    ):
        url = reverse(f"admin:{name}", args=[obj.pk])
        assert admin_client.get(url).status_code == 200


def test_admin_requires_login(client):
    assert client.get("/admin/").status_code == 302


def test_admin_search_by_related_name(admin_client, clinic):
    url = reverse("admin:visits_visit_changelist")
    body = admin_client.get(url, {"q": "Барс"}).content.decode("utf-8")
    assert "Барсик" in body
    assert "Рекс" not in body


def test_admin_status_filter(admin_client, clinic):
    url = reverse("admin:visits_visit_changelist")
    response = admin_client.get(url, {"status__exact": "cancelled"})
    assert len(response.context["cl"].result_list) == 1


def test_admin_animal_list_shows_annotation(admin_client, clinic):
    url = reverse("admin:animals_animal_changelist")
    response = admin_client.get(url)
    animals = response.context["cl"].result_list
    rows = {animal.name: animal.active_visits for animal in animals}
    assert rows["Барсик"] == 1
    assert rows["Рекс"] == 0


def run_action(admin_client, name, action, objects):
    url = reverse(f"admin:{name}_changelist")
    return admin_client.post(url, {
        "action": action,
        "_selected_action": [obj.pk for obj in objects],
    })


def test_admin_action_cancel_visits(admin_client, clinic):
    from visits.models import Visit

    response = run_action(
        admin_client, "visits_visit", "cancel_visits", [clinic.visit1])
    assert response.status_code == 302
    clinic.visit1.refresh_from_db()
    assert clinic.visit1.status == Visit.Status.CANCELLED


def test_admin_action_complete_visits(admin_client, clinic):
    from visits.models import Visit

    run_action(
        admin_client, "visits_visit", "complete_visits", [clinic.visit3])
    clinic.visit3.refresh_from_db()
    assert clinic.visit3.status == Visit.Status.COMPLETED


def test_admin_action_restore_visit(admin_client, clinic):
    run_action(
        admin_client, "visits_visit", "restore_visits", [clinic.visit2])
    clinic.visit2.refresh_from_db()
    assert clinic.visit2.is_active


def test_admin_restore_is_blocked_when_doctor_is_busy(
        admin_client, clinic):
    from visits.models import Visit

    Visit.objects.create(
        animal=clinic.murka, doctor=clinic.sidorov,
        visit_date=clinic.visit2.visit_date)
    run_action(
        admin_client, "visits_visit", "restore_visits", [clinic.visit2])
    clinic.visit2.refresh_from_db()
    assert clinic.visit2.status == Visit.Status.CANCELLED


def test_admin_action_add_year_recalculates_is_senior(
        admin_client, db):
    from animals.models import Animal

    animal = Animal.objects.create(
        name="Почти старый", species="кошка", age=7, owner="А")
    run_action(admin_client, "animals_animal", "add_year", [animal])
    animal.refresh_from_db()
    assert animal.age == 8
    assert animal.is_senior is True


def test_admin_add_visit_validates_doctor_busy(admin_client, clinic):
    from visits.models import Visit

    url = reverse("admin:visits_visit_add")
    response = admin_client.post(url, {
        "animal": clinic.rex.pk,
        "doctor": clinic.sidorov.pk,
        "visit_date": "2026-10-15",
        "diagnosis": "",
        "status": "active",
        "prescriptions-TOTAL_FORMS": "0",
        "prescriptions-INITIAL_FORMS": "0",
        "prescriptions-MIN_NUM_FORMS": "0",
        "prescriptions-MAX_NUM_FORMS": "1000",
    })
    assert response.status_code == 200
    assert Visit.objects.count() == 3
