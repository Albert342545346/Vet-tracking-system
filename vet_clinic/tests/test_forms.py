"""Тесты форм: фильтры, создание и редактирование, фото."""
import io

import pytest

pytestmark = pytest.mark.django_db


def visit_data(animal, doctor, visit_date, diagnosis=""):
    return {
        "animal": animal.pk,
        "doctor": doctor.pk,
        "visit_date": visit_date.isoformat(),
        "diagnosis": diagnosis,
    }


def test_visit_form_valid(clinic, future_date):
    from visits.forms import VisitForm

    form = VisitForm(
        visit_data(clinic.rex, clinic.sidorov, future_date(5)))
    assert form.is_valid(), form.errors


def test_visit_form_has_no_status_field(db):
    from visits.forms import VisitForm

    assert "status" not in VisitForm().fields


def test_visit_form_rejects_past_date(clinic):
    from datetime import date

    from visits.forms import VisitForm

    form = VisitForm(
        visit_data(clinic.rex, clinic.sidorov, date(2020, 1, 1)))
    assert not form.is_valid()
    assert "visit_date" in form.errors


def test_visit_form_rejects_busy_doctor(clinic, future_date):
    from visits.forms import VisitForm
    from visits.models import Visit

    busy_day = future_date(7)
    Visit.objects.create(
        animal=clinic.barsik, doctor=clinic.sidorov, visit_date=busy_day)
    form = VisitForm(visit_data(clinic.rex, clinic.sidorov, busy_day))
    assert not form.is_valid()
    assert form.non_field_errors()


def test_visit_form_cancelled_visit_does_not_block(clinic, future_date):
    from visits.forms import VisitForm
    from visits.models import Visit

    day = future_date(8)
    Visit.objects.create(
        animal=clinic.barsik, doctor=clinic.sidorov, visit_date=day,
        status=Visit.Status.CANCELLED)
    form = VisitForm(visit_data(clinic.rex, clinic.sidorov, day))
    assert form.is_valid(), form.errors


def test_visit_form_edit_without_changes_is_valid(clinic):
    from visits.forms import VisitForm

    data = visit_data(
        clinic.barsik, clinic.sidorov, clinic.visit1.visit_date,
        "Гастрит")
    form = VisitForm(data, instance=clinic.visit1)
    assert form.is_valid(), form.errors


def test_visit_form_edit_to_past_date_is_invalid(clinic):
    from datetime import date

    from visits.forms import VisitForm

    data = visit_data(clinic.barsik, clinic.sidorov, date(2020, 1, 1))
    form = VisitForm(data, instance=clinic.visit1)
    assert not form.is_valid()


def test_filter_form_valid_and_empty(clinic):
    from visits.forms import VisitFilterForm

    form = VisitFilterForm({"animal": clinic.rex.pk, "sort": "animal"})
    assert form.is_valid()
    assert form.cleaned_data["animal"] == clinic.rex
    assert VisitFilterForm({}).is_valid()


def test_filter_form_invalid_values(clinic):
    from visits.forms import VisitFilterForm

    assert not VisitFilterForm({"date": "не-дата"}).is_valid()
    assert not VisitFilterForm({"animal": "abc"}).is_valid()
    assert not VisitFilterForm({"sort": "id; DROP TABLE"}).is_valid()


def test_filter_form_only_active_hides_status(db):
    from visits.forms import VisitFilterForm

    assert "status" in VisitFilterForm().fields
    assert "status" not in VisitFilterForm(only_active=True).fields


def make_png(name="pet.png"):
    image_module = pytest.importorskip("PIL.Image")
    from django.core.files.uploadedfile import SimpleUploadedFile

    buffer = io.BytesIO()
    image_module.new("RGB", (4, 4), "red").save(buffer, format="PNG")
    return SimpleUploadedFile(
        name, buffer.getvalue(), content_type="image/png")


def animal_data():
    return {"name": "Шарик", "species": "собака", "age": 4,
            "owner": "Орлов Д.В."}


def test_animal_form_without_photo_is_valid(db):
    from animals.forms import AnimalForm

    assert AnimalForm(animal_data()).is_valid()


def test_animal_form_accepts_png(db):
    from animals.forms import AnimalForm

    form = AnimalForm(animal_data(), {"photo": make_png()})
    assert form.is_valid(), form.errors


def test_animal_form_rejects_non_image(db):
    from django.core.files.uploadedfile import SimpleUploadedFile

    from animals.forms import AnimalForm

    fake = SimpleUploadedFile(
        "fake.png", b"not an image", content_type="image/png")
    form = AnimalForm(animal_data(), {"photo": fake})
    assert not form.is_valid()
    assert "photo" in form.errors


def test_animal_form_has_no_slug_or_generated_fields(db):
    from animals.forms import AnimalForm

    fields = AnimalForm().fields
    assert "slug" not in fields
    assert "is_senior" not in fields


def test_create_animal_with_photo_through_view(client, settings, tmp_path):
    from animals.models import Animal

    settings.MEDIA_ROOT = tmp_path
    data = dict(animal_data(), photo=make_png())
    response = client.post("/animals/create/", data)
    assert response.status_code == 302
    animal = Animal.objects.get(name="Шарик")
    assert response.url == animal.get_absolute_url()
    assert animal.photo.name.startswith("animals/")
    assert (tmp_path / animal.photo.name).exists()
    page = client.get(animal.get_absolute_url()).content.decode("utf-8")
    assert "<img" in page and animal.photo.url in page


def test_create_animal_invalid_shows_errors(client):
    from animals.models import Animal

    response = client.post("/animals/create/", {"name": ""})
    assert response.status_code == 200
    assert Animal.objects.count() == 0
    assert "errorlist" in response.content.decode("utf-8")


def test_animal_create_page_opens(client):
    response = client.get("/animals/create/")
    assert response.status_code == 200
    assert 'enctype="multipart/form-data"' in response.content.decode()
    assert "csrfmiddlewaretoken" in response.content.decode()
