# Руководство по развертыванию

В этом руководстве описывается процесс развертывания Django-приложения на чистой виртуальной машине с ОС Linux (
например, Ubuntu 22.04) с использованием Docker и **Caddy** в качестве реверс-прокси и балансировщика.

### Обзор стека

* **Операционная система**: Ubuntu 22.04 LTS (или другой современный дистрибутив Linux).
* **Контейнеризация**: Docker.
* **Приложение**: Django-проект, запущенный с помощью Gunicorn внутри Docker-контейнера.
* **Реверс-прокси / Веб-сервер**: Caddy (для простоты настройки и автоматического HTTPS).

### Шаг 1: Подготовка сервера

1. **Подключитесь к вашему серверу по SSH.**

2. **Установите Docker:**
   Следуйте [официальной инструкции](https://docs.docker.com/engine/install/ubuntu/) для установки Docker Engine.

3. **Установите Git:**
   ```bash
   sudo apt update
   sudo apt install git -y
   ```

4. **Клонируйте репозиторий:**
   ```bash
   git clone <your-repository-url>
   cd academic-difference-api
   ```

### Шаг 2: Установка и настройка Caddy

Caddy будет принимать весь внешний трафик (включая HTTPS), автоматически получать и обновлять SSL-сертификаты и
проксировать запросы к нашему Django-приложению, работающему в Docker.

1. **Установите Caddy:**
   Следуйте [официальной инструкции](https://caddyserver.com/docs/install#debian-ubuntu-raspbian) для вашего
   дистрибутива.

2. **Создайте файл конфигурации `Caddyfile`:**
   В директории проекта создайте файл `Caddyfile`:
   ```bash
   nano Caddyfile
   ```
   Вставьте в него следующее содержимое, заменив `your-domain.com` на ваш реальный домен:
   ```caddy
   your-domain.com {
       # Автоматически настраивает HTTPS с помощью Let's Encrypt

       # Проксируем все запросы к нашему Django-приложению,
       # работающему на порту 8000
       reverse_proxy localhost:8000
   }
   ```

3. **Запустите Caddy:**
   Перейдите в директорию с `Caddyfile` и запустите его. Caddy автоматически уйдет в фон.
   ```bash
   caddy start
   ```

### Шаг 3: Сборка и запуск Docker-контейнера

1. **Соберите Docker-образ:**
   ```bash
   docker build -t academic-api .
   ```

2. **Создайте Docker Volume для базы данных:**
   Это самый надежный способ хранить данные. Volume переживет перезапуски и удаления контейнеров.
   ```bash
   docker volume create academic-api-db-data
   ```

3. **Запустите контейнер приложения:**
   Эта команда запустит контейнер в фоновом режиме, будет автоматически перезапускать его и примонтирует том с базой
   данных.

   **ВНИМАНИЕ:** Замените `your-super-secret-production-key` на сгенерированный вами ключ и укажите ваш домен в
   `ALLOWED_HOSTS`.
   ```bash
   docker run --name academic-api-container -p 8000:8000 \
     -v academic-api-db-data:/home/app/web \
     -e SECRET_KEY="your-super-secret-production-key" \
     -e DEBUG=False \
     -e ALLOWED_HOSTS="your-domain.com" \
     --restart unless-stopped \
     -d \
     academic-api
   ```

### Шаг 4: Начальная настройка приложения

1. **Выполните миграции базы данных:**
   ```bash
   docker exec academic-api-container python manage.py migrate
   ```

2. **Создайте суперпользователя (если необходимо):**
   ```bash
   docker exec -it academic-api-container python manage.py createsuperuser
   ```

### Шаг 5: Проверка

Откройте в браузере `https://your-domain.com/api/v1/schema/swagger-ui/`. Вы должны увидеть документацию вашего API,
работающую через защищенное HTTPS-соединение!

### Резервное копирование базы данных (SQLite)

Вы можете настроить cron-задание для регулярного создания бэкапов.

1. Создайте директорию для бэкапов внутри volume:
   ```bash
   docker exec academic-api-container mkdir -p /home/app/web/backups
   ```
2. Команда для создания бэкапа:
   ```bash
   docker exec academic-api-container sqlite3 db.sqlite3 ".backup '/home/app/web/backups/backup-$(date +%Y-%m-%d-%H%M%S).sqlite3'"
   ```
3. Чтобы скопировать бэкапы на хост-машину, используйте команду `docker cp`:
   ```bash
   # Пример копирования всех бэкапов в домашнюю директорию на сервере
   docker cp academic-api-container:/home/app/web/backups/. ~/backups/
   ```
