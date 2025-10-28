# Руководство по использованию скриптов для управления SSL сертификатами Let's Encrypt с DNS-валидацией через API reg.ru

## 🆕 Новое в версии 2.0

**Автоматическая интеграция с Nginx Proxy Manager!**

Python скрипт теперь автоматически загружает созданные сертификаты в Nginx Proxy Manager.

- ✅ Автоматическая загрузка сертификатов в NPM
- ✅ Автоматическое обновление существующих сертификатов
- ✅ Полная интеграция через API NPM
- ✅ Поддержка wildcard сертификатов

---

## Содержание
1. [Введение](#введение)
2. [⚡ Быстрая установка (letsencrypt_regru.sh)](#-быстрая-установка-letsencrypt_regrush)
3. [🔨 Сборка исполняемых файлов](#-сборка-исполняемых-файлов)
4. [Быстрый старт](#-быстрый-старт)
5. [Установка через Makefile](#-установка-через-makefile)
6. [Создание тестовых сертификатов](#-создание-тестового-самоподписанного-сертификата)
7. [Требования](#требования)
8. [Установка зависимостей](#установка-зависимостей)
9. [Настройка](#настройка)
10. [Использование Bash скрипта](#использование-bash-скрипта)
11. [Использование Python скрипта](#использование-python-скрипта)
12. [Интеграция с Nginx Proxy Manager](#интеграция-с-nginx-proxy-manager)
13. [Автоматическая проверка и обновление сертификатов](#автоматическая-проверка-и-обновление-сертификатов)
14. [Автоматизация обновления](#автоматизация-обновления)
15. [Устранение неполадок](#устранение-неполадок)

---

## Введение

В проекте представлены два скрипта для автоматического создания и обновления SSL сертификатов Let's Encrypt с использованием DNS-валидации через API reg.ru:

1. **letsencrypt_regru_dns.sh** - Bash скрипт с использованием плагина certbot-dns-regru
2. **letsencrypt_regru_api.py** - Python скрипт с прямым взаимодействием с API reg.ru и интеграцией с NPM

Оба скрипта поддерживают:
- Создание wildcard сертификатов (*.domain.com)
- Автоматическое обновление сертификатов
- DNS-валидацию через API reg.ru
- Логирование всех операций
- Перезагрузку веб-сервера после обновления

**Дополнительно Python скрипт поддерживает:**
- ✨ Автоматическую загрузку в Nginx Proxy Manager
- ✨ Автоматическое обновление сертификатов в NPM
- ✨ API интеграцию с NPM

---

## ⚡ Быстрая установка (letsencrypt_regru.sh)

**Автоматическая установка всего приложения одной командой!**

Скрипт `letsencrypt_regru.sh` автоматизирует весь процесс развертывания:
- ✅ Установка всех зависимостей (Python, certbot, библиотеки)
- ✅ Создание виртуального окружения Python
- ✅ Интерактивная настройка конфигурации
- ✅ Настройка systemd для автоматического обновления
- ✅ Создание удобных команд

### Установка

**Вариант 1: Автоматическая установка одной командой**

```bash
# Скачать и запустить установочный скрипт напрямую с GitHub
sudo bash -c "$(curl -fsSL https://github.com/DFofanov/configure_nginx_manager/raw/refs/heads/master/letsencrypt_regru.sh)"
```

**Вариант 2: Клонирование репозитория**

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/DFofanov/configure_nginx_manager.git
cd configure_nginx_manager

# 2. Запустите установку
sudo bash letsencrypt_regru.sh
```

**Интерактивная настройка:**

Скрипт спросит:
- Домен (например, example.com)
- Email для Let's Encrypt
- Учетные данные reg.ru
- Настройки NPM (опционально)


### Использование после установки

После установки доступна глобальная команда `letsencrypt-regru`:

```bash
# Проверить срок действия сертификата
letsencrypt-regru --check

# Получить новый сертификат Let's Encrypt
letsencrypt-regru --obtain

# Обновить существующий сертификат
letsencrypt-regru --renew

# Создать тестовый самоподписанный сертификат
letsencrypt-regru --test-cert

# Автоматическая проверка и обновление при необходимости
letsencrypt-regru --auto
```

### Автоматическое обновление

Скрипт установки настраивает автоматическую проверку сертификатов каждые 12 часов:

```bash
# Проверить статус автообновления
systemctl status letsencrypt-regru.timer

# Посмотреть логи
journalctl -u letsencrypt-regru -f

# Или в файле
tail -f /var/log/letsencrypt-regru/letsencrypt_regru.log
```

### Управление установкой

```bash
# Обновить приложение до последней версии
sudo bash letsencrypt_regru.sh update

# Полностью удалить приложение
sudo bash letsencrypt_regru.sh uninstall
```

### Расположение файлов

После установки файлы находятся:

| Тип | Путь |
|-----|------|
| Приложение | `/opt/letsencrypt-regru/` |
| Конфигурация | `/etc/letsencrypt-regru/config.json` |
| Логи | `/var/log/letsencrypt-regru/` |
| Сертификаты | `/etc/letsencrypt/live/` |
| Systemd сервис | `/etc/systemd/system/letsencrypt-regru.service` |
| Systemd таймер | `/etc/systemd/system/letsencrypt-regru.timer` |

### Редактирование конфигурации

```bash
# Отредактировать настройки
sudo nano /etc/letsencrypt-regru/config.json

# Перезапустить таймер после изменений
sudo systemctl restart letsencrypt-regru.timer
```

---

## 🚀 Установка через Makefile

**Самый быстрый способ установки на Linux!**

Makefile автоматизирует весь процесс установки, настройки systemd-сервисов и cron-заданий.

### Быстрая установка

```bash
# 1. Установка (требует root)
sudo make install

# 2. Редактирование конфигурации
sudo nano /etc/letsencrypt/regru_config.json

# 3. Проверка конфигурации
sudo make check-config

# 4. Тестовый запуск
sudo make test-run
```

### Доступные команды Makefile

#### Основные команды

```bash
# Установка всего: создание директорий, копирование скрипта, настройка systemd и cron
sudo make install

# Полное удаление: удаление службы, cron-задания, файлов
sudo make uninstall

# Показать статус установки, systemd и cron
sudo make status

# Справка по всем командам
make help
```

#### Утилиты

```bash
# Проверка JSON конфигурации на валидность
sudo make check-config

# Тестовый запуск без обновления cron/systemd
sudo make test-run

# Просмотр логов
sudo make logs

# Запуск скрипта напрямую
sudo make run

# Получение нового сертификата
sudo make obtain

# Обновление существующего сертификата
sudo make renew

# Создание тестового самоподписанного сертификата
sudo make test-cert

# Очистка логов
sudo make clean
```

### Что делает `make install`

1. **Создает директории**
   - `/opt/letsencrypt-regru/` - директория установки
   - `/var/log/letsencrypt/` - директория логов

2. **Устанавливает зависимости**
   ```bash
   pip3 install certbot requests cryptography
   ```

3. **Копирует скрипт**
   - Копирует `letsencrypt_regru_api.py` в `/opt/letsencrypt-regru/`
   - Устанавливает права на выполнение

4. **Создает конфигурацию**
   - Создает `/etc/letsencrypt/regru_config.json` (если не существует)
   - Устанавливает права 600 для безопасности

5. **Настраивает systemd**
   - Создает `letsencrypt-regru.service` - разовый запуск
   - Создает `letsencrypt-regru.timer` - таймер для ежедневного запуска
   - Включает и запускает таймер

6. **Настраивает cron**
   - Добавляет задание для запуска каждый день в 3:00 AM
   ```
   0 3 * * * /opt/letsencrypt-regru/letsencrypt_regru_api.py --config /etc/letsencrypt/regru_config.json --auto >> /var/log/letsencrypt/letsencrypt_regru.log 2>&1
   ```

### Что делает `make uninstall`

1. **Останавливает и удаляет службы**
   - Останавливает systemd timer и service
   - Удаляет файлы служб из `/etc/systemd/system/`
   - Перезагружает конфигурацию systemd

2. **Удаляет cron-задание**
   - Удаляет запись из crontab

3. **Удаляет файлы** (с подтверждением)
   - Удаляет `/opt/letsencrypt-regru/`
   - Опционально удаляет конфигурацию и логи

### Пример: Полная установка от А до Я

```bash
# 1. Клонируем или скачиваем проект
cd /tmp
git clone <repository-url>
cd configure_nginx_manager

# 2. Устанавливаем через Makefile
sudo make install

# 3. Редактируем конфигурацию
sudo nano /etc/letsencrypt/regru_config.json

# Вставляем реальные данные:
{
    "regru_username": "myuser",
    "regru_password": "mypassword",
    "domain": "example.com",
    "wildcard": true,
    "email": "admin@example.com",
    "renewal_days": 30,
    "npm_enabled": true,
    "npm_host": "https://npm.example.com",
    "npm_email": "admin@example.com",
    "npm_password": "npm_password"
}

# 4. Проверяем конфигурацию
sudo make check-config

# 5. Тестируем
sudo make test-run

# 6. Проверяем статус
sudo make status

# 7. Смотрим логи
sudo make logs
```

### Структура после установки

```
/opt/letsencrypt-regru/
├── letsencrypt_regru_api.py          # Основной скрипт

/etc/letsencrypt/
├── regru_config.json                 # Конфигурация (600)
└── live/                             # Сертификаты Let's Encrypt
    └── example.com/
        ├── fullchain.pem
        └── privkey.pem

/var/log/letsencrypt/
└── letsencrypt_regru.log             # Логи

/etc/systemd/system/
├── letsencrypt-regru.service         # Systemd сервис
└── letsencrypt-regru.timer           # Systemd таймер (ежедневно)
```

### Проверка работы автоматизации

```bash
# Статус systemd таймера
sudo systemctl status letsencrypt-regru.timer

# Когда будет следующий запуск
sudo systemctl list-timers letsencrypt-regru.timer

# Проверка cron
sudo crontab -l | grep letsencrypt

# Ручной запуск службы (для теста)
sudo systemctl start letsencrypt-regru.service

# Просмотр логов службы
sudo journalctl -u letsencrypt-regru.service -f
```

### Удаление

```bash
# Полное удаление
sudo make uninstall

# Система спросит подтверждение перед удалением конфигурации и логов
```

### 🧪 Создание тестового самоподписанного сертификата

**Идеально для тестирования без ограничений Let's Encrypt!**

Let's Encrypt имеет ограничения на количество сертификатов (5 в неделю на домен). Для тестирования и разработки можно использовать самоподписанные сертификаты.

#### Преимущества тестовых сертификатов

✅ **Нет ограничений** - создавайте сколько угодно сертификатов  
✅ **Мгновенное создание** - без DNS-валидации и ожидания  
✅ **Тестирование NPM** - проверка интеграции с Nginx Proxy Manager  
✅ **Офлайн работа** - не требуется интернет и API reg.ru  
✅ **Идентичная структура** - те же файлы, что и Let's Encrypt  

⚠️ **Ограничения**: Браузеры не доверяют самоподписанным сертификатам

#### Быстрое создание

```bash
# Создать тестовый сертификат
sudo make test-cert
```

Команда автоматически:
1. Генерирует RSA ключ 2048 бит
2. Создает самоподписанный сертификат на 90 дней
3. Поддерживает wildcard домены (если настроено)
4. Создает все необходимые файлы (privkey.pem, cert.pem, fullchain.pem, chain.pem)
5. Опционально загружает в Nginx Proxy Manager

#### Использование Python скрипта напрямую

```bash
# Создать тестовый сертификат с подробным выводом
sudo python3 /opt/letsencrypt-regru/letsencrypt_regru_api.py \
    --config /etc/letsencrypt/regru_config.json \
    --test-cert -v
```

#### Что создается

После выполнения команды будут созданы файлы:

```
/etc/letsencrypt/live/example.com/
├── privkey.pem      # Приватный ключ RSA 2048 бит
├── cert.pem         # Сертификат
├── fullchain.pem    # Полная цепочка (для nginx)
└── chain.pem        # Цепочка CA (пустой для самоподписанного)
```

#### Интеграция с NPM

Если в конфигурации включена интеграция с NPM (`npm_enabled: true`), тестовый сертификат автоматически загрузится в Nginx Proxy Manager:

```json
{
    "npm_enabled": true,
    "npm_host": "https://npm.example.com",
    "npm_email": "admin@example.com",
    "npm_password": "password"
}
```

#### Пример вывода

```
═══════════════════════════════════════════════════════════════
ГЕНЕРАЦИЯ ТЕСТОВОГО САМОПОДПИСАННОГО СЕРТИФИКАТА
═══════════════════════════════════════════════════════════════
Домен: example.com
Wildcard: True
Срок действия: 90 дней
⚠️  ВНИМАНИЕ: Это тестовый сертификат, не для production!

✓ Приватный ключ сохранен: /etc/letsencrypt/live/example.com/privkey.pem
✓ Сертификат сохранен: /etc/letsencrypt/live/example.com/cert.pem
✓ Fullchain сохранен: /etc/letsencrypt/live/example.com/fullchain.pem
✓ Chain файл создан: /etc/letsencrypt/live/example.com/chain.pem

═══════════════════════════════════════════════════════════════
ИНФОРМАЦИЯ О СЕРТИФИКАТЕ
═══════════════════════════════════════════════════════════════
Домен: example.com
Wildcard: *.example.com
Действителен с: 2025-10-27 12:00:00
Действителен до: 2026-01-25 12:00:00
```

#### Когда использовать тестовые сертификаты

**✅ Используйте для:**
- Локальной разработки и тестирования
- Проверки интеграции с Nginx Proxy Manager
- Тестирования автоматизации
- Разработки без доступа к интернету
- Избежания лимитов Let's Encrypt при частом тестировании

**❌ НЕ используйте для:**
- Production окружения
- Публичных веб-сайтов
- Любых случаев, где требуется доверие браузеров

#### Переход с тестового на production

После успешного тестирования легко переключиться на настоящий Let's Encrypt сертификат:

```bash
# 1. Удалить тестовый сертификат
sudo rm -rf /etc/letsencrypt/live/example.com/

# 2. Получить настоящий сертификат
sudo make obtain

# Или автоматически
sudo make run
```

---

## Требования

### Общие требования
- Операционная система: Linux (Ubuntu/Debian/CentOS)
- Права: root или sudo
- Домен зарегистрирован на reg.ru
- Доступ к API reg.ru (имя пользователя и пароль)

### Для Bash скрипта
- certbot
- certbot-dns-regru (плагин)
- curl
- jq
- openssl

### Для Python скрипта
- Python 3.6+
- certbot
- pip3
- Модули Python: requests, cryptography

---

## Установка зависимостей

### Ubuntu/Debian

```bash
# Обновление пакетов
sudo apt-get update

# Установка базовых зависимостей
sudo apt-get install -y certbot curl jq openssl python3 python3-pip

# Для Python скрипта
sudo pip3 install certbot-dns-regru requests cryptography

# Для Bash скрипта (если используете)
sudo pip3 install certbot-dns-regru
```

### CentOS/RHEL

```bash
# Обновление пакетов
sudo yum update -y

# Установка EPEL репозитория
sudo yum install -y epel-release

# Установка базовых зависимостей
sudo yum install -y certbot curl jq openssl python3 python3-pip

# Установка плагина
sudo pip3 install certbot-dns-regru requests cryptography
```

---

## Настройка

### 1. Получение учетных данных API reg.ru

1. Войдите в личный кабинет на сайте [reg.ru](https://www.reg.ru)
2. Перейдите в раздел "Управление API"
3. Используйте ваше имя пользователя и пароль для доступа к API
4. Убедитесь, что у вас есть права на управление DNS-записями

### 2. Настройка конфигурации

#### Для Python скрипта

Создайте файл конфигурации на основе примера:

```bash
# Создание примера конфигурации
sudo python3 letsencrypt_regru_api.py --create-config /etc/letsencrypt/regru_config.json

# Редактирование конфигурации
sudo nano /etc/letsencrypt/regru_config.json
```

Отредактируйте параметры:

```json
{
    "regru_username": "your_actual_username",
    "regru_password": "your_actual_password",
    "domain": "example.com",
    "wildcard": true,
    "email": "admin@example.com",
    "cert_dir": "/etc/letsencrypt/live",
    "log_file": "/var/log/letsencrypt_regru.log",
    "dns_propagation_wait": 60,
    "dns_check_attempts": 10,
    "dns_check_interval": 10
}
```

#### Для Bash скрипта

Отредактируйте переменные в начале скрипта:

```bash
sudo nano letsencrypt_regru_dns.sh
```

Измените следующие параметры:

```bash
REGRU_USERNAME="your_actual_username"
REGRU_PASSWORD="your_actual_password"
DOMAIN="example.com"
WILDCARD_DOMAIN="*.example.com"
EMAIL="admin@example.com"
```

### 3. Установка прав доступа

```bash
# Для Bash скрипта
sudo chmod +x letsencrypt_regru_dns.sh

# Для Python скрипта
sudo chmod +x letsencrypt_regru_api.py

# Защита файла конфигурации
sudo chmod 600 /etc/letsencrypt/regru_config.json
```

---

## Использование Bash скрипта

### Первый запуск (получение сертификата)

```bash
sudo ./letsencrypt_regru_dns.sh
```

Скрипт автоматически:
1. Проверит зависимости
2. Создаст файл с учетными данными
3. Установит плагин certbot-dns-regru (если не установлен)
4. Проверит наличие существующего сертификата
5. Получит новый сертификат или обновит существующий
6. Перезагрузит веб-сервер

### Просмотр логов

```bash
sudo tail -f /var/log/letsencrypt_regru.log
```

### Ручная проверка сертификата

```bash
sudo certbot certificates
```

---

## Использование Python скрипта

### Создание примера конфигурации

```bash
sudo python3 letsencrypt_regru_api.py --create-config /etc/letsencrypt/regru_config.json
```

### Получение нового сертификата

```bash
# С использованием конфигурационного файла
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json --obtain

# С подробным выводом
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json --obtain -v
```

### Обновление существующего сертификата

```bash
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json --renew
```

### Проверка срока действия сертификата

```bash
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json --check
```

### Автоматический режим (проверка и обновление)

```bash
# Скрипт сам определит, нужно ли обновление
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json
```

### Опции командной строки

```
-c, --config FILE       Путь к файлу конфигурации (JSON)
--create-config FILE    Создать пример файла конфигурации
--obtain                Получить новый сертификат
--renew                 Обновить существующий сертификат
--check                 Проверить срок действия сертификата
-v, --verbose           Подробный вывод
```

---

## � Сборка исполняемых файлов

### PyInstaller - компиляция в исполняемые файлы

Скрипт можно скомпилировать в исполняемый файл для Linux и Windows с помощью PyInstaller.

**Преимущества:**
- ✅ Не требуется установленный Python на целевой системе
- ✅ Все зависимости включены в один файл
- ✅ Простота распространения и развертывания

**Недостатки:**
- ❌ Большой размер (~40-60 MB)
- ❌ Certbot всё равно должен быть установлен в системе
- ❌ Медленный первый запуск

### Быстрая сборка

#### Для Linux:
```bash
make build-linux
```

#### Для Windows:
```bash
make build-windows
```

#### Для всех платформ:
```bash
make build-all
```

### Полный релиз с пакетами

```bash
# Создаст tar.gz для Linux и zip для Windows
make release
```

**Результат:**
- `dist/letsencrypt-regru` - Linux executable
- `dist/letsencrypt-regru.exe` - Windows executable  
- `dist/letsencrypt-regru-linux-x86_64.tar.gz`
- `dist/letsencrypt-regru-windows-x86_64.zip`

### Использование собранного файла

**Linux:**
```bash
# Установка
sudo cp dist/letsencrypt-regru /usr/local/bin/
sudo chmod +x /usr/local/bin/letsencrypt-regru

# Использование
sudo letsencrypt-regru --help
sudo letsencrypt-regru --check -c /etc/letsencrypt-regru/config.json
```

**Windows:**
```powershell
# Просто запустить
.\dist\letsencrypt-regru.exe --help
```

📖 **Подробнее:** См. [BUILD_GUIDE.md](BUILD_GUIDE.md) для детальных инструкций по сборке.

---

## �🚀 Быстрый старт

### За 3 простых шага получите SSL сертификат в Nginx Proxy Manager!

#### Шаг 1: Создайте конфигурацию

```bash
sudo python3 letsencrypt_regru_api.py --create-config /etc/letsencrypt/regru_config.json
```

#### Шаг 2: Отредактируйте параметры

```bash
sudo nano /etc/letsencrypt/regru_config.json
```

Заполните:

```json
{
    "regru_username": "ваш_логин_regru",
    "regru_password": "ваш_пароль_regru",
    "domain": "example.com",
    "wildcard": true,
    "email": "admin@example.com",
    
    "npm_enabled": true,
    "npm_host": "http://10.10.10.14:81",
    "npm_email": "admin@example.com",
    "npm_password": "changeme"
}
```

#### Шаг 3: Получите сертификат

```bash
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json --obtain
```

### ✅ Готово!

Откройте Nginx Proxy Manager → SSL Certificates

Ваш сертификат `*.example.com` готов к использованию! 🎉

**Что произошло:**
1. ✅ Создан wildcard сертификат через Let's Encrypt
2. ✅ Выполнена DNS-валидация через API reg.ru
3. ✅ Сертификат автоматически загружен в Nginx Proxy Manager
4. ✅ Веб-сервер перезагружен

---

## Интеграция с Nginx Proxy Manager

### Обзор возможностей

Скрипт `letsencrypt_regru_api.py` поддерживает автоматическое добавление и обновление SSL сертификатов в Nginx Proxy Manager через его API.

**Возможности:**
- ✅ Автоматическое добавление новых сертификатов в NPM
- ✅ Обновление существующих сертификатов в NPM
- ✅ Поиск сертификатов по доменному имени
- ✅ Поддержка wildcard сертификатов
- ✅ Полная синхронизация после создания/обновления

### Настройка интеграции

#### 1. Параметры конфигурации NPM

| Параметр | Описание | Пример |
|----------|----------|--------|
| `npm_enabled` | Включить интеграцию с NPM | `true` или `false` |
| `npm_host` | URL адрес NPM | `http://10.10.10.14:81` |
| `npm_email` | Email для входа в NPM | `admin@example.com` |
| `npm_password` | Пароль администратора NPM | `changeme` |

#### 2. Получение учетных данных NPM

1. Войдите в Nginx Proxy Manager: `http://10.10.10.14:81`
2. Используйте email и пароль администратора
3. По умолчанию:
   - Email: `admin@example.com`
   - Password: `changeme`
4. **ВАЖНО:** Измените пароль по умолчанию!

### Использование

#### Автоматическая синхронизация

После создания или обновления сертификата скрипт автоматически:
1. Авторизуется в Nginx Proxy Manager
2. Проверит, существует ли сертификат для домена
3. Создаст новый сертификат или обновит существующий
4. Загрузит файлы сертификата в NPM

#### Создание нового сертификата с автоматической загрузкой в NPM

```bash
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json --obtain
```

**Скрипт выполнит:**
- ✅ Создание сертификата через Let's Encrypt
- ✅ DNS-валидация через reg.ru API
- ✅ Автоматическая загрузка в NPM
- ✅ Перезагрузка веб-сервера

#### Обновление существующего сертификата

```bash
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json --renew
```

**Скрипт выполнит:**
- ✅ Обновление сертификата через certbot
- ✅ Автоматическое обновление в NPM
- ✅ Перезагрузка веб-сервера

#### Автоматический режим

```bash
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json
```

Скрипт автоматически определит:
- Нужно ли создать новый сертификат
- Требуется ли обновление (если осталось < 30 дней)
- Выполнит синхронизацию с NPM

### Работа с API Nginx Proxy Manager

#### Класс NginxProxyManagerAPI

Скрипт использует класс `NginxProxyManagerAPI` для работы с NPM:

```python
from letsencrypt_regru_api import NginxProxyManagerAPI

# Инициализация
npm_api = NginxProxyManagerAPI(
    host="http://10.10.10.14:81",
    email="admin@example.com",
    password="changeme",
    logger=logger
)

# Авторизация
npm_api.login()

# Получение списка сертификатов
certificates = npm_api.get_certificates()

# Поиск сертификата по домену
cert = npm_api.find_certificate_by_domain("example.com")

# Синхронизация сертификата
npm_api.sync_certificate("example.com", "/etc/letsencrypt/live/example.com")
```

#### API Endpoints

Скрипт использует следующие endpoints NPM API:

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/tokens` | POST | Авторизация |
| `/api/nginx/certificates` | GET | Список сертификатов |
| `/api/nginx/certificates` | POST | Создание сертификата |
| `/api/nginx/certificates/{id}` | PUT | Обновление сертификата |

### Логи и отладка

#### Просмотр логов

```bash
# Основной лог скрипта
sudo tail -f /var/log/letsencrypt_regru.log

# Подробный режим
sudo python3 letsencrypt_regru_api.py -c config.json --obtain -v
```

#### Примеры логов при успешной синхронизации

```
2025-10-27 10:30:15 - INFO - === Синхронизация сертификата с Nginx Proxy Manager ===
2025-10-27 10:30:15 - INFO - Авторизация в Nginx Proxy Manager...
2025-10-27 10:30:16 - INFO - Авторизация в NPM успешна
2025-10-27 10:30:16 - DEBUG - Получение списка сертификатов из NPM...
2025-10-27 10:30:16 - DEBUG - Получено 3 сертификатов
2025-10-27 10:30:16 - INFO - Создание нового сертификата в NPM
2025-10-27 10:30:16 - INFO - Загрузка сертификата для example.com в NPM...
2025-10-27 10:30:17 - INFO - Сертификат успешно загружен в NPM (ID: 4)
2025-10-27 10:30:17 - INFO - Сертификат успешно добавлен в Nginx Proxy Manager
```

### Устранение неполадок NPM

#### Ошибка: Не удалось авторизоваться в NPM

**Причины:**
- Неверный email или пароль
- NPM недоступен по указанному адресу
- Сетевые проблемы

**Решение:**
```bash
# Проверьте доступность NPM
curl http://10.10.10.14:81/api/

# Проверьте учетные данные
# Войдите в NPM через браузер с теми же учетными данными
```

#### Ошибка: Сертификат не загружен в NPM

**Причины:**
- Файлы сертификата не найдены
- Неправильный формат сертификата
- Проблемы с API NPM

**Решение:**
```bash
# Проверьте наличие файлов сертификата
ls -la /etc/letsencrypt/live/example.com/

# Проверьте права доступа
sudo chmod 644 /etc/letsencrypt/live/example.com/*.pem

# Попробуйте вручную
sudo python3 -c "
from letsencrypt_regru_api import NginxProxyManagerAPI
import logging
logger = logging.getLogger()
npm = NginxProxyManagerAPI('http://10.10.10.14:81', 'admin@example.com', 'changeme', logger)
npm.login()
print(npm.get_certificates())
"
```

#### Ошибка: API NPM возвращает 401 (Unauthorized)

**Решение:**
- Проверьте учетные данные в конфигурации
- Убедитесь, что пароль был изменен с дефолтного
- Попробуйте войти через веб-интерфейс

#### Ошибка: Сертификат создан, но не обновляется в NPM

**Причина:** Скрипт не может найти существующий сертификат

**Решение:**
```bash
# Просмотрите список сертификатов в NPM
# SSL Certificates → найдите сертификат для вашего домена

# Удалите старый сертификат вручную через UI
# Запустите скрипт снова - будет создан новый
```

### Безопасность NPM

#### Защита учетных данных

```bash
# Установите правильные права на конфигурацию
sudo chmod 600 /etc/letsencrypt/regru_config.json
sudo chown root:root /etc/letsencrypt/regru_config.json
```

#### Рекомендации

1. **Измените пароль NPM по умолчанию**
   ```
   Старый пароль: changeme
   Новый пароль: надежный_пароль
   ```

2. **Используйте HTTPS для NPM** (если доступно)
   ```json
   "npm_host": "https://10.10.10.14:443"
   ```

3. **Ограничьте доступ к API NPM**
   - Настройте firewall
   - Используйте VPN для удаленного доступа

### Проверка результата

#### В логах скрипта

```bash
sudo tail -n 50 /var/log/letsencrypt_regru.log | grep -i npm
```

#### В веб-интерфейсе NPM

1. Откройте NPM: `http://10.10.10.14:81`
2. Войдите в систему
3. Перейдите в **SSL Certificates**
4. Проверьте наличие сертификата для вашего домена
5. Проверьте дату истечения

#### В командной строке

```bash
# Список сертификатов в NPM через API
curl -X POST http://10.10.10.14:81/api/tokens \
  -H "Content-Type: application/json" \
  -d '{"identity":"admin@example.com","secret":"changeme"}' \
  | jq -r '.token' > /tmp/npm_token

curl -H "Authorization: Bearer $(cat /tmp/npm_token)" \
  http://10.10.10.14:81/api/nginx/certificates \
  | jq '.'
```

### Дополнительные возможности

#### Отключение синхронизации с NPM

Если нужно временно отключить синхронизацию:

```json
{
    "npm_enabled": false
}
```

#### Использование с несколькими доменами

Создайте отдельные конфигурационные файлы:

```bash
# Для домена 1
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/domain1_config.json

# Для домена 2
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/domain2_config.json
```

---

## Автоматическая проверка и обновление сертификатов

### Как это работает

Скрипт в автоматическом режиме (без флагов `--obtain` или `--renew`) выполняет интеллектуальную проверку:

#### 1. Проверка наличия сертификата

```bash
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json
```

**Если сертификата нет:**
- ✅ Создает новый сертификат через Let's Encrypt
- ✅ Выполняет DNS-валидацию через reg.ru
- ✅ Загружает сертификат в Nginx Proxy Manager (если включено)
- ✅ Перезагружает веб-сервер

#### 2. Проверка срока действия

**Если сертификат существует:**
- 🔍 Проверяет сколько дней осталось до истечения
- 📅 Сравнивает с порогом обновления (по умолчанию 30 дней)

**Если осталось меньше 30 дней:**
- 🔄 Автоматически обновляет сертификат
- ✅ Синхронизирует с Nginx Proxy Manager
- ✅ Перезагружает веб-сервер

**Если сертификат действителен (более 30 дней):**
- ℹ️  Выводит информацию о сертификате
- ✅ Проверяет наличие в NPM и синхронизирует при необходимости
- ⏭️  Завершает работу (обновление не требуется)

### Настройка порога обновления

В конфигурации можно изменить порог обновления:

```json
{
    "renewal_days": 30,  # За сколько дней до истечения обновлять
}
```

**Рекомендуемые значения:**
- `30` - по умолчанию (рекомендуется)
- `14` - для более консервативного подхода
- `60` - для раннего обновления

### Примеры работы скрипта

#### Сценарий 1: Сертификата нет

```bash
$ sudo python3 letsencrypt_regru_api.py -c config.json

============================================================
АВТОМАТИЧЕСКАЯ ПРОВЕРКА И ОБНОВЛЕНИЕ СЕРТИФИКАТА
============================================================
Порог обновления: 30 дней до истечения
Сертификат не найден
============================================================
СТАТУС: Сертификат не найден
ДЕЙСТВИЕ: Создание нового сертификата
============================================================
=== Запрос нового SSL сертификата ===
...
Сертификат успешно получен!
============================================================
СИНХРОНИЗАЦИЯ С NGINX PROXY MANAGER
============================================================
✅ Сертификат успешно создан в Nginx Proxy Manager
============================================================
ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО
============================================================
```

#### Сценарий 2: Сертификат истекает через 20 дней

```bash
$ sudo python3 letsencrypt_regru_api.py -c config.json

============================================================
АВТОМАТИЧЕСКАЯ ПРОВЕРКА И ОБНОВЛЕНИЕ СЕРТИФИКАТА
============================================================
Порог обновления: 30 дней до истечения
Сертификат истекает: 2025-11-16
Осталось дней: 20
============================================================
СТАТУС: Сертификат истекает через 20 дней
ДЕЙСТВИЕ: Обновление сертификата (порог: 30 дней)
============================================================
=== Обновление SSL сертификата ===
...
Проверка обновления завершена
============================================================
РЕЗУЛЬТАТ: Сертификат успешно обновлен
============================================================
✅ Сертификат успешно обновлен в Nginx Proxy Manager
```

#### Сценарий 3: Сертификат действителен (60 дней)

```bash
$ sudo python3 letsencrypt_regru_api.py -c config.json

============================================================
АВТОМАТИЧЕСКАЯ ПРОВЕРКА И ОБНОВЛЕНИЕ СЕРТИФИКАТА
============================================================
Порог обновления: 30 дней до истечения
Сертификат истекает: 2025-12-26
Осталось дней: 60
============================================================
СТАТУС: Сертификат действителен (60 дней)
ДЕЙСТВИЕ: Обновление не требуется
============================================================
Проверка синхронизации с Nginx Proxy Manager...
Сертификат найден в NPM (ID: 4)
```

### Ежедневная автоматическая проверка

Для ежедневной проверки и автоматического обновления настройте cron:

```bash
# Редактируем crontab
sudo crontab -e

# Добавляем задачу - проверка каждый день в 3:00 утра
0 3 * * * /usr/bin/python3 /path/to/letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json >> /var/log/letsencrypt_cron.log 2>&1
```

**Что будет происходить каждый день:**
1. 🕒 В 3:00 утра запускается скрипт
2. 🔍 Проверяет наличие и срок действия сертификата
3. 📊 Записывает результат в лог
4. 🔄 Обновляет сертификат только если нужно (< 30 дней)
5. ✅ Синхронизирует с NPM при обновлении

### Мониторинг работы

#### Просмотр логов ежедневной проверки

```bash
# Последние проверки
sudo tail -n 100 /var/log/letsencrypt_cron.log

# Фильтр по статусу
sudo grep "СТАТУС:" /var/log/letsencrypt_cron.log

# Фильтр по действиям
sudo grep "ДЕЙСТВИЕ:" /var/log/letsencrypt_cron.log

# Только успешные операции
sudo grep "ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО" /var/log/letsencrypt_cron.log
```

#### Проверка следующего запуска cron

```bash
# Список задач cron
sudo crontab -l

# Статус cron службы
sudo systemctl status cron
```

### Уведомления при обновлении

Добавьте email уведомления в cron:

```bash
# В начале crontab добавьте
MAILTO=admin@example.com

# Задача с уведомлениями
0 3 * * * /usr/bin/python3 /path/to/letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json 2>&1 | mail -s "SSL Certificate Check - $(date)" admin@example.com
```

---

## Автоматизация обновления

Let's Encrypt сертификаты действительны 90 дней. Рекомендуется настроить автоматическое обновление.

### Использование cron (для обоих скриптов)

#### Для Python скрипта

```bash
# Открыть crontab
sudo crontab -e

# Добавить задачу (проверка каждый день в 3:00 AM)
0 3 * * * /usr/bin/python3 /path/to/letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json >> /var/log/letsencrypt_cron.log 2>&1
```

#### Для Bash скрипта

```bash
# Открыть crontab
sudo crontab -e

# Добавить задачу (проверка каждый день в 3:00 AM)
0 3 * * * /path/to/letsencrypt_regru_dns.sh >> /var/log/letsencrypt_cron.log 2>&1
```

### Использование systemd timer

Создайте systemd service и timer для более гибкого управления:

#### Создание service файла

```bash
sudo nano /etc/systemd/system/letsencrypt-regru.service
```

Содержимое:

```ini
[Unit]
Description=Let's Encrypt Certificate Renewal with reg.ru DNS
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /path/to/letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Создание timer файла

```bash
sudo nano /etc/systemd/system/letsencrypt-regru.timer
```

Содержимое:

```ini
[Unit]
Description=Daily Let's Encrypt Certificate Check and Renewal
Requires=letsencrypt-regru.service

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=1h

[Install]
WantedBy=timers.target
```

#### Активация timer

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение и запуск timer
sudo systemctl enable letsencrypt-regru.timer
sudo systemctl start letsencrypt-regru.timer

# Проверка статуса
sudo systemctl status letsencrypt-regru.timer
sudo systemctl list-timers
```

---

## Устранение неполадок

### Проблема: Ошибка аутентификации API reg.ru

**Решение:**
- Проверьте правильность имени пользователя и пароля
- Убедитесь, что у вашего аккаунта есть доступ к API
- Проверьте, что домен находится под управлением вашего аккаунта

```bash
# Проверка доступа к API
curl -X POST "https://api.reg.ru/api/regru2/user/get_balance" \
  -d "username=YOUR_USERNAME" \
  -d "password=YOUR_PASSWORD" \
  -d "output_format=json"
```

### Проблема: DNS запись не распространяется

**Решение:**
- Увеличьте параметр `dns_propagation_wait` в конфигурации (например, до 120 секунд)
- Проверьте DNS записи вручную:

```bash
nslookup -type=TXT _acme-challenge.example.com
# или
dig TXT _acme-challenge.example.com
```

### Проблема: Certbot не установлен

**Решение:**

```bash
# Ubuntu/Debian
sudo apt-get install certbot

# CentOS/RHEL
sudo yum install certbot

# Или через snap
sudo snap install --classic certbot
```

### Проблема: Плагин certbot-dns-regru не найден

**Решение:**

```bash
# Установка через pip
sudo pip3 install certbot-dns-regru

# Или через pip3 с обновлением
sudo pip3 install --upgrade certbot-dns-regru
```

### Проблема: Недостаточно прав

**Решение:**
- Убедитесь, что запускаете скрипт от имени root или с sudo
- Проверьте права доступа к директории `/etc/letsencrypt/`

```bash
sudo chmod 755 /etc/letsencrypt/
sudo chown -R root:root /etc/letsencrypt/
```

### Проблема: Ошибка при перезагрузке веб-сервера

**Решение:**
- Проверьте, какой веб-сервер используется:

```bash
systemctl status nginx
systemctl status apache2
```

- Вручную перезагрузите веб-сервер:

```bash
# Для Nginx
sudo systemctl reload nginx

# Для Apache
sudo systemctl reload apache2
```

### Просмотр подробных логов certbot

```bash
# Логи certbot
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Логи скрипта
sudo tail -f /var/log/letsencrypt_regru.log
```

### Тестовый режим (staging)

Для тестирования используйте staging окружение Let's Encrypt:

```bash
# Добавьте опцию --staging к команде certbot
certbot certonly --staging --dns-regru ...
```

---

## Проверка полученного сертификата

### Просмотр информации о сертификате

```bash
# Просмотр всех сертификатов
sudo certbot certificates

# Просмотр конкретного сертификата
sudo openssl x509 -in /etc/letsencrypt/live/example.com/cert.pem -text -noout

# Проверка даты истечения
sudo openssl x509 -enddate -noout -in /etc/letsencrypt/live/example.com/cert.pem
```

### Проверка сертификата в браузере

1. Откройте ваш сайт в браузере: `https://example.com`
2. Нажмите на иконку замка в адресной строке
3. Проверьте информацию о сертификате
4. Убедитесь, что сертификат выдан Let's Encrypt и покрывает wildcard домен

### Онлайн проверка SSL

- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [SSL Shopper](https://www.sslshopper.com/ssl-checker.html)

---

## Использование сертификата в Nginx Proxy Manager

После получения сертификата вы можете использовать его в Nginx Proxy Manager:

### Вариант 1: Импорт существующего сертификата

1. Войдите в Nginx Proxy Manager: http://10.10.10.14:81/
2. Перейдите в **SSL Certificates** → **Add SSL Certificate**
3. Выберите **Custom**
4. Вставьте содержимое файлов:
   - Certificate Key: `/etc/letsencrypt/live/dfv24.com/privkey.pem`
   - Certificate: `/etc/letsencrypt/live/dfv24.com/fullchain.pem`
5. Сохраните сертификат

### Вариант 2: Прямая настройка Nginx

Если вы используете Nginx напрямую, добавьте в конфигурацию:

```nginx
server {
    listen 443 ssl http2;
    server_name dfv24.com *.dfv24.com;
    
    ssl_certificate /etc/letsencrypt/live/dfv24.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dfv24.com/privkey.pem;
    
    # Дополнительные SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... остальная конфигурация
}
```

---

## Дополнительная документация

- 📘 **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Полное руководство по созданию и использованию тестовых сертификатов
- � **[GITEA_SYNC.md](GITEA_SYNC.md)** - Настройка автоматической синхронизации Gitea → GitHub
- 📘 **[CHEATSHEET.md](CHEATSHEET.md)** - Быстрая шпаргалка по командам
- �🚀 **[Makefile](Makefile)** - Автоматизация установки и управления
- 📝 **[config.json.example](config.json.example)** - Пример конфигурации

---

## Поддержка и вопросы

При возникновении проблем:

1. Проверьте логи: `/var/log/letsencrypt_regru.log`
2. Проверьте логи certbot: `/var/log/letsencrypt/letsencrypt.log`
3. Используйте подробный режим: `-v` для Python скрипта
4. Проверьте документацию reg.ru API: https://www.reg.ru/support/api
5. Проверьте документацию Let's Encrypt: https://letsencrypt.org/docs/
6. **Для тестирования**: См. [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

## Заключение

Оба скрипта предоставляют надежное решение для автоматического управления SSL сертификатами Let's Encrypt с использованием DNS-валидации через API reg.ru. 

**Рекомендации:**
- Используйте Python скрипт для более гибкой настройки и интеграции
- Используйте Bash скрипт для простоты и минимальных зависимостей
- **Используйте тестовые сертификаты для разработки** (без лимитов Let's Encrypt)
- Настройте автоматическое обновление через cron или systemd timer
- Регулярно проверяйте логи и статус сертификатов
- Храните учетные данные в безопасности (chmod 600)

**Быстрый старт для тестирования:**
```bash
sudo make install           # Установка
sudo make test-cert         # Создать тестовый сертификат
sudo make obtain            # Получить production сертификат
```

Успешной автоматизации! 🔒

---

## 🔄 Синхронизация Gitea → GitHub

Проект поддерживает автоматическую синхронизацию из Gitea в GitHub.

### Быстрая настройка

**Метод 1: Git Hook (мгновенно)**
```bash
# На сервере Gitea скопируйте hook
cp gitea-hooks/post-receive /path/to/repo.git/hooks/
chmod +x /path/to/repo.git/hooks/post-receive
```

**Метод 2: GitHub Actions (каждый час)**
- Workflow уже настроен в `.github/workflows/sync-from-gitea.yml`
- Добавьте секреты `GITEA_URL` и `GITEA_TOKEN` в GitHub

**Подробная документация**: См. [GITEA_SYNC.md](GITEA_SYNC.md)

---
