-- ============================================================================
-- SQL скрипт для PostgreSQL - Система учета заявок на ремонт оборудования
-- ВЕРСИЯ С АВТОИНКРЕМЕНТОМ
-- ============================================================================

-- ============================================================================
-- 1. УДАЛЕНИЕ СТАРЫХ ТАБЛИЦ (если существуют)
-- ============================================================================

DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS repair_requests CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- 2. СОЗДАНИЕ ТАБЛИЦ С АВТОИНКРЕМЕНТОМ
-- ============================================================================

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) NOT NULL CHECK (user_type IN ('Менеджер', 'Специалист', 'Оператор', 'Заказчик', 'Менеджер по качеству'))
);

CREATE TABLE repair_requests (
    request_id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    climate_tech_type VARCHAR(100) NOT NULL,
    climate_tech_model VARCHAR(100) NOT NULL,
    problem_description TEXT NOT NULL,
    request_status VARCHAR(50) NOT NULL CHECK (request_status IN ('Новая заявка', 'В процессе ремонта', 'Готова к выдаче', 'Ожидание комплектующих')),
    completion_date DATE,
    repair_parts VARCHAR(255),
    master_id INT,
    client_id INT NOT NULL,
    FOREIGN KEY (master_id) REFERENCES users(user_id),
    FOREIGN KEY (client_id) REFERENCES users(user_id),
    CONSTRAINT check_completion_date CHECK (completion_date IS NULL OR completion_date >= start_date)
);

CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    master_id INT NOT NULL,
    request_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (master_id) REFERENCES users(user_id),
    FOREIGN KEY (request_id) REFERENCES repair_requests(request_id)
);

-- ============================================================================
-- 3. СОЗДАНИЕ ИНДЕКСОВ
-- ============================================================================

CREATE INDEX idx_requests_status ON repair_requests(request_status);
CREATE INDEX idx_requests_master ON repair_requests(master_id);
CREATE INDEX idx_requests_client ON repair_requests(client_id);
CREATE INDEX idx_comments_request ON comments(request_id);
CREATE INDEX idx_users_type ON users(user_type);

-- ============================================================================
-- 4. ВСТАВКА ДАННЫХ (без указания ID - они генерируются автоматически)
-- ============================================================================

INSERT INTO users (full_name, phone, login, password, user_type)
VALUES
    ('Широков Василий Матвеевич', '89210563128', 'login1', 'pass1', 'Менеджер'),
    ('Кудрявцева Ева Ивановна', '89535078985', 'login2', 'pass2', 'Специалист'),
    ('Гончарова Ульяна Ярославовна', '89210673849', 'login3', 'pass3', 'Специалист'),
    ('Гусева Виктория Данииловна', '89990563748', 'login4', 'pass4', 'Оператор'),
    ('Баранов Артём Юрьевич', '89994563847', 'login5', 'pass5', 'Оператор'),
    ('Овчинников Фёдор Никитич', '89219567849', 'login6', 'pass6', 'Заказчик'),
    ('Петров Никита Артёмович', '89219567841', 'login7', 'pass7', 'Заказчик'),
    ('Ковалева Софья Владимировна', '89219567842', 'login8', 'pass8', 'Заказчик'),
    ('Кузнецов Сергей Матвеевич', '89219567843', 'login9', 'pass9', 'Заказчик'),
    ('Беспалова Екатерина Даниэльевна', '89219567844', 'login10', 'pass10', 'Специалист');

INSERT INTO repair_requests (start_date, climate_tech_type, climate_tech_model, problem_description, request_status, completion_date, repair_parts, master_id, client_id)
VALUES
    ('2023-06-06', 'Кондиционер', 'TCL TAC-12CHSA/TPG-W белый', 'Не охлаждает воздух', 'В процессе ремонта', NULL, NULL, 2, 7),
    ('2023-05-05', 'Кондиционер', 'Electrolux EACS/I-09HAT/N3_21Y белый', 'Выключается сам по себе', 'В процессе ремонта', NULL, NULL, 3, 8),
    ('2022-07-07', 'Увлажнитель воздуха', 'Xiaomi Smart Humidifier 2', 'Пар имеет неприятный запах', 'Готова к выдаче', '2023-01-01', NULL, 3, 9),
    ('2023-08-02', 'Увлажнитель воздуха', 'Polaris PUH 2300 WIFI IQ Home', 'Увлажнитель воздуха продолжает работать при предельном снижении уровня воды', 'Новая заявка', NULL, NULL, NULL, 8),
    ('2023-08-02', 'Сушилка для рук', 'Ballu BAHD-1250', 'Не работает', 'Новая заявка', NULL, NULL, NULL, 9);

-- Добавляем больше тестовых заявок
INSERT INTO repair_requests (start_date, climate_tech_type, climate_tech_model, problem_description, request_status, completion_date, repair_parts, master_id, client_id)
VALUES
    ('2023-09-10', 'Кондиционер', 'LG S09ET', 'Издает странный звук', 'В процессе ремонта', NULL, NULL, 2, 6),
    ('2023-09-15', 'Увлажнитель воздуха', 'Boneco U201', 'Не включается', 'Новая заявка', NULL, NULL, NULL, 7),
    ('2023-09-20', 'Кондиционер', 'Daikin FTXB25C', 'Протечка воды', 'Ожидание комплектующих', NULL, NULL, 10, 8),
    ('2023-08-01', 'Сушилка для рук', 'Dyson Airblade V', 'Слабый поток воздуха', 'Готова к выдаче', '2023-08-15', 'Фильтр', 2, 9),
    ('2023-07-10', 'Кондиционер', 'Mitsubishi MSZ-SF25VE', 'Не реагирует на пульт', 'Готова к выдаче', '2023-07-25', 'ИК-приемник', 3, 6),
    ('2023-06-15', 'Увлажнитель воздуха', 'Stadler Form Oskar', 'Неприятный запах', 'Готова к выдаче', '2023-06-30', 'Картридж', 10, 7),
    ('2023-09-25', 'Кондиционер', 'Panasonic CS-E9RKDW', 'Не охлаждает', 'Новая заявка', NULL, NULL, NULL, 9);

INSERT INTO comments (message, master_id, request_id)
VALUES
    ('Всё сделаем!', 2, 1),
    ('Всё сделаем!', 3, 2),
    ('Починим в момент.', 3, 3);

-- ============================================================================
-- 5. ПРОВЕРКА ДАННЫХ
-- ============================================================================

SELECT * FROM users;
SELECT * FROM repair_requests;
SELECT * FROM comments;

-- Проверка автоинкремента
SELECT
    'users' as table_name,
    pg_get_serial_sequence('users', 'user_id') as sequence_name,
    last_value as current_value
FROM users_user_id_seq
UNION ALL
SELECT
    'repair_requests',
    pg_get_serial_sequence('repair_requests', 'request_id'),
    last_value
FROM repair_requests_request_id_seq
UNION ALL
SELECT
    'comments',
    pg_get_serial_sequence('comments', 'comment_id'),
    last_value
FROM comments_comment_id_seq;
