# Frontend «Рядом»

Это самостоятельный mobile-first frontend на HTML, CSS и vanilla JavaScript.

## Запуск

1. Запустите API из корня проекта: `uvicorn app.main:app --reload`.
2. В отдельном PowerShell откройте папку `frontend` и запустите: `python -m http.server 8001`.
3. Откройте http://127.0.0.1:8001.

API-адрес находится только в `js/api.js`. Для другого адреса можно до загрузки приложения задать `window.RYADOM_API_URL`.

Поиск и сохранённое пока являются информационными экранами: backend не предоставляет для них API.
