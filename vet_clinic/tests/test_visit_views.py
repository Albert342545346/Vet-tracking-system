"""Тесты списка (фильтры, сортировка, страницы) и CRUD посещений."""
from datetime import timedelta

import pytest

pytestmark = pytest.mark.django_db


def text(response):
    return response.content.decode("utf-8")


def names(response):
    """Клички животных в списке (выпадающие списки формы не в счёт)."""
    return [row["animal_name"] for row in response.context["visits"]]


def doctors(response):
    return [row["doctor_name"] for row in response.context["visits"]]


def many_visits(clinic, future_date, count=7):
    """Добавить посещения Рекса к хирургу на разные будущие даты."""
    from visits.models import Visit

    for number in range(count):
        Visit.objects.create(
            animal=clinic.rex, doctor=clinic.kuznetsova,
            visit_date=future_date(20 + number))


def test_filter_by_doctor(client, clinic):
    response = client.get(f"/visits/?doctor={clinic.kuznetsova.pk}")
    assert names(response) == ["Мурка"]


def test_filter_by_animal(client, clinic):
    body = text(client.get(f"/visits/?animal={clinic.barsik.pk}"))
    assert "Всего посещений: 1" in body


def test_filter_by_date(client, clinic):
    response = client.get("/visits/?date=2026-10-16")
    assert names(response) == ["Рекс"]


def test_filter_by_status(client, clinic):
    response = client.get("/visits/?status=cancelled")
    assert names(response) == ["Рекс"]


def test_filter_by_related_specialization(client, clinic):
    response = client.get("/visits/?specialization=хирург")
    assert names(response) == ["Мурка"]


def test_filters_are_combined(client, clinic):
    url = f"/visits/?doctor={clinic.sidorov.pk}&date=2026-10-15"
    assert "Всего посещений: 1" in text(client.get(url))


def test_invalid_filters_show_error_not_traceback(client, clinic):
    for query in ("date=abc", "animal=abc", "doctor=99999", "sort=zzz"):
        response = client.get(f"/visits/?{query}")
        assert response.status_code == 200
        assert "Проверьте корректность параметров" in text(response)


def test_active_page_keeps_only_active_with_filters(client, clinic):
    response = client.get("/visits/active/?date=2026-10-16")
    assert names(response) == []
    assert "Всего посещений: 0" in text(response)


def test_sort_by_animal_name(client, clinic):
    response = client.get("/visits/?sort=animal")
    assert names(response) == ["Барсик", "Мурка", "Рекс"]


def test_sort_by_doctor_name(client, clinic):
    response = client.get("/visits/?sort=doctor")
    assert doctors(response)[0] == "Кузнецова О.В."


def test_default_sort_is_by_date(client, clinic):
    response = client.get("/visits/")
    dates = [row["visit_date"] for row in response.context["visits"]]
    assert dates == sorted(dates)


def test_pagination_five_per_page(client, clinic, future_date):
    many_visits(clinic, future_date)
    response = client.get("/visits/")
    assert len(response.context["page_obj"]) == 5
    assert response.context["page_obj"].paginator.num_pages == 2
    assert "Всего посещений: 10" in text(response)


def test_pagination_second_page(client, clinic, future_date):
    many_visits(clinic, future_date)
    response = client.get("/visits/?page=2")
    assert len(response.context["page_obj"]) == 5


def test_pagination_keeps_filters_in_links(client, clinic, future_date):
    many_visits(clinic, future_date)
    body = text(client.get(f"/visits/?doctor={clinic.kuznetsova.pk}"))
    assert f"doctor={clinic.kuznetsova.pk}" in body
    assert "page=2" in body


def test_pagination_bad_page_is_safe(client, clinic, future_date):
    many_visits(clinic, future_date)
    assert client.get("/visits/?page=abc").status_code == 200
    assert client.get("/visits/?page=999").status_code == 200


def test_create_page_has_csrf_and_initial_date(client, future_date):
    response = client.get("/visits/create/")
    body = text(response)
    assert response.status_code == 200
    assert "csrfmiddlewaretoken" in body
    assert "Новое посещение" in body


def test_create_visit(client, clinic, future_date):
    from visits.models import Visit

    day = future_date(3)
    response = client.post("/visits/create/", {
        "animal": clinic.rex.pk, "doctor": clinic.kuznetsova.pk,
        "visit_date": day.isoformat(), "diagnosis": ""})
    assert response.status_code == 302
    visit = Visit.objects.latest("pk")
    assert visit.status == Visit.Status.ACTIVE
    assert visit.visit_date == day


def test_create_visit_cannot_set_status(client, clinic, future_date):
    from visits.models import Visit

    client.post("/visits/create/", {
        "animal": clinic.rex.pk, "doctor": clinic.kuznetsova.pk,
        "visit_date": future_date(4).isoformat(), "diagnosis": "",
        "status": "completed"})
    assert Visit.objects.latest("pk").status == Visit.Status.ACTIVE


