"""Тесты веб-интерфейса на Django ORM: URL -> view -> шаблон."""
import pytest

pytestmark = pytest.mark.django_db


def text(response):
    """Вернуть тело ответа в виде строки."""
    return response.content.decode("utf-8")


def listed_animals(response):
    """Клички животных в списке посещений (без выпадающих списков)."""
    return [row["animal_name"] for row in response.context["visits"]]


def test_homepage(client, clinic):
    response = client.get("/")
    assert response.status_code == 200
    assert "VetClinic" in text(response)


def test_animal_list(client, clinic):
    body = text(client.get("/animals/"))
    assert "Барсик" in body
    assert "Всего животных" in body
    assert "Мурка" in body


def test_animal_search_by_name_ignores_case(client, clinic):
    body = text(client.get("/animals/?q=барс"))
    assert "Барсик" in body
    assert "Рекс" not in body
    assert "Найдено животных" in body


def test_animal_search_upper_case_query(client, clinic):
    assert "Барсик" in text(client.get("/animals/?q=БАРС"))


def test_animal_search_by_owner(client, clinic):
    body = text(client.get("/animals/?q=петрова"))
    assert "Рекс" in body
    assert "Барсик" not in body


def test_animal_filter_by_species(client, clinic):
    body = text(client.get("/animals/?species=собака"))
    assert "Рекс" in body
    assert "Барсик" not in body


def test_animal_search_nothing_found(client, clinic):
    body = text(client.get("/animals/?q=несуществующий"))
    assert "Животные не найдены" in body


def test_animal_search_is_safe_for_sql_injection(client, clinic):
    response = client.get("/animals/?q=' OR 1=1 --")
    assert response.status_code == 200
    assert "Животные не найдены" in text(response)


def test_animal_search_wildcards_are_escaped(client, clinic):
    body = text(client.get("/animals/?q=%25"))
    assert "Животные не найдены" in body


def test_animal_detail_by_slug(client, clinic):
    url = clinic.barsik.get_absolute_url()
    assert url == f"/animals/barsik-{clinic.barsik.pk}/"
    response = client.get(url)
    assert response.status_code == 200
    assert "Иванов И.И." in text(response)
    assert "Сидоров П.П." in text(response)


def test_animal_not_found_returns_404(client, clinic):
    assert client.get("/animals/no-such-animal/").status_code == 404


def test_animal_detail_shows_history(client, clinic):
    body = text(client.get(clinic.murka.get_absolute_url()))
    assert "Кузнецова О.В." in body
    assert "История посещений (1)" in body


def test_animal_detail_without_photo(client, clinic):
    body = text(client.get(clinic.rex.get_absolute_url()))
    assert "Фотография не загружена." in body


def test_doctor_list(client, clinic):
    body = text(client.get("/doctors/"))
    assert "Сидоров П.П." in body
    assert "Кузнецова О.В." in body
    assert "Врачей: 2" in body
    assert "Активных посещений: 1" in body


def test_doctor_filter_by_specialization(client, clinic):
    body = text(client.get("/doctors/?spec=хирург"))
    assert "Кузнецова О.В." in body
    assert "Сидоров П.П." not in body


def test_doctor_search_ignores_case(client, clinic):
    body = text(client.get("/doctors/?q=ХИРУРГ"))
    assert "Кузнецова О.В." in body
    assert "Сидоров П.П." not in body


def test_visit_list_shows_statuses(client, clinic):
    body = text(client.get("/visits/"))
    assert "Активно" in body
    assert "Отменено" in body


def test_visit_detail(client, clinic):
    response = client.get(f"/visits/{clinic.visit1.pk}/")
    assert response.status_code == 200
    assert "Гастрит" in text(response)
    assert "Омепразол" in text(response)


def test_visit_list_has_all_visits(client, clinic):
    body = text(client.get("/visits/"))
    assert "Всего посещений: 3" in body
    assert "Барсик" in body
    assert "Рекс" in body


def test_active_visits_exclude_cancelled(client, clinic):
    response = client.get("/visits/active/")
    assert "Всего посещений: 2" in text(response)
    names = listed_animals(response)
    assert "Барсик" in names
    assert "Рекс" not in names


