# Phone Address Service

Сервис для хранения и управления связками `телефон — адрес`, реализованный на **FastAPI** с использованием **Redis** как
быстрого key-value хранилища.

Проект оформлен как микросервис с:

- Полностью типизированным кодом
- Выделенным слоем бизнес-логики (services)
- Автоматической Swagger-документацией
- Docker/Docker Compose
- Настроенными линтерами **ruff** и **mypy**
- Хранением конфигурации и секретов в `.env` файле

---

## Стек

- Python 3.12
- FastAPI
- Redis (redis-py async)
- pydantic-settings
- Docker / Docker Compose
- ruff (линтер)
- mypy (проверка типов)

---

## Конфигурация и секреты

Все настройки читаются через `pydantic-settings` из переменных окружения и `.env` файла.

Основные переменные:

- `REDIS_URL` — URL для подключения к Redis (по умолчанию `redis://redis:6379/0`)
- `API_V1_PREFIX` — префикс для v1 API (по умолчанию `/api/v1`)
- `PROJECT_NAME` — название сервиса (по умолчанию `Phone Address Service`)

Создайте файл `.env` на основе примера:

```bash
cp .env.example .env
```

Отредактируйте значения под свою среду, например:

```env
REDIS_URL=redis://redis:6379/0
PROJECT_NAME=Phone Address Service
API_V1_PREFIX=/api/v1
```

---

## Запуск через Docker Compose (рекомендуемый способ)

Требования:

- Docker
- Docker Compose

1. Склонируйте/скачайте проект.
```commandline
git clone https://github.com/faiver-90/phone_address_service
cd phone_address_service
```
2. Создайте `.env`:

```bash
cp .env.example .env
```

3. Запустите сервисы, предварительно проверив, что порт 8000 свободен:

```bash
docker compose up --build -d
```

Сервисы:

- API: `http://localhost:8000`
- Redis: доступен внутри сети Docker как `redis:6379`
- Swagger `http://localhost:8000/docs`

4. Остановить сервисы:

```bash
docker compose down
```

5. Запустить тесты
```bash
poetry run pytest
```

---

## Описание API

Базовый префикс: `/api/v1`

### 1. Просмотр данных (получить адрес по телефону)

**GET** `/api/v1/phone-addresses/{phone}`

- Цель: получить сохранённый адрес по номеру телефона.
- Успешный ответ: `200 OK` и JSON:

```json
{
  "phone": "+7 999 123-45-67",
  "address": "Moscow, Tverskaya street, 1"
}
```

- Если номер не найден: `404 Not Found`

### 2. Создание новой записи

**POST** `/api/v1/phone-addresses`

Тело запроса:

```json
{
  "phone": "+7 999 123-45-67",
  "address": "Moscow, Tverskaya street, 1"
}
```

- Если телефон уже существует: `409 Conflict`
- Если создано успешно: `201 Created` и JSON созданной записи.

### 3. Обновление существующей записи

**PUT** `/api/v1/phone-addresses/{phone}`

Тело запроса:

```json
{
  "address": "Moscow, Arbat street, 10"
}
```

- Если телефон существует: `200 OK` и JSON обновлённой записи.
- Если телефон не найден: `404 Not Found`

### 4. Удаление записи

**DELETE** `/api/v1/phone-addresses/{phone}`

- Если запись существовала и удалена: `204 No Content`
- Если запись не найдена: `404 Not Found`

Все эндпоинты подробно задокументированы в Swagger UI (`/docs`).

---

## Бизнес-логика и слои

- Вся работа с Redis и бизнес-правила инкапсулированы в `PhoneAddressService` (`app/services/phone_address_service.py`).
- API-уровень (`routes_phone_address.py`) не знает о деталях хранилища и работает только через сервис.
- Это упрощает тестирование и возможную смену хранилища (например, на БД) без изменения API-слоя.

---

## Линтеры и проверка типов

### ruff

Запуск линтера:

```bash
ruff check .
```

Фикс автозамен:

```bash
ruff check . --fix
```

### mypy

Статическая проверка типов:

```bash
mypy app
```

---

## Полезные команды

```bash
# Запуск приложения локально
uvicorn app.main:app --reload

# Линтер
ruff check .

# Проверка типов
mypy app

# Docker Compose
docker compose up --build
docker compose down

# Taskfile - вывести список команд
task -l
```
