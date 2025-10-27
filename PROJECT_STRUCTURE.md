# 📁 Структура проекта configure_nginx_manager

## Основные скрипты

### Python (Рекомендуется)
- **letsencrypt_regru_api.py** (1,411 строк)
  - Полнофункциональный Python скрипт
  - Прямая работа с API reg.ru
  - Интеграция с Nginx Proxy Manager
  - Автоматическая проверка и обновление сертификатов
  - Генерация тестовых самоподписанных сертификатов
  - Поддержка wildcard доменов

### Bash
- **letsencrypt_regru_dns.sh**
  - Bash скрипт с certbot-dns-regru плагином
  - Простота использования
  - Минимальные зависимости

### PowerShell
- **letsencrypt_regru.ps1**
  - Windows версия
  - Аналогична Bash скрипту

### Тестирование
- **test_certificate.sh**
  - Быстрое создание тестовых сертификатов через OpenSSL
  - Автономная работа без Python
  - Поддержка wildcard доменов

## Автоматизация

### Makefile
- **Makefile** (415 строк)
  - `make install` - Полная установка и настройка
  - `make uninstall` - Чистое удаление
  - `make status` - Проверка состояния
  - `make test-cert` - Создание тестового сертификата
  - `make obtain` - Получение Let's Encrypt сертификата
  - `make renew` - Обновление сертификата
  - `make logs` - Просмотр логов
  - `make check-config` - Валидация конфигурации

## Конфигурация

### config.json.example
Пример конфигурации со всеми параметрами:
- Учетные данные reg.ru API
- Настройки домена и email
- Параметры обновления (renewal_days)
- Настройки Nginx Proxy Manager
- Пути к директориям и логам

## Документация

### README.md (1,420+ строк)
Основная документация:
- Введение и возможности
- Быстрый старт
- Установка через Makefile
- Создание тестовых сертификатов
- Требования и установка зависимостей
- Настройка и использование
- Интеграция с NPM
- Автоматическая проверка и обновление
- Автоматизация через cron/systemd
- Устранение неполадок

### TESTING_GUIDE.md (370+ строк)
Руководство по тестированию:
- Зачем нужны тестовые сертификаты
- Обход лимитов Let's Encrypt (5 в неделю)
- Быстрый старт с тестовыми сертификатами
- Сравнение методов создания
- Использование в разработке
- Автоматизация тестирования
- Переход с тестовых на production
- Частые вопросы
- Примеры для CI/CD и Docker

### PROJECT_STRUCTURE.md (этот файл)
- Описание всех файлов проекта
- Краткая характеристика каждого компонента

## Вспомогательные файлы

### Markdown документы
- **Add Let's Encrypt Certificate для провайдера reg.ru.md**
  - Первоначальные инструкции
  
- **Создание и продление SSL сертификата.md**
  - Дополнительная информация о процессе

## Возможности

### ✅ Основные
- [x] Создание Let's Encrypt сертификатов через reg.ru DNS API
- [x] Wildcard сертификаты (*.domain.com)
- [x] Автоматическое обновление сертификатов
- [x] DNS-01 валидация
- [x] Интеграция с Nginx Proxy Manager
- [x] Автоматическая загрузка/обновление в NPM

### ✅ Продвинутые
- [x] Автоматическая проверка срока действия
- [x] Настраиваемый порог обновления (renewal_days)
- [x] Systemd service + timer
- [x] Cron автоматизация
- [x] Подробное логирование
- [x] Валидация конфигурации

### 🆕 Тестирование
- [x] Генерация самоподписанных тестовых сертификатов
- [x] Обход лимитов Let's Encrypt (5/неделю)
- [x] Мгновенное создание без DNS
- [x] Интеграция тестовых сертификатов с NPM
- [x] Полная совместимость структуры с Let's Encrypt

## Установка

### Быстрая установка
```bash
sudo make install
sudo nano /etc/letsencrypt/regru_config.json
sudo make test-cert  # Для тестирования
sudo make obtain     # Для production
```

### Структура после установки
```
/opt/letsencrypt-regru/
├── letsencrypt_regru_api.py

/etc/letsencrypt/
├── regru_config.json
└── live/
    └── example.com/
        ├── privkey.pem
        ├── cert.pem
        ├── fullchain.pem
        └── chain.pem

/etc/systemd/system/
├── letsencrypt-regru.service
└── letsencrypt-regru.timer

/var/log/letsencrypt/
└── letsencrypt_regru.log
```

## Использование

### Тестирование (без лимитов)
```bash
sudo make test-cert              # Создать тестовый сертификат
sudo make status                 # Проверить статус
```

### Production
```bash
sudo make obtain                 # Получить Let's Encrypt сертификат
sudo make renew                  # Обновить сертификат
sudo make run                    # Автоматический режим
```

### Мониторинг
```bash
sudo make logs                   # Просмотр логов
sudo make status                 # Статус служб
sudo make check-config           # Проверка конфигурации
```

## Технологии

- **Python 3.6+** - Основной язык
- **Certbot** - Let's Encrypt клиент
- **requests** - HTTP запросы к API
- **cryptography** - Генерация тестовых сертификатов
- **systemd** - Автоматизация запуска
- **cron** - Альтернативная автоматизация
- **Make** - Управление установкой
- **OpenSSL** - Альтернативная генерация сертификатов

## Лицензия

Open Source - свободное использование

## Автор

GitHub Copilot @ 2025

## Поддержка

См. документацию:
- [README.md](README.md) - Основное руководство
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Руководство по тестированию

---

**Версия**: 2.1  
**Дата**: 27 октября 2025  
**Статус**: ✅ Production Ready
