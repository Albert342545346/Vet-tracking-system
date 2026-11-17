-- ==========================================
-- VetClinic: структура базы данных (SQLite)
-- ==========================================
-- Сущности предметной области -> таблицы:
--   животное   -> animals
--   врач       -> doctors
--   посещение  -> visits        (связывает животное и врача)
--   назначение -> prescriptions (лечение, входит в состав посещения)

CREATE TABLE IF NOT EXISTS animals (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    species TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0),
    owner TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL
);

-- Диагноз может отсутствовать до приёма (NULL), поэтому NOT NULL нет.
-- is_cancelled: 0 - посещение активно, 1 - отменено.
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY,
    animal_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    visit_date TEXT NOT NULL,
    diagnosis TEXT,
    is_cancelled INTEGER NOT NULL DEFAULT 0 CHECK (is_cancelled IN (0, 1)),
    FOREIGN KEY (animal_id) REFERENCES animals(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);

-- Назначение не существует без посещения, поэтому при удалении
-- посещения его назначения удаляются каскадно.
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_id INTEGER NOT NULL,
    medication TEXT NOT NULL,
    dosage TEXT NOT NULL,
    duration TEXT NOT NULL,
    FOREIGN KEY (visit_id) REFERENCES visits(id) ON DELETE CASCADE
);

-- Индексы для частых условий: врач + дата, животное.
CREATE INDEX IF NOT EXISTS idx_visits_doctor_date
    ON visits (doctor_id, visit_date);
CREATE INDEX IF NOT EXISTS idx_visits_animal
    ON visits (animal_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_visit
    ON prescriptions (visit_id);