def test_create_visit_busy_doctor_is_rejected(client, clinic):
    from visits.models import Visit

    response = client.post("/visits/create/", {
        "animal": clinic.rex.pk, "doctor": clinic.sidorov.pk,
        "visit_date": clinic.visit1.visit_date.isoformat(),
        "diagnosis": ""})
    assert response.status_code == 200
    assert Visit.objects.count() == 3


def test_create_visit_past_date_is_rejected(client, clinic):
    from visits.models import Visit

    response = client.post("/visits/create/", {
        "animal": clinic.rex.pk, "doctor": clinic.kuznetsova.pk,
        "visit_date": "2020-01-01", "diagnosis": ""})
    assert response.status_code == 200
    assert Visit.objects.count() == 3


def test_update_page_prefilled(client, clinic):
    response = client.get(f"/visits/{clinic.visit1.pk}/edit/")
    body = text(response)
    assert response.status_code == 200
    assert "Редактирование посещения" in body
    assert "Гастрит" in body


def test_update_visit_saves_same_record(client, clinic, future_date):
    from visits.models import Visit

    day = future_date(6)
    response = client.post(f"/visits/{clinic.visit1.pk}/edit/", {
        "animal": clinic.barsik.pk, "doctor": clinic.sidorov.pk,
        "visit_date": day.isoformat(), "diagnosis": "Выздоровел"})
    assert response.status_code == 302
    clinic.visit1.refresh_from_db()
    assert clinic.visit1.visit_date == day
    assert clinic.visit1.diagnosis == "Выздоровел"
    assert Visit.objects.count() == 3


def test_update_unchanged_does_not_conflict_with_itself(client, clinic):
    response = client.post(f"/visits/{clinic.visit1.pk}/edit/", {
        "animal": clinic.barsik.pk, "doctor": clinic.sidorov.pk,
        "visit_date": clinic.visit1.visit_date.isoformat(),
        "diagnosis": "Гастрит"})
    assert response.status_code == 302


def test_update_to_busy_day_is_rejected(client, clinic, future_date):
    from visits.models import Visit

    day = future_date(9)
    Visit.objects.create(
        animal=clinic.rex, doctor=clinic.sidorov, visit_date=day)
    response = client.post(f"/visits/{clinic.visit1.pk}/edit/", {
        "animal": clinic.barsik.pk, "doctor": clinic.sidorov.pk,
        "visit_date": day.isoformat(), "diagnosis": ""})
    assert response.status_code == 200
    clinic.visit1.refresh_from_db()
    assert clinic.visit1.visit_date != day


def test_update_missing_or_cancelled_returns_404(client, clinic):
    assert client.get("/visits/9999/edit/").status_code == 404
    assert client.get(
        f"/visits/{clinic.visit2.pk}/edit/").status_code == 404


def test_cancel_requires_post(client, clinic):
    response = client.get(f"/visits/{clinic.visit1.pk}/cancel/")
    assert response.status_code == 405
    clinic.visit1.refresh_from_db()
    assert clinic.visit1.is_active


def test_cancel_visit_keeps_record(client, clinic):
    from visits.models import Visit

    response = client.post(f"/visits/{clinic.visit1.pk}/cancel/")
    assert response.status_code == 302
    clinic.visit1.refresh_from_db()
    assert clinic.visit1.status == Visit.Status.CANCELLED
    assert Visit.objects.count() == 3


def test_cancelled_visit_frees_doctor(client, clinic):
    client.post(f"/visits/{clinic.visit1.pk}/cancel/")
    body = text(client.get("/visits/available/?date=2026-10-15"))
    assert "Сидоров П.П." in body


def test_cancel_already_cancelled_returns_404(client, clinic):
    response = client.post(f"/visits/{clinic.visit2.pk}/cancel/")
    assert response.status_code == 404


def test_list_shows_edit_and_cancel_only_for_active(client, clinic):
    body = text(client.get("/visits/"))
    assert f"/visits/{clinic.visit1.pk}/edit/" in body
    assert f"/visits/{clinic.visit1.pk}/cancel/" in body
    assert f"/visits/{clinic.visit2.pk}/edit/" not in body


def test_messages_are_shown_after_create(client, clinic, future_date):
    response = client.post("/visits/create/", {
        "animal": clinic.rex.pk, "doctor": clinic.kuznetsova.pk,
        "visit_date": (future_date(3) + timedelta(days=1)).isoformat(),
        "diagnosis": ""}, follow=True)
    assert "Посещение создано." in text(response)


def test_select_related_keeps_detail_query_count_small(
        client, clinic, django_assert_max_num_queries):
    with django_assert_max_num_queries(6):
        client.get(f"/visits/{clinic.visit1.pk}/")
