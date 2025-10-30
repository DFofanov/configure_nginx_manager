# ⚡ Шпаргалка по SSL сертификатам

## 🚀 Быстрый старт

### Установка за 3 команды
```bash
sudo make install
sudo nano /etc/letsencrypt/regru_config.json  # Заполнить данные
sudo make test-cert                            # Тест
```

---

## 🧪 Тестирование (БЕЗ лимитов Let's Encrypt)

```bash
# Создать тестовый сертификат (неограниченно)
sudo make test-cert

# Проверить статус
sudo make status

# Просмотреть логи
sudo make logs
```

**Когда использовать:**
- ⚠️ Let's Encrypt: макс. 5 сертификатов/неделю
- ✅ Тестовые: НЕОГРАНИЧЕННО
- ⚡ Создание: 1-2 секунды vs 2-5 минут

---

## 🔒 Production (Let's Encrypt)

```bash
# Получить настоящий сертификат
sudo make obtain

# Автоматический режим (проверка + обновление)
sudo make run

# Принудительное обновление
sudo make renew
```

---

## 📋 Основные команды

### Команды letsencrypt-regru

| Команда | Описание | Лимиты | Использование |
|---------|----------|--------|---------------|
| `--check` | Проверить срок действия | - | Мониторинг |
| `--obtain` | Получить новый сертификат | ⚠️ 5/неделю | Первое создание |
| `--renew` | Обновить существующий | ⚠️ 5/неделю | Продление |
| `--auto` | Авто-проверка и обновление | ⚠️ 5/неделю | Cron/systemd |
| `--test-cert` | Тестовый сертификат | ✅ Нет | Разработка |
| `--test-api` | Проверить API reg.ru | - | Диагностика |
| `--test-dns` | Тест создания DNS записи | - | Проверка перед SSL |
| `--help` | Справка | - | Помощь |
| `-v` | Подробный вывод | - | Отладка |

### Команды Makefile

| Команда | Описание | Эквивалент |
|---------|----------|------------|
| `make test-cert` | Тестовый сертификат | `letsencrypt-regru --test-cert` |
| `make obtain` | Let's Encrypt новый | `letsencrypt-regru --obtain` |
| `make renew` | Обновить существующий | `letsencrypt-regru --renew` |
| `make run` | Авто-режим | `letsencrypt-regru --auto` |
| `make status` | Статус системы | - |
| `make logs` | Показать логи | `journalctl -u letsencrypt-regru` |
| `make check-config` | Проверить конфигурацию | - |

### Команды letsencrypt_regru.sh

| Команда | Описание |
|---------|----------|
| `sudo bash letsencrypt_regru.sh install` | Установить приложение |
| `sudo bash letsencrypt_regru.sh update` | Обновить приложение |
| `sudo bash letsencrypt_regru.sh uninstall` | Удалить приложение |

---

## 📝 Конфигурация

### Минимальная (тестирование)
```json
{
    "domain": "test.example.com",
    "wildcard": true,
    "cert_dir": "/etc/letsencrypt/live"
}
```

### Полная (production + NPM)
```json
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
```

---

## 🔄 Workflow

### Разработка → Production

```bash
# 1. Разработка (тестовые сертификаты)
sudo make test-cert              # Создать тестовый
# Тестировать приложение...

# 2. Production (Let's Encrypt)
sudo rm -rf /etc/letsencrypt/live/example.com/  # Удалить тест
sudo make obtain                 # Создать production
```

---

## 📁 Важные пути

```bash
# Конфигурация
/etc/letsencrypt/regru_config.json

# Сертификаты
/etc/letsencrypt/live/example.com/
├── privkey.pem      # Приватный ключ
├── cert.pem         # Сертификат
├── fullchain.pem    # Полная цепочка (для nginx)
└── chain.pem        # CA цепочка

# Скрипты
/opt/letsencrypt-regru/letsencrypt_regru_api.py

# Логи
/var/log/letsencrypt_regru.log
```

---

## 🔍 Проверка

```bash
# Проверить конфигурацию
sudo make check-config

# Проверить сертификат
openssl x509 -in /etc/letsencrypt/live/example.com/cert.pem -text -noout

# Проверить срок действия
openssl x509 -in /etc/letsencrypt/live/example.com/cert.pem -noout -dates

# Проверить systemd
sudo systemctl status letsencrypt-regru.timer
sudo systemctl list-timers letsencrypt-regru.timer

# Проверить cron
sudo crontab -l | grep letsencrypt
```

---

## 🐛 Отладка

```bash
# Подробные логи
sudo make logs

# Тестовый запуск с подробностями
sudo python3 /opt/letsencrypt-regru/letsencrypt_regru_api.py \
    -c /etc/letsencrypt/regru_config.json --check -v

# Логи certbot
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Логи systemd
sudo journalctl -u letsencrypt-regru.service -f
```

---

## ⚠️ Частые ошибки

### Let's Encrypt: Rate limit exceeded
```bash
# РЕШЕНИЕ: Используйте тестовые сертификаты
sudo make test-cert
```

### NPM: Certificate not found
```bash
# РЕШЕНИЕ: Проверьте настройки NPM
sudo make check-config

# Проверьте подключение
curl -k https://npm.example.com
```

### Permission denied
```bash
# РЕШЕНИЕ: Запускайте с sudo
sudo make test-cert
```

---

## 🎯 Сценарии использования

### Локальная разработка
```bash
sudo make test-cert
# Открыть https://localhost (игнорировать предупреждение)
```

### CI/CD тестирование
```bash
# В pipeline
sudo make test-cert
# Запустить тесты...
sudo make status
```

### Staging окружение
```bash
sudo make test-cert  # Или
sudo make obtain     # Если есть домен
```

### Production окружение
```bash
sudo make install
sudo make obtain
# Автоматическое обновление через cron/systemd
```

---

## 📚 Документация

- **README.md** - Полное руководство (1420+ строк)
- **TESTING_GUIDE.md** - Тестирование (370+ строк)
- **PROJECT_STRUCTURE.md** - Структура проекта
- **CHEATSHEET.md** - Эта шпаргалка

---

## 🆘 Быстрая помощь

```bash
# Показать все команды
make help

# Проверить установку
sudo make status

# Полная переустановка
sudo make uninstall
sudo make install
```

---

## 💡 Советы

1. **Всегда начинайте с тестовых сертификатов** - избегайте лимитов
2. **Проверяйте конфигурацию** - `make check-config`
3. **Мониторьте логи** - `make logs`
4. **Автоматизируйте** - systemd/cron уже настроены
5. **Храните бэкапы** конфигурации

---

**Версия**: 2.1  
**Обновлено**: 27.10.2025
