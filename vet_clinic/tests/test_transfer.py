"""Тест переноса данных из базы ПР7 в базу Django."""
import pytest

pytestmark = pytest.mark.django_db


def test_transfer_copies_all_tables(db_file):
    from db.import_sqlite_to_orm import transfer

    counts = transfer(db_file)
    assert counts == {
        "animals": 3, "doctors": 2, "visits": 3, "prescriptions": 1}


def test_transfer_keeps_ids_relations_and_statuses(db_file):
    from animals.models import Animal
    from db.import_sqlite_to_orm import transfer
    from visits.models import Visit

    transfer(db_file)
    visit = Visit.objects.select_related("animal", "doctor").get(pk=1)
    assert (visit.animal.name, visit.doctor.name) == (
        "Барсик", "Сидоров П.П.")
    assert visit.visit_date.isoformat() == "2026-10-15"
    assert visit.diagnosis == "Гастрит"
    assert Visit.objects.get(pk=2).status == Visit.Status.CANCELLED
    assert Visit.objects.get(pk=2).diagnosis == ""
    assert Visit.objects.get(pk=3).status == Visit.Status.ACTIVE
    assert Animal.objects.get(pk=1).slug == "barsik-1"
    assert visit.prescriptions.get().medication == "Омепразол"


def test_transfer_is_repeatable(db_file):
    from db.import_sqlite_to_orm import transfer

    transfer(db_file)
    assert transfer(db_file)["visits"] == 3


def test_transfer_missing_source_raises(tmp_path):
    from db.import_sqlite_to_orm import transfer

    with pytest.raises(FileNotFoundError):
        transfer(tmp_path / "nope.sqlite")
