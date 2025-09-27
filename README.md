# Academic Differences API

Простое и мощное API на Django REST Framework для управления расхождениями в учебных планах (РУП).

## ✨ Возможности

* **REST API**: Полный набор CRUD-операций для студентов, кафедр, предметов и академических расхождений.
* **Аутентификация**: Используется JWT (JSON Web Tokens) для безопасного доступа к API.
* **Процесс разработки**: Проект следует стратегии **Trunk-Based Development** с обязательными проверками через Pull
  Request'ы.
* **Стиль коммитов**: Внедрена проверка на соответствие
  стилю [Conventional Commits](https://www.conventionalcommits.org/).
* **Качество кода**: Настроен `pre-commit` с хуками для `black`, `isort` и `pylint`.
* **Тестирование**: Высокое покрытие кода тестами с использованием `pytest` и `factory-boy`.
* **CI/CD**: Настроен pipeline на GitHub Actions для автоматических проверок.
* **Docker-ready**: Проект полностью готов к контейнеризации и развертыванию.

## 🚀 Процесс разработки (Trunk-Based Development)

Этот проект использует методологию **Trunk-Based Development**. Это означает, что все изменения интегрируются в основную
ветку (`trunk`) через короткоживущие feature-ветки и **Pull Request'ы (PR)**.

**Прямые коммиты в `trunk` запрещены** с помощью правил защиты веток (Branch Protection Rules).

### Флоу работы над задачей:

1. **Создайте ветку** от актуальной версии `trunk`:
   ```bash
   git checkout trunk
   git pull
   git checkout -b <type>/<short-description>
   # Например: git checkout -b feat/add-student-search
   ```

2. **Сделайте изменения** и закоммитьте их, следуя стилю [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   # ...пишете код...
   git add .
   git commit -m "feat: implement search logic for students"
   # или используйте `cz commit` для помощи
   ```

3. **Отправьте ветку** в удаленный репозиторий и создайте Pull Request на GitHub.

4. **Дождитесь прохождения автоматических проверок**: CI-пайплайн (GitHub Actions) автоматически запустит линтеры, тесты
   и проверку сообщений коммитов.

5. **Выполните слияние (Merge)**: После успешного прохождения всех проверок (и код-ревью, если требуется), ваш PR будет
   влит в `trunk`. Feature-ветка будет удалена автоматически.

## 📦 Локальный запуск (для разработки)

### Предварительные требования

* [Python 3.11+](https://www.python.org/)
* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/) (опционально)

### Установка и запуск

1. **Клонируйте репозиторий** и перейдите в него.

2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Установите pre-commit хуки (важный шаг!):**
   Эта команда установит хуки для автоматической проверки кода (`pre-commit`) и сообщений коммитов (`commit-msg`). **Это
   нужно сделать один раз** после клонирования репозитория.
   ```bash
   pre-commit install --hook-type pre-commit --hook-type commit-msg
   ```

5. **Настройте переменные окружения:**
   ```bash
   cp .env.example .env
   ```

6. **Примените миграции и создайте суперпользователя:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

7. **Запустите сервер для разработки:**
   ```bash
   python manage.py runserver
   ```
   Проект будет доступен по адресу `http://127.0.0.1:8000/`.

## 🛠 Инструменты и качество кода

#### Тестирование

* **Запуск всех тестов**: `pytest`
* **Запуск с отчетом о покрытии**: `pytest --cov` (использует настройки из `.coveragerc`)

#### Стиль коммитов

Проект использует [Conventional Commits](https://www.conventionalcommits.org/). Для упрощения создания коммитов
используйте `cz commit` вместо `git commit`.

#### Pre-commit хуки

После установки (см. раздел "Локальный запуск") хуки будут запускаться автоматически перед каждым коммитом. Они
проверяют код с помощью `black`, `isort`, `pylint` и валидируют сообщение коммита через `commitizen`.

## 🐳 Запуск через Docker

1. **Сборка образа**: `docker build -t academic-api .`
2. **Запуск контейнера**:
   ```bash
   docker run --name academic-api-container -p 8000:8000 \
     -v ./db.sqlite3:/home/app/web/db.sqlite3 \
     -e SECRET_KEY="your-local-secret-key" \
     -e DEBUG=True \
     -e ALLOWED_HOSTS="127.0.0.1,localhost" \
     --rm -it academic-api
   ```
3. **Миграции** (в отдельном терминале): `docker exec -it academic-api-container python manage.py migrate`

## 📄 API Документация

После запуска сервера документация API доступна по адресам:

* **Swagger UI**: `http://127.0.0.1:8000/api/v1/schema/swagger-ui/`
* **ReDoc**: `http://127.0.0.1:8000/api/v1/schema/redoc/`
