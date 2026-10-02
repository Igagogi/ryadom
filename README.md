# Рядом

**AI-помощник для родителей детей 2–6 лет**

> «Что делать прямо сейчас?»

🌐 **Live Demo:** https://ryadomai.online  
📖 **API Docs:** https://api.ryadomai.online/docs

---

## О проекте

**Рядом** — веб-приложение с AI, которое помогает родителям быстро получить практический ответ в конкретной ситуации.

Вместо длинных статей пользователь получает короткий структурированный ответ: **что сделать, что сказать, чего избегать и что попробовать, если первый вариант не помог.**

Проект создан как полноценный backend-проект и развёрнут в production.

## Возможности

### 💡 Что делать сейчас?
Пользователь указывает возраст ребёнка, ситуацию и место. Система сначала ищет подходящий сценарий в базе данных, а при необходимости использует AI.

### 🎨 Чем занять ребёнка?
AI создаёт конкретную игру или занятие с учётом:
- возраста;
- доступного времени;
- места;
- имеющихся предметов.

### 📖 Создать историю
Персональная короткая история с учётом имени ребёнка, возраста, настроения, темы и персонажа.

### 👤 Регистрация и профиль
- регистрация и авторизация;
- JWT-аутентификация;
- просмотр и редактирование профиля;
- удаление аккаунта.

### 🛡️ Ограничение AI-запросов
Для гостей действует rate limit на AI-функции.

---

## Архитектура

```text
Frontend
   ↓
FastAPI Router
   ↓
Pydantic Schema
   ↓
Service
   ↓
Repository
   ↓
PostgreSQL

Service
   ↓
AIService
   ↓
LLM Provider
   ├── YandexGPT
   ├── Groq
   └── OpenAI
```

Основные принципы:
- разделение HTTP-слоя, бизнес-логики и доступа к данным;
- валидация через Pydantic;
- работа с БД через SQLAlchemy;
- миграции через Alembic;
- отдельный AI-слой с поддержкой нескольких провайдеров.

## Технические сложности

### Структурированные ответы AI

Ответы LLM не используются напрямую как обычный текст. Они проверяются через Pydantic-модели, что позволяет контролировать структуру данных и обрабатывать некорректные ответы AI.

### Поддержка нескольких AI-провайдеров

AI-интеграция изолирована через интерфейс `LLMProvider`. Провайдер выбирается через переменную окружения `AI_PROVIDER`, поэтому бизнес-логика приложения не зависит от конкретного AI-сервиса.

### Сценарии → AI fallback

Для рекомендаций приложение сначала ищет подходящий готовый сценарий в PostgreSQL. Если сценарий не найден, запрос передаётся AI-сервису. Это позволяет использовать заранее подготовленные ответы там, где они подходят, и AI — для более нестандартных ситуаций.

### Production-развёртывание

Приложение развёрнуто на VPS с использованием Docker Compose, PostgreSQL, Nginx и HTTPS. Доступ к серверу защищён через UFW и SSH-аутентификацию по ключам, а резервные копии PostgreSQL создаются автоматически.

## AI Architecture

AI интегрирован через единый интерфейс `LLMProvider`.

Провайдер выбирается через переменную окружения:

```env
AI_PROVIDER=yandex
```

Поддерживаются:
- **YandexGPT**
- **Groq**
- **OpenAI**

AI-ответы проходят структурированную валидацию через Pydantic-модели.

## Технологии

**Backend**
- Python 3.13
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL

**AI**
- YandexGPT
- Groq
- OpenAI
- Structured outputs

**Security**
- JWT
- password hashing
- CORS
- rate limiting

**Testing & CI**
- pytest
- GitHub Actions

**Deployment**
- Docker
- Docker Compose
- Nginx
- Ubuntu
- HTTPS / Let's Encrypt
- UFW

**Frontend**
- HTML
- CSS
- JavaScript

## Тестирование

Проект содержит **28 автоматических тестов**.

Проверяются:
- регистрация и авторизация;
- JWT и защищённые endpoints;
- валидация данных;
- рекомендации и fallback на AI;
- генерация занятий;
- генерация историй;
- ошибки AI;
- работа с тестовой PostgreSQL;
- изоляция пользователей.

CI запускает тесты в GitHub Actions с PostgreSQL.

## Production

Проект развёрнут на VPS и доступен в интернете:

- **Frontend:** https://ryadomai.online
- **API:** https://api.ryadomai.online
- **Swagger:** https://api.ryadomai.online/docs

Production-инфраструктура:
- Selectel VPS;
- Ubuntu 24.04;
- Docker Compose;
- PostgreSQL 17;
- Nginx;
- HTTPS;
- UFW;
- SSH по ключу без root/password login;
- автоматические ежедневные PostgreSQL-бэкапы.

## Локальный запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Igagogi/ryadom.git
cd ryadom
```

### 2. Создать виртуальное окружение

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить `.env`

Создайте `.env` на основе `.env.example` и укажите необходимые переменные:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/ryadom

AI_PROVIDER=yandex

YANDEX_API_KEY=...
YANDEX_FOLDER_ID=...

JWT_SECRET_KEY=...

CORS_ORIGINS=http://127.0.0.1:8001
```

### 5. Запустить PostgreSQL

Базу данных можно запустить через Docker Compose:

```bash
docker compose up -d db
```

### 6. Применить миграции

```bash
alembic upgrade head
```

### 7. Запустить API

```bash
uvicorn app.main:app --reload
```

API будет доступен по адресу:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 8. Запустить frontend

В отдельном терминале:

```bash
python -m http.server 8001 --directory frontend
```

Frontend:

```text
http://127.0.0.1:8001
```

## Docker

Для запуска backend и PostgreSQL:

```bash
docker compose up -d --build
```

В production Dockerfile миграции применяются автоматически перед запуском FastAPI.

## API

Основные endpoints:

| Метод | Endpoint | Назначение |
|---|---|---|
| `POST` | `/auth/register` | Регистрация |
| `POST` | `/auth/login` | Авторизация |
| `GET` | `/users/me` | Текущий пользователь |
| `PUT` | `/users/{user_id}` | Изменение профиля |
| `DELETE` | `/users/{user_id}` | Удаление аккаунта |
| `POST` | `/recommendations` | Рекомендация по ситуации |
| `POST` | `/activities` | Генерация занятия |
| `POST` | `/stories` | Генерация истории |

Полная документация API доступна в Swagger:

https://api.ryadomai.online/docs

## Структура проекта

```text
ryadom/
├── app/
│   ├── ai/
│   ├── constants/
│   ├── core/
│   ├── db/
│   ├── repository/
│   ├── routers/
│   ├── schemas/
│   ├── service/
│   └── utils/
├── alembic/
├── frontend/
├── tests/
├── .github/
│   └── workflows/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Статус

**MVP реализован и развёрнут в production.**

Сейчас проект сфокусирован на:
- реальном использовании;
- сборе обратной связи;
- дальнейшем улучшении продукта.

### Следующие этапы

- история запросов;
- сохранение результатов;
- профиль ребёнка и персонализация;
- анализ повторяющихся ситуаций;
- голосовой ввод;
- PWA / mobile UX;
- платная подписка;
- расширение AI knowledge base / RAG при необходимости.

---

## Автор

Проект разработан как portfolio project для позиции **Junior Python Backend Developer / AI Automation Engineer**.
