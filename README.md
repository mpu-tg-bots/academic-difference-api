# Academic Differences API

**Система управления академическими расхождениями в учебных планах (РУП)**

Полностью автоматизированный проект на Django REST Framework с Telegram ботом для управления расхождениями в учебных планах. Включает CI/CD pipeline, инфраструктуру как код (Ansible) и готовую конфигурацию для production деплоя.

---

## 🚀 Быстрый старт

### Требования

- **Docker** 20.10+
- **Docker Compose** v2.0+
- **Node.js** 20+ (для разработки бота)
- **Python** 3.12+ (для локальной разработки API)

### Запуск локально

1. **Клонируйте репозиторий:**

   ```bash
   git clone <repository-url>
   cd academic-difference-api
   ```

2. **Создайте файл окружения:**

   ```bash
   cp .env.example .env
   ```

3. **Запустите проект:**

   ```bash
   docker compose up --build -d
   ```

4. **Проверьте работу:**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/api/v1/schema/swagger-ui/
   - ReDoc: http://localhost:8000/api/v1/schema/redoc/
   - Telegram Bot: работает в фоне

---

## 📚 Документация

- **[Архитектура проекта](docs/ARCHITECTURE.md)** - описание компонентов системы, взаимодействие сервисов, CI/CD
- **[Доменная область](docs/DOMAIN.md)** - модели данных, бизнес-логика, API endpoints, workflow пользователя
- **[Руководство для разработчиков](docs/DEVELOPMENT.md)** - настройка окружения, работа с кодом, тестирование
- **[Руководство по деплою](docs/DEPLOYMENT.md)** - развертывание на production сервере

---

## ✨ Возможности

### API (Django REST Framework)

- ✅ CRUD операции для студентов, кафедр, предметов и академических расхождений
- ✅ JWT аутентификация
- ✅ Автоматическая документация (Swagger/ReDoc)
- ✅ Фильтрация и поиск
- ✅ История изменений (django-simple-history)
- ✅ Импорт/экспорт данных (django-import-export)

### Telegram Bot

- ✅ Интеграция с API через автогенерируемый клиент
- ✅ Управление расхождениями через Telegram
- ✅ TypeScript + Telegraf
- ✅ Сессии и сцены

### DevOps

- ✅ **Docker** контейнеризация всех сервисов
- ✅ **CI/CD** через GitHub Actions
- ✅ **Ansible** для автоматизации деплоя
- ✅ **Caddy** как reverse proxy с автоматическим HTTPS
- ✅ **Uptime Kuma** для мониторинга
- ✅ **Trunk-Based Development** workflow
- ✅ **Pre-commit** хуки (black, isort, pylint)
- ✅ **Conventional Commits** проверка

---

## 🏗️ Структура проекта

```
academic-difference-api/
├── api/                      # Django REST API
│   ├── api/                  # Основное приложение
│   ├── core/                 # Настройки Django
│   ├── Dockerfile
│   └── requirements.txt
├── tgbot/                    # Telegram Bot
│   ├── src/
│   │   ├── generated/        # Автогенерируемый API клиент
│   │   ├── scenes.ts         # Сцены бота
│   │   └── main.ts
│   ├── Dockerfile
│   └── package.json
├── infra/                    # Инфраструктура
│   └── ansible/
│       ├── playbook.yml      # Ansible playbook для деплоя
│       ├── compose.yml       # Production Docker Compose
│       ├── templates/        # Шаблоны конфигов
│       └── vars/vault.yml    # Зашифрованные секреты
├── docs/                     # Документация
│   ├── DEVELOPMENT.md
│   ├── DEPLOYMENT.md
│   └── ARCHITECTURE.md
├── compose.yml               # Development Docker Compose
└── .env.example              # Пример переменных окружения
```

---

## 🛠️ Технологии

### Backend

- **Django** 5.2 + **Django REST Framework** 3.16
- **PostgreSQL** 18
- **Token** аутентификация
- **Gunicorn** WSGI сервер

### Frontend Bot

- **TypeScript** 5.9
- **Telegraf** 4.16
- **Express** 5.1 (для healthcheck)
- **Zod** для валидации

### Infrastructure

- **Docker** + **Docker Compose**
- **Caddy** 2 (reverse proxy + HTTPS)
- **Ansible** для автоматизации
- **GitHub Actions** для CI/CD
- **Uptime Kuma** для мониторинга

---

## 🔐 Безопасность

- Все секреты хранятся в **Ansible Vault** (зашифрованы)
- Token аутентификация для доступа бота к API
- HTTPS через Caddy с автоматическими сертификатами Let's Encrypt
- Переменные окружения не коммитятся в Git
- Pre-commit хуки для проверки кода

---

## 📋 Требования к системе

### Разработка

- macOS / Linux / Windows (с WSL2)
- Docker Desktop или Docker Engine
- 4GB RAM минимум
- 10GB свободного места

### Production

- Ubuntu 22.04 LTS
- 2 CPU cores
- 4GB RAM
- 20GB SSD
- Открытые порты: 80, 443, 443/udp, 22

---

## 🤝 Процесс разработки

Проект использует **Trunk-Based Development**:

1. Создайте feature-ветку: `git checkout -b feat/my-feature`
2. Делайте коммиты согласно [Conventional Commits](https://www.conventionalcommits.org/)
3. Отправьте PR в `trunk`
4. Дождитесь прохождения CI проверок
5. После ревью и merge - удалите локальную ветку

Подробнее в [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)

---

## 📦 API Endpoints

### Аутентификация

- `POST /api/v1/auth/token/` - Получить JWT токен
- `POST /api/v1/auth/token/refresh/` - Обновить токен

### Основные ресурсы

- `/api/v1/students/` - Студенты
- `/api/v1/departments/` - Кафедры
- `/api/v1/subjects/` - Предметы
- `/api/v1/academic-differences/` - Академические расхождения
- `/api/v1/academic-difference-files/` - Файлы расхождений

Полная документация: http://localhost:8000/api/v1/schema/swagger-ui/

---

## 🧪 Тестирование

```bash
# API тесты
cd api
pytest --cov

# Bot линтинг
cd tgbot
npm run lint

# Запуск pre-commit хуков вручную
pre-commit run --all-files
```

---

## 📝 Лицензия

Этот проект создан в образовательных целях.

---

## 📞 Контакты

Для вопросов и предложений создавайте Issues в репозитории.

---

## 🔗 Полезные ссылки

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Telegraf Documentation](https://telegraf.js.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Ansible Documentation](https://docs.ansible.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
