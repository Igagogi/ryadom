# Рядом

AI-помощник для родителей детей 2–6 лет.

Проект помогает быстро получить практический ответ на вопрос:

> «Что делать прямо сейчас?»

Ответ формируется с учётом возраста ребёнка, ситуации и контекста.

Проект разработан как полноценный backend-проект с REST API, PostgreSQL, JWT-аутентификацией, интеграцией LLM, тестированием и Docker.

---

## Возможности

### 1. Рекомендации

Пользователь указывает:

- возраст ребёнка;
- категорию ситуации;
- подкатегорию;
- место.

Система сначала ищет подходящий готовый сценарий в PostgreSQL.

Если сценарий не найден, запрос передаётся AI.

Ответ содержит:

- название рекомендации;
- последовательность действий;
- готовую фразу;
- чего лучше избегать;
- что делать, если рекомендация не помогла.

### 2. Занятия

Пользователь указывает:

- возраст ребёнка;
- доступное время;
- место;
- доступные предметы.

AI генерирует одно подходящее занятие.

Если AI предлагает занятие дольше доступного времени, система отправляет дополнительный запрос на корректировку.

### 3. Истории

Можно создать персонализированную историю с учётом:

- возраста;
- имени ребёнка;
- настроения;
- персонажа;
- продолжительности.

### 4. Регистрация и авторизация

Реализованы:

- регистрация;
- вход;
- JWT-аутентификация;
- хеширование паролей через Argon2;
- получение текущего пользователя;
- изменение данных пользователя;
- удаление пользователя.

### 5. Ограничение AI-запросов

Для неавторизованных пользователей действует ограничение количества AI-запросов.

Лимиты разделены по операциям:

- рекомендации;
- занятия;
- истории.

Авторизованные пользователи не используют гостевой лимит.

### 6. Web-интерфейс

В проекте есть frontend на HTML, CSS и JavaScript.

Frontend взаимодействует с реальным FastAPI API и поддерживает регистрацию, авторизацию, профиль пользователя, рекомендации, генерацию занятий и историй, обработку ошибок API и адаптивный интерфейс.

---

## Архитектура

Основная структура backend:

```text
Client
   ↓
Router
   ↓
Schema
   ↓
Service
   ├── Repository → PostgreSQL
   │
   └── AIService → LLM Provider
```

### Основные компоненты

**Router** — HTTP-эндпоинты FastAPI, получение параметров запроса и подключение зависимостей.

**Schema** — Pydantic-модели для валидации входных данных и формирования API-ответов.

**Service** — бизнес-логика приложения и координация между repository, AI и другими компонентами.

**Repository** — работа с PostgreSQL через SQLAlchemy.

**AIService** — единая точка взаимодействия бизнес-логики с LLM-провайдерами.

**Security** — хеширование паролей и работа с JWT.

**Dependencies** — FastAPI-зависимости, включая получение текущего пользователя и AI-сервиса.

**Alembic** — миграции структуры базы данных.

---

## AI-архитектура

Для работы с несколькими LLM-провайдерами используется единый интерфейс:

```text
                    ┌── Groq
                    │
AIService ──────────┼── OpenAI
                    │
                    └── Yandex
```

Провайдер выбирается через переменную окружения:

```env
AI_PROVIDER=groq
```

Поддерживаемые значения:

```text
groq
openai
yandex
```

Каждый провайдер реализует единый интерфейс `LLMProvider`.

Это позволяет менять поставщика AI без изменения бизнес-логики приложения.

---

## Структура проекта

```text
ryadom/
│
├── app/
│   ├── ai/
│   │   ├── prompts/
│   │   ├── base.py
│   │   ├── factory.py
│   │   ├── groq_provider.py
│   │   ├── openai_provider.py
│   │   ├── service.py
│   │   └── yandex_provider.py
│   │
│   ├── constants/
│   ├── core/
│   ├── db/
│   ├── repository/
│   ├── routers/
│   ├── schemas/
│   ├── service/
│   └── utils/
│
├── alembic/
├── frontend/
├── tests/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# Технологии

### Backend

- Python 3.13
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- Uvicorn

### Authentication & Security

- PyJWT
- pwdlib
- Argon2

### AI

- Groq API
- OpenAI API
- Yandex AI Studio SDK

### Testing

- pytest
- pytest-asyncio
- HTTP testing

### Infrastructure

- Docker
- Docker Compose

### Frontend

- HTML
- CSS
- JavaScript

---

# Переменные окружения

Создайте файл `.env` в корне проекта.

Пример структуры находится в:

```text
.env.example
```

Основные переменные:

```env
DATABASE_URL=
GROQ_API_KEY=
OPENAI_API_KEY=
YANDEX_API_KEY=
YANDEX_FOLDER_ID=
JWT_SECRET_KEY=
AI_PROVIDER=groq
```

### AI_PROVIDER

Определяет используемого AI-провайдера:

```env
AI_PROVIDER=groq
```

или:

```env
AI_PROVIDER=openai
```

или:

```env
AI_PROVIDER=yandex
```

Для выбранного провайдера необходимо указать соответствующие credentials.

Файл `.env` не должен добавляться в Git.

---

# Локальный запуск

## 1. Клонирование

```bash
git clone https://github.com/Igagogi/ryadom.git
cd ryadom
```

## 2. Создание виртуального окружения

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Установка зависимостей

```powershell
pip install -r requirements.txt
```

## 4. Настройка PostgreSQL

Создайте базу данных:

```text
ryadom
```

и укажите подключение в `.env`:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/ryadom
```

