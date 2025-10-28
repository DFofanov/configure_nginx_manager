# Руководство по использованию letsencrypt_regru.sh

**Автор:** Фофанов Дмитрий  
**Дата:** 28.10.2025

## Описание

`letsencrypt_regru.sh` - это автоматический установщик для Let's Encrypt Manager с интеграцией reg.ru и Nginx Proxy Manager.

Скрипт автоматизирует:
- Установку всех системных зависимостей
- Создание виртуального окружения Python
- Установку Python библиотек (requests, cryptography, certbot)
- Интерактивную настройку конфигурации
- Создание и настройку systemd сервисов
- Настройку автоматического обновления сертификатов

## Требования

- Linux (Debian/Ubuntu, CentOS/RHEL/Fedora)
- Root доступ (sudo)
- Минимум 512MB RAM
- Минимум 1GB свободного места на диске
- Интернет соединение

## Быстрая установка

**Способ 1: Автоматическая установка (рекомендуется)**

Самый быстрый способ - запустить установку напрямую с GitHub:

```bash
sudo bash -c "$(curl -fsSL https://github.com/DFofanov/configure_nginx_manager/raw/refs/heads/master/letsencrypt_regru.sh)"
```

Эта команда:
- Автоматически скачает установочный скрипт
- Запустит его с правами root
- Проведет через интерактивную настройку

**Способ 2: Через клонирование репозитория**

Если вы хотите изучить код перед установкой:

```bash
# 1. Скачайте репозиторий
git clone https://github.com/DFofanov/configure_nginx_manager.git
cd configure_nginx_manager

# 2. Дайте права на выполнение
chmod +x letsencrypt_regru.sh

# 3. Запустите установку
sudo ./letsencrypt_regru.sh
```

## Интерактивная настройка

Во время установки скрипт спросит:

1. **Домен** - ваш основной домен (например, `example.com`)
2. **Email** - для уведомлений Let's Encrypt
3. **Учетные данные reg.ru:**
   - Имя пользователя
   - Пароль
4. **Wildcard сертификат** - создавать ли `*.example.com` (рекомендуется: Да)
5. **Интеграция с NPM** (опционально):
   - Адрес NPM (например, `http://192.168.10.14:81`)
   - Email для входа в NPM
   - Пароль NPM

## Структура после установки

```
/opt/letsencrypt-regru/           # Приложение
├── letsencrypt_regru_api.py      # Основной скрипт
├── venv/                         # Виртуальное окружение Python
└── docs/                         # Документация

/etc/letsencrypt-regru/           # Конфигурация
└── config.json                   # Настройки (credentials, домен, NPM)

/var/log/letsencrypt-regru/       # Логи
└── letsencrypt_regru.log

/etc/letsencrypt/live/            # Сертификаты Let's Encrypt
└── example.com/
    ├── privkey.pem
    ├── cert.pem
    ├── chain.pem
    └── fullchain.pem

/etc/systemd/system/              # Systemd сервисы
├── letsencrypt-regru.service     # Сервис обновления
└── letsencrypt-regru.timer       # Таймер (каждые 12 часов)

/usr/local/bin/
└── letsencrypt-regru             # Глобальная команда
```

## Использование команды letsencrypt-regru

После установки доступна удобная команда:

```bash
# Проверить срок действия текущего сертификата
letsencrypt-regru --check

# Получить новый сертификат Let's Encrypt
letsencrypt-regru --obtain

# Обновить существующий сертификат
letsencrypt-regru --renew

# Автоматически проверить и обновить при необходимости
letsencrypt-regru --auto

# Создать тестовый самоподписанный сертификат
letsencrypt-regru --test-cert

# Показать справку
letsencrypt-regru --help
```

## Автоматическое обновление

Установщик настраивает systemd timer для автоматической проверки:

```bash
# Проверить статус таймера
systemctl status letsencrypt-regru.timer

# Когда следующий запуск
systemctl list-timers letsencrypt-regru.timer

# Посмотреть историю запусков
journalctl -u letsencrypt-regru

# Следить за логами в реальном времени
journalctl -u letsencrypt-regru -f
```

### Настройки таймера

По умолчанию:
- Первый запуск: через 15 минут после загрузки системы
- Периодичность: каждые 12 часов
- Случайная задержка: до 1 часа (чтобы не создавать нагрузку)

Изменить можно в `/etc/systemd/system/letsencrypt-regru.timer`.

## Редактирование конфигурации

```bash
# Открыть конфигурацию в редакторе
sudo nano /etc/letsencrypt-regru/config.json

# После изменений перезапустите таймер
sudo systemctl restart letsencrypt-regru.timer
```

### Пример config.json