def test_available_doctors_page_without_date(client, clinic):
    body = text(client.get("/visits/available/"))
    assert "Свободные врачи" in body
    assert "свободных врачей нет" not in body


def test_available_doctors_cancelled_visit_does_not_block(client, clinic):
    body = text(client.get("/visits/available/?date=2026-10-16"))
    assert "Сидоров П.П." in body
    assert "Кузнецова О.В." in body


def test_available_doctors_busy_doctor_is_excluded(client, clinic):
    body = text(client.get("/visits/available/?date=2026-10-15"))
    assert "Сидоров П.П." not in body
    assert "Кузнецова О.В." not in body
    assert "свободных врачей нет" in body


def test_available_doctors_completed_visit_does_not_block(client, clinic):
    clinic.visit1.complete()
    body = text(client.get("/visits/available/?date=2026-10-15"))
    assert "Сидоров П.П." in body


def test_available_doctors_invalid_date(client, clinic):
    body = text(client.get("/visits/available/?date=15.10.2026"))
    assert "Введите дату в формате ГГГГ-ММ-ДД." in body


def test_statistics_page(client, clinic):
    response = client.get("/visits/statistics/")
    body = text(response)
    assert response.status_code == 200
    assert "Статистика клиники" in body
    assert "Омепразол" in body
    assert "кошка" in body
    assert "терапевт" in body


def test_statistics_counts_by_status(client, clinic):
    context = client.get("/visits/statistics/").context
    assert context["active_count"] == 2
    assert context["cancelled_count"] == 1
    assert context["completed_count"] == 0
    assert context["age_stats"]["animals_count"] == 3
    assert context["age_stats"]["min_age"] == 3
    assert context["age_stats"]["max_age"] == 7


def test_statistics_doctor_without_visits_has_zero(client, clinic):
    from doctors.models import Doctor

    Doctor.objects.create(name="Новый В.В.", specialization="офтальмолог")
    stats = list(client.get("/visits/statistics/").context["doctor_stats"])
    names = {item["doctor_name"]: item["visits_count"] for item in stats}
    assert names["Новый В.В."] == 0
    assert names["Сидоров П.П."] == 1


def test_statistics_having_threshold(client, clinic):
    assert "Врачей с таким числом" not in text(
        client.get("/visits/statistics/?min=1")
    )
    assert "Врачей с таким числом" in text(
        client.get("/visits/statistics/?min=2")
    )


def test_statistics_invalid_threshold_uses_default(client, clinic):
    assert client.get("/visits/statistics/?min=abc").status_code == 200


def test_visit_not_found_returns_404(client, clinic):
    assert client.get("/visits/999/").status_code == 404


def test_unknown_url_returns_404(client, clinic):
    assert client.get("/nonexistent/").status_code == 404


def test_named_urls():
    from django.urls import reverse

    assert reverse("homepage:index") == "/"
    assert reverse("animals:list") == "/animals/"
    assert reverse("animals:create") == "/animals/create/"
    assert reverse("animals:detail", args=["barsik-1"]) == (
        "/animals/barsik-1/"
    )
    assert reverse("visits:detail", args=[2]) == "/visits/2/"
    assert reverse("visits:update", args=[2]) == "/visits/2/edit/"
    assert reverse("visits:cancel", args=[2]) == "/visits/2/cancel/"
    assert reverse("visits:create") == "/visits/create/"
    assert reverse("doctors:list") == "/doctors/"
    assert reverse("visits:active") == "/visits/active/"
    assert reverse("visits:available") == "/visits/available/"
    assert reverse("visits:statistics") == "/visits/statistics/"


def test_navigation_links(client, clinic):
    body = text(client.get("/"))
    for url in ("/animals/", "/doctors/", "/visits/",
                "/visits/statistics/"):
        assert f'href="{url}"' in body


def test_context_processor_provides_common_data(client, clinic):
    response = client.get("/visits/")
    assert response.context["site_name"] == "VetClinic"
    assert response.context["animals_count"] == 3
    assert "Животные (3)" in text(response)


def test_views_do_not_use_sqlite3():
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    for app in ("animals", "doctors", "visits"):
        source = (root / app / "views.py").read_text(encoding="utf-8")
        assert "sqlite3" not in source
        assert "cursor" not in source