## 5. Настройка AI

Например, для Yandex:

```env
AI_PROVIDER=yandex
YANDEX_API_KEY=your_api_key
YANDEX_FOLDER_ID=your_folder_id
```

Или для Groq:

```env
AI_PROVIDER=groq
GROQ_API_KEY=your_api_key
```

## 6. Применение миграций

```powershell
alembic upgrade head
```

## 7. Заполнение готовых сценариев

```powershell
python -m app.db.seed_scenarios
```

## 8. Запуск backend

```powershell
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# Запуск frontend

Frontend находится в:

```text
frontend/
```

Для локального запуска:

```powershell
python -m http.server 8001 --directory frontend
```

После этого:

```text
http://localhost:8001
```

Frontend взаимодействует с FastAPI backend.

---

# Запуск через Docker

Проект содержит:

- `Dockerfile`;
- `docker-compose.yml`.

Docker Compose запускает:

```text
FastAPI
   +
PostgreSQL
```

Запуск:

```powershell
docker compose up --build
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## Миграции в Docker

После запуска контейнеров:

```powershell
docker compose exec api alembic upgrade head
```

Проверить текущую версию миграций:

```powershell
docker compose exec api alembic current
```

---

# Тестирование

Запуск всех тестов:

```powershell
python -m pytest -q
```

Текущий набор содержит:

```text
28 tests
```

Тесты проверяют:

- подключение к тестовой БД;
- валидацию;
- регистрацию;
- авторизацию;
- JWT;
- protected endpoints;
- рекомендации;
- готовые сценарии;
- AI fallback;
- обработку ошибок AI;
- генерацию занятий;
- генерацию историй;
- ограничения гостевых AI-запросов.

---

# База данных

Используется:

```text
PostgreSQL
    ↓
SQLAlchemy
    ↓
Alembic
```

Миграции находятся в:

```text
alembic/versions/
```

Актуальная версия схемы определяется через:

```powershell
alembic current
```

---

# API

Основные endpoints:

### Authentication

```text
POST /auth/register
POST /auth/login
```

### User

```text
GET    /users/me
PUT    /users/me
DELETE /users/me
```

### Recommendations

```text
POST /recommendations
```

### Activities

```text
POST /activities
```

### Stories

```text
POST /stories
```

Полная интерактивная документация API доступна через Swagger:

```text
http://localhost:8000/docs
```

---

# Обработка AI-запросов

Для AI-ответов используются Pydantic-модели.

Общий поток:

```text
User Request
     ↓
FastAPI
     ↓
Service
     ↓
AIService
     ↓
LLM Provider
     ↓
Structured JSON
     ↓
Pydantic validation
     ↓
API Response
```

Это позволяет отделить работу конкретного LLM-провайдера от бизнес-логики приложения.

---

# Статус проекта

Проект находится на стадии MVP.

Уже реализованы:

- FastAPI REST API;
- PostgreSQL;
- SQLAlchemy;
- Alembic;
- готовые сценарии рекомендаций;
- AI fallback;
- генерация занятий;
- генерация историй;
- регистрация;
- авторизация;
- JWT;
- Argon2;
- ограничение гостевых AI-запросов;
- multi-provider AI architecture;
- frontend;
- тестирование;
- Docker;
- Docker Compose.

---

# Текущая цель

«Рядом» создаётся как практический AI-продукт и portfolio project.

Проект демонстрирует работу с:

- Python;
- FastAPI;
- REST API;
- PostgreSQL;
- SQLAlchemy;
- Alembic;
- Pydantic;
- JWT;
- authentication;
- business logic;
- repository pattern;
- LLM API;
- multi-provider AI architecture;
- error handling;
- automated testing;
- Docker;
- frontend integration.

Разработка ведётся по принципу:

```text
MVP
 ↓
реальные пользователи
 ↓
обратная связь
 ↓
улучшение продукта
```

---

# Следующие этапы

После завершения MVP возможны:

- профиль ребёнка;
- история запросов;
- персонализация;
- дополнительные сценарии;
- улучшение AI-рекомендаций;
- deployment;
- сбор обратной связи;
- анализ пользовательских запросов;
- монетизация.

Новые функции добавляются после проверки их необходимости на реальных пользовательских сценариях.
