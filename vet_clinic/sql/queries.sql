-- ==========================================================
-- VetClinic: SQL-запросы проекта (проверены в SQLite)
-- Запуск:  sqlite3 data/vetclinic.sqlite < sql/queries.sql
-- Значения, помеченные «в приложении ?», в веб-приложении
-- передаются параметрами (заполнитель ?), а не подстановкой строк.
-- ==========================================================

-- ---------- Выборка списков (SELECT ... FROM ... ORDER BY) ----------

-- 1. Список всех животных
SELECT
    id,
    name,
    species,
    age,
    owner
FROM animals
ORDER BY name;

-- 2. Список врачей
SELECT
    id,
    name,
    specialization
FROM doctors
ORDER BY name;

-- 3. Список видов животных без повторов (DISTINCT)
--    Используется для выпадающего списка фильтра на странице животных.
SELECT DISTINCT species
FROM animals
ORDER BY species;

-- 4. Ближайшие посещения: сортировка, ограничение и сдвиг выборки
--    (LIMIT/OFFSET: вторая «страница» по 3 записи)
SELECT
    id,
    visit_date,
    animal_id,
    doctor_id
FROM visits
ORDER BY visit_date, id
LIMIT 3 OFFSET 3;

-- ---------- Фильтрация (WHERE) ----------

-- 5. Животные заданного вида (в приложении species = ?)
SELECT
    id,
    name,
    species,
    age
FROM animals
WHERE species = 'кошка'
ORDER BY name;

-- 6. Поиск животного по части клички (LIKE).
--    В приложении используется py_lower(name) LIKE ? для поиска без
--    учёта регистра (LIKE в SQLite нечувствителен к регистру только
--    для латиницы).
SELECT
    id,
    name,
    species
FROM animals
WHERE name LIKE 'Бар%'
ORDER BY name;

-- 7. Животные от заданного возраста, несколько условий (AND)
SELECT
    id,
    name,
    species,
    age
FROM animals
WHERE age >= 3
  AND species IN ('кошка', 'собака')
ORDER BY age DESC, name;

-- 8. Активные посещения (is_cancelled = 0)
SELECT
    id,
    animal_id,
    doctor_id,
    visit_date
FROM visits
WHERE is_cancelled = 0
ORDER BY visit_date, id;

-- 9. Активные посещения за период (BETWEEN) у выбранного врача
--    (в приложении значения передаются параметрами)
SELECT
    id,
    animal_id,
    visit_date
FROM visits
WHERE is_cancelled = 0
  AND doctor_id = 1
  AND visit_date BETWEEN '2026-10-01' AND '2026-10-31'
ORDER BY visit_date;

-- 10. Посещения, по которым ещё не поставлен диагноз (проверка NULL)
SELECT
    id,
    animal_id,
    visit_date
FROM visits
WHERE diagnosis IS NULL
  AND is_cancelled = 0
ORDER BY visit_date;

-- 11. Свободные врачи на выбранную дату (подзапрос NOT IN).
--     Врач свободен, если у него нет активного посещения на эту дату.
--     В приложении дата передаётся параметром: visit_date = ?
SELECT
    doctors.id,
    doctors.name,
    doctors.specialization
FROM doctors
WHERE doctors.id NOT IN (
    SELECT visits.doctor_id
    FROM visits
    WHERE visits.visit_date = '2026-10-15'
      AND visits.is_cancelled = 0
)
ORDER BY doctors.name;

-- ---------- Соединение таблиц (JOIN) ----------

-- 12. Полная информация о посещениях: животное + врач
SELECT
    visits.id,
    visits.visit_date,
    visits.diagnosis,
    visits.is_cancelled,
    animals.name AS animal_name,
    animals.species AS animal_species,
    doctors.name AS doctor_name,
    doctors.specialization AS doctor_specialization
FROM visits
JOIN animals
    ON visits.animal_id = animals.id
JOIN doctors
    ON visits.doctor_id = doctors.id
ORDER BY visits.visit_date, visits.id;

-- 13. История посещений животного (в приложении animal_id = ?)
SELECT
    visits.id,
    visits.visit_date,
    visits.is_cancelled,
    doctors.name AS doctor_name
FROM visits
JOIN doctors
    ON visits.doctor_id = doctors.id
WHERE visits.animal_id = 1
ORDER BY visits.visit_date DESC;

-- 14. Назначения вместе с посещением, животным и врачом (JOIN 4 таблиц)
SELECT
    prescriptions.medication,
    prescriptions.dosage,
    prescriptions.duration,
    visits.visit_date,
    animals.name AS animal_name,
    doctors.name AS doctor_name
FROM prescriptions
JOIN visits
    ON prescriptions.visit_id = visits.id
JOIN animals
    ON visits.animal_id = animals.id
JOIN doctors
    ON visits.doctor_id = doctors.id
ORDER BY visits.visit_date;

-- ---------- Агрегатные функции ----------

-- 15. Количество активных посещений (COUNT)
SELECT
    COUNT(*) AS active_visits_count
FROM visits
WHERE is_cancelled = 0;

-- 16. Возраст животных: среднее, минимум, максимум (AVG, MIN, MAX)
SELECT
    ROUND(AVG(age), 1) AS avg_age,
    MIN(age) AS min_age,
    MAX(age) AS max_age
FROM animals;

-- 17. Занятость врача на дату: сколько у него активных посещений
--     (в приложении doctor_id = ? и visit_date = ?)
SELECT
    COUNT(*) AS busy
FROM visits
WHERE doctor_id = 1
  AND visit_date = '2026-10-15'
  AND is_cancelled = 0;

-- ---------- Группировка (GROUP BY) и фильтрация групп (HAVING) ----------

-- 18. Количество животных и средний возраст по видам
SELECT
    species,
    COUNT(*) AS animals_count,
    ROUND(AVG(age), 1) AS avg_age
FROM animals
GROUP BY species
ORDER BY animals_count DESC, species;

-- 19. Количество активных посещений по врачам.
--     LEFT JOIN сохраняет врачей без посещений (для них будет 0).
SELECT
    doctors.name AS doctor_name,
    doctors.specialization,
    COUNT(visits.id) AS visits_count
FROM doctors
LEFT JOIN visits
    ON doctors.id = visits.doctor_id
   AND visits.is_cancelled = 0
GROUP BY doctors.id, doctors.name, doctors.specialization
ORDER BY visits_count DESC, doctors.name;

-- 20. Виды, у которых в клинике не менее 2 животных (HAVING)
SELECT
    species,
    COUNT(*) AS animals_count
FROM animals
GROUP BY species
HAVING COUNT(*) >= 2
ORDER BY animals_count DESC;

-- 21. Врачи, у которых не менее N активных посещений (HAVING)
--     (в приложении порог N передаётся параметром: HAVING ... >= ?)
SELECT
    doctors.name AS doctor_name,
    COUNT(visits.id) AS visits_count
FROM doctors
JOIN visits
    ON doctors.id = visits.doctor_id
WHERE visits.is_cancelled = 0
GROUP BY doctors.id, doctors.name
HAVING COUNT(visits.id) >= 1
ORDER BY visits_count DESC, doctors.name;

-- 22. Самые назначаемые препараты (GROUP BY + LIMIT)
SELECT
    medication,
    COUNT(*) AS prescriptions_count
FROM prescriptions
GROUP BY medication
ORDER BY prescriptions_count DESC, medication
LIMIT 5;
