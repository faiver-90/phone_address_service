FROM python:3.12-slim

# Настройки Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_HOME="/opt/poetry"

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# Копируем только файлы по которым строится зависимость — быстрый кеш
COPY pyproject.toml poetry.lock* ./

# Устанавливаем только PROD зависимости
RUN poetry install --only main --no-root

# Копируем исходники
COPY app ./app

# Пробрасываем порт
EXPOSE 8000

# Команда запуска
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