```json
{
    "regru_username": "your_username",
    "regru_password": "your_password",
    "domain": "example.com",
    "wildcard": true,
    "email": "admin@example.com",
    "cert_dir": "/etc/letsencrypt/live",
    "log_file": "/var/log/letsencrypt-regru/letsencrypt_regru.log",
    "dns_propagation_wait": 60,
    "dns_check_attempts": 10,
    "dns_check_interval": 10,
    "renewal_days": 30,
    "npm_enabled": true,
    "npm_host": "http://192.168.10.14:81",
    "npm_email": "admin@npm.local",
    "npm_password": "secure_password"
}
```

## Обновление приложения

```bash
# Скачайте последнюю версию
cd configure_nginx_manager
git pull

# Запустите обновление
sudo ./letsencrypt_regru.sh update
```

Обновление:
- Остановит таймер
- Обновит скрипт
- Обновит Python зависимости
- Перезапустит таймер

## Удаление

```bash
# Полное удаление приложения
sudo ./letsencrypt_regru.sh uninstall
```

Скрипт удалит:
- Приложение из `/opt/letsencrypt-regru/`
- Systemd сервисы
- Глобальную команду

Сертификаты в `/etc/letsencrypt/live/` сохраняются!

Опционально можно удалить:
- Конфигурацию `/etc/letsencrypt-regru/`
- Логи `/var/log/letsencrypt-regru/`

## Просмотр логов

```bash
# Логи systemd (рекомендуется)
journalctl -u letsencrypt-regru -f

# Файл лога
tail -f /var/log/letsencrypt-regru/letsencrypt_regru.log

# Последние 100 строк
tail -n 100 /var/log/letsencrypt-regru/letsencrypt_regru.log
```

## Устранение проблем

### Проверка установки

```bash
# Проверить наличие команды
which letsencrypt-regru

# Проверить Python окружение
ls -la /opt/letsencrypt-regru/venv/

# Проверить systemd сервисы
systemctl list-unit-files | grep letsencrypt-regru
```

### Ошибки при установке

**Ошибка: "Permission denied"**
```bash
# Запустите с sudo
sudo ./letsencrypt_regru.sh
```

**Ошибка: "Package not found"**
```bash
# Обновите списки пакетов
sudo apt-get update  # Debian/Ubuntu
sudo yum update      # CentOS/RHEL
```

**Ошибка: "Python module not found"**
```bash
# Переустановите виртуальное окружение
sudo rm -rf /opt/letsencrypt-regru/venv
sudo ./letsencrypt_regru.sh
```

### Проблемы с сертификатами

**Сертификат не создается**
```bash
# Проверьте логи
tail -n 50 /var/log/letsencrypt-regru/letsencrypt_regru.log

# Проверьте конфигурацию
cat /etc/letsencrypt-regru/config.json

# Попробуйте вручную
letsencrypt-regru --obtain -v
```

**DNS не обновляется**
```bash
# Увеличьте время ожидания в config.json
"dns_propagation_wait": 120,
"dns_check_attempts": 20
```

### Проблемы с NPM

**Не загружается в NPM**
```bash
# Проверьте доступность NPM
curl http://192.168.10.14:81

# Проверьте учетные данные в config.json
# Попробуйте вручную
letsencrypt-regru --test-cert -v
```

## Поддерживаемые ОС

✅ Debian 10, 11, 12  
✅ Ubuntu 20.04, 22.04, 24.04  
✅ CentOS 7, 8  
✅ RHEL 7, 8, 9  
✅ Fedora 35+  

## Дополнительные возможности

### Тестовый сертификат

Для тестирования без лимитов Let's Encrypt:

```bash
letsencrypt-regru --test-cert
```

Создаст самоподписанный сертификат на 90 дней.

### Ручной запуск обновления

```bash
# Запустить сервис вручную
sudo systemctl start letsencrypt-regru.service

# Посмотреть статус
systemctl status letsencrypt-regru.service
```

### Изменить периодичность проверки

Отредактируйте `/etc/systemd/system/letsencrypt-regru.timer`:

```ini
[Timer]
# Каждые 6 часов вместо 12
OnUnitActiveSec=6h
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl restart letsencrypt-regru.timer
```

## Безопасность

- Конфигурация с паролями имеет права `600` (только root)
- Приватные ключи сертификатов имеют права `600`
- Все операции выполняются от root
- Логи доступны только root

## Поддержка

- GitHub Issues: https://github.com/YOUR_USERNAME/configure_nginx_manager/issues
- Документация: `/opt/letsencrypt-regru/docs/`
- Email: admin@dfv24.com

---

**Разработано:** Фофанов Дмитрий  
**Дата:** 28.10.2025  
**Версия:** 2.0
