https://flask-pages-analyzer.onrender.com/

### Hexlet tests and linter status:
[![Actions Status](https://github.com/karelinaas/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/karelinaas/python-project-83/actions)

[![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-light.svg)](https://sonarcloud.io/summary/new_code?id=karelinaas_python-project-83)

# Flask Pages Analyzer

![Tests](https://ru.hexlet.io/rails/active_storage/blobs/proxy/eyJfcmFpbHMiOnsiZGF0YSI6MzU2NDMsInB1ciI6ImJsb2JfaWQifX0=--0aa29d4120b54a5789c1bde22aa181e577b5dc91/tests.gif)

Веб-приложение для анализа и мониторинга веб-страниц. Этот инструмент позволяет добавлять URL-адреса, проверять их статус-коды и извлекать SEO-метаданные, такие как заголовки страниц, заголовки h1 и мета-описания.

## Возможности

- **Управление URL**: Добавление и управление несколькими URL-адресами для анализа
- **SEO-анализ**: Извлечение и отображение SEO-тегов (h1, title, meta description)
- **Мониторинг статуса**: Проверка HTTP-статус-кодов для каждого URL
- **История проверок**: Просмотр истории проверок для каждого отслеживаемого URL
- **Валидация**: Автоматическая валидация и нормализация URL

## Технологический стек

- **Backend**: Flask 3.1+
- **База данных**: PostgreSQL с psycopg3
- **Парсинг HTML**: BeautifulSoup4
- **HTTP-клиент**: Requests
- **WSGI-сервер**: Gunicorn
- **Тестирование**: pytest, pytest-cov
- **Линтинг**: Ruff
- **Менеджер пакетов**: UV

## Установка

### Предварительные требования

- Python 3.12 или выше
- PostgreSQL 12 или выше
- Менеджер пакетов UV

### Настройка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/karelinaas/python-project-83.git
cd python-project-83
```

2. Установите зависимости с помощью UV (рекомендуется):
```bash
uv sync
```

(Опционально) Установите зависимости для разработки:
```bash
uv sync --group dev
```

3. Настройте базу данных, в консоли psql:
```bash
createdb page_analyzer
psql page_analyzer < database.sql
```

4. Создайте файл `.env` в корне проекта и заполните его по примеру:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/page_analyzer
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=1
```

Замените `user` и `password` на ваши учётные данные PostgreSQL.

## Запуск

### Режим разработки

1. Активируйте виртуальное окружение:
```bash
source .venv/bin/activate  # На Linux/Mac
.venv\Scripts\activate     # На Windows
```

2. Установите приложение Flask:
```bash
export FLASK_APP=page_analyzer
export FLASK_ENV=development
```

3. Запустите приложение:
```bash
flask run
```

Приложение будет доступно по адресу `http://localhost:5000`

### Режим производства

С помощью Gunicorn:
```bash
gunicorn page_analyzer:app
```

Или с помощью предоставленного скрипта сборки:
```bash
./build.sh
```

## Тестирование

Запустите тесты:
```bash
pytest
```

Запустите тесты с покрытием:
```bash
pytest --cov=page_analyzer --cov-report=html
```
