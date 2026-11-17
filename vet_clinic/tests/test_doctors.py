from models import Doctor


def test_doctor_creation():
    doctor = Doctor(1, "Петров И.И.", "терапевт")
    assert doctor.id == 1
    assert doctor.name == "Петров И.И."
    assert doctor.specialization == "терапевт"
