# Руководство по использованию скриптов для управления SSL сертификатами Let's Encrypt с DNS-валидацией через API reg.ru

## Содержание
1. [Введение](#введение)
2. [Требования](#требования)
3. [Установка зависимостей](#установка-зависимостей)
4. [Настройка](#настройка)
5. [Использование Bash скрипта](#использование-bash-скрипта)
6. [Использование Python скрипта](#использование-python-скрипта)
7. [Автоматизация обновления](#автоматизация-обновления)
8. [Устранение неполадок](#устранение-неполадок)

---

## Введение

В проекте представлены два скрипта для автоматического создания и обновления SSL сертификатов Let's Encrypt с использованием DNS-валидации через API reg.ru:

1. **letsencrypt_regru_dns.sh** - Bash скрипт с использованием плагина certbot-dns-regru
2. **letsencrypt_regru_api.py** - Python скрипт с прямым взаимодействием с API reg.ru

Оба скрипта поддерживают:
- Создание wildcard сертификатов (*.domain.com)
- Автоматическое обновление сертификатов
- DNS-валидацию через API reg.ru
- Логирование всех операций
- Перезагрузку веб-сервера после обновления

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
    "domain": "dfv24.com",
    "wildcard": true,
    "email": "admin@dfv24.com",
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
DOMAIN="dfv24.com"
WILDCARD_DOMAIN="*.dfv24.com"
EMAIL="admin@dfv24.com"
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
nslookup -type=TXT _acme-challenge.dfv24.com
# или
dig TXT _acme-challenge.dfv24.com
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
sudo openssl x509 -in /etc/letsencrypt/live/dfv24.com/cert.pem -text -noout

# Проверка даты истечения
sudo openssl x509 -enddate -noout -in /etc/letsencrypt/live/dfv24.com/cert.pem
```

### Проверка сертификата в браузере

1. Откройте ваш сайт в браузере: `https://dfv24.com`
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

1. Войдите в Nginx Proxy Manager: http://192.168.10.14:81/
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

## Поддержка и вопросы

При возникновении проблем:

1. Проверьте логи: `/var/log/letsencrypt_regru.log`
2. Проверьте логи certbot: `/var/log/letsencrypt/letsencrypt.log`
3. Используйте подробный режим: `-v` для Python скрипта
4. Проверьте документацию reg.ru API: https://www.reg.ru/support/api
5. Проверьте документацию Let's Encrypt: https://letsencrypt.org/docs/

---

## Заключение

Оба скрипта предоставляют надежное решение для автоматического управления SSL сертификатами Let's Encrypt с использованием DNS-валидации через API reg.ru. 

**Рекомендации:**
- Используйте Python скрипт для более гибкой настройки и интеграции
- Используйте Bash скрипт для простоты и минимальных зависимостей
- Настройте автоматическое обновление через cron или systemd timer
- Регулярно проверяйте логи и статус сертификатов
- Храните учетные данные в безопасности (chmod 600)

Успешной автоматизации! 🔒
