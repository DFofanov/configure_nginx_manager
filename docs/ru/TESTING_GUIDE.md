# 🧪 Руководство по тестированию SSL сертификатов

## Зачем нужны тестовые сертификаты?

Let's Encrypt имеет **строгие ограничения**:
- ⚠️ Максимум **5 сертификатов в неделю** на один домен
- ⚠️ Максимум **50 сертификатов в неделю** на аккаунт
- ⚠️ **Бан на 1 неделю** при превышении лимита

**Решение**: Используйте самоподписанные тестовые сертификаты для разработки!

---

## Быстрый старт

### Вариант 1: Через Makefile (рекомендуется)

```bash
# После установки скрипта (make install)
sudo make test-cert
```

**Результат**: Создан сертификат в `/etc/letsencrypt/live/ваш-домен/`

### Вариант 2: Через Python скрипт

```bash
sudo python3 letsencrypt_regru_api.py \
    --config /etc/letsencrypt/regru_config.json \
    --test-cert -v
```

### Вариант 3: Через Bash скрипт (автономный)

```bash
# Простой домен
sudo ./test_certificate.sh example.com no

# С wildcard
sudo ./test_certificate.sh example.com yes
```

---

## Сравнение методов

| Метод | Скорость | Требования | NPM интеграция | Лимиты |
|-------|----------|------------|----------------|--------|
| **Let's Encrypt** | 2-5 минут | Internet, DNS | ✅ Да | ⚠️ 5/неделю |
| **Тестовый (Python)** | 1-2 секунды | Только Python | ✅ Да | ✅ Нет |
| **Тестовый (Bash)** | 1-2 секунды | Только OpenSSL | ❌ Ручная | ✅ Нет |

---

## Детальная инструкция

### 1. Подготовка конфигурации

```bash
# Создать конфигурацию
sudo nano /etc/letsencrypt/regru_config.json
```

```json
{
    "domain": "test.example.com",
    "wildcard": true,
    "cert_dir": "/etc/letsencrypt/live",
    "npm_enabled": true,
    "npm_host": "https://npm.example.com",
    "npm_email": "admin@example.com",
    "npm_password": "your_password"
}
```

### 2. Создание тестового сертификата

```bash
sudo make test-cert
```

### 3. Проверка созданных файлов

```bash
ls -la /etc/letsencrypt/live/test.example.com/
# Должны быть:
# - privkey.pem     (приватный ключ)
# - cert.pem        (сертификат)
# - fullchain.pem   (полная цепочка)
# - chain.pem       (CA цепочка)
```

### 4. Просмотр информации о сертификате

```bash
openssl x509 -in /etc/letsencrypt/live/test.example.com/cert.pem -text -noout
```

---

## Использование в Nginx

### Прямое использование

```nginx
server {
    listen 443 ssl;
    server_name test.example.com;

    ssl_certificate /etc/letsencrypt/live/test.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/test.example.com/privkey.pem;

    # ... остальная конфигурация
}
```

### Через Nginx Proxy Manager

Если `npm_enabled: true` в конфигурации, сертификат автоматически загрузится в NPM.

**Проверка в NPM:**
1. Откройте веб-интерфейс NPM
2. Перейдите в **SSL Certificates**
3. Найдите ваш домен в списке
4. ⚠️ Будет помечен как "Custom" (не Let's Encrypt)

---

## Автоматизация тестирования

### Скрипт для CI/CD

```bash
#!/bin/bash
# test_ssl_integration.sh

set -e

echo "🧪 Тестирование SSL интеграции..."

# 1. Создать тестовый сертификат
sudo python3 letsencrypt_regru_api.py \
    --config test_config.json \
    --test-cert

# 2. Проверить файлы
if [ ! -f "/etc/letsencrypt/live/test.example.com/fullchain.pem" ]; then
    echo "❌ Сертификат не создан"
    exit 1
fi

# 3. Проверить валидность
openssl x509 -in /etc/letsencrypt/live/test.example.com/cert.pem -noout -checkend 0
if [ $? -eq 0 ]; then
    echo "✅ Сертификат валиден"
else
    echo "❌ Сертификат невалиден"
    exit 1
fi

# 4. Проверить загрузку в NPM (опционально)
# ... ваша проверка через API NPM

echo "✅ Все тесты пройдены"
```

### Makefile для тестирования

```makefile
.PHONY: test-ssl test-npm test-all

test-ssl:
	@echo "Создание тестового сертификата..."
	sudo make test-cert
	@echo "Проверка файлов..."
	test -f /etc/letsencrypt/live/$(DOMAIN)/fullchain.pem
	@echo "✅ SSL тест пройден"

test-npm:
	@echo "Проверка интеграции с NPM..."
	# Ваши проверки API NPM
	@echo "✅ NPM тест пройден"

test-all: test-ssl test-npm
	@echo "✅ Все тесты пройдены"
```

---

## Переход на production

### Шаг 1: Тестирование

```bash
# 1. Создать тестовый сертификат
sudo make test-cert

# 2. Проверить работу с NPM
# Открыть https://ваш-домен и проверить

# 3. Убедиться что все работает
```

### Шаг 2: Переключение на Let's Encrypt

```bash
# 1. Удалить тестовый сертификат
sudo rm -rf /etc/letsencrypt/live/ваш-домен/

# 2. Получить настоящий сертификат
sudo make obtain

# 3. Проверить обновление в NPM
sudo make status
```

---

## Частые вопросы

### Q: Почему браузер показывает предупреждение?

**A:** Самоподписанные сертификаты не доверяются браузерами. Это нормально для тестирования.

Чтобы избежать предупреждения в браузере (только для локального тестирования):
1. Chrome: `chrome://flags/#allow-insecure-localhost`
2. Firefox: Нажмите "Advanced" → "Accept the Risk"

### Q: Можно ли использовать для production?

**A:** ❌ **НЕТ!** Тестовые сертификаты только для разработки и тестирования.

### Q: Как часто можно создавать тестовые сертификаты?

**A:** ✅ Неограниченно! Нет никаких лимитов.

### Q: Загружаются ли в NPM автоматически?

**A:** ✅ Да, если `npm_enabled: true` в конфигурации.

### Q: Работают ли с wildcard доменами?

**A:** ✅ Да! Просто установите `"wildcard": true` в конфигурации.

### Q: Как проверить срок действия?

```bash
openssl x509 -in /etc/letsencrypt/live/ваш-домен/cert.pem -noout -dates
```

### Q: Как изменить срок действия?

Отредактируйте `validity_days` в функции `generate_self_signed_certificate()`:

```python
validity_days: int = 365  # Изменить на нужное количество дней
```

---

## Устранение проблем

### Ошибка: Permission denied

```bash
# Запускайте с sudo
sudo make test-cert
```

### Ошибка: Module 'cryptography' not found

```bash
# Установите зависимости
sudo pip3 install cryptography
```

### NPM не показывает сертификат

1. Проверьте настройки NPM в конфигурации
2. Проверьте логи: `sudo make logs`
3. Попробуйте загрузить вручную через веб-интерфейс NPM

### Сертификат не создается

```bash
# Проверьте права
ls -la /etc/letsencrypt/live/

# Создайте директорию вручную
sudo mkdir -p /etc/letsencrypt/live/

# Проверьте конфигурацию
sudo make check-config
```

---

## Примеры использования

### Разработка с Docker

```dockerfile
FROM nginx:alpine

# Копировать тестовый сертификат
COPY test-certs/ /etc/nginx/ssl/

# Конфигурация nginx
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 443
```

### Локальное тестирование

```bash
# Создать сертификат для localhost
sudo python3 letsencrypt_regru_api.py --test-cert

# Добавить в /etc/hosts
echo "127.0.0.1 test.example.com" | sudo tee -a /etc/hosts

# Запустить nginx
sudo nginx -t && sudo nginx -s reload

# Открыть в браузере
open https://test.example.com
```

### Автоматическое тестирование перед deployment

```bash
#!/bin/bash
# pre-deploy.sh

# Тестовая проверка SSL
sudo make test-cert
if [ $? -eq 0 ]; then
    echo "✅ Тестовый сертификат создан успешно"
    echo "✅ Готово к созданию production сертификата"
    sudo make obtain
else
    echo "❌ Ошибка при создании тестового сертификата"
    exit 1
fi
```

---

## Дополнительные ресурсы

- 📘 [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)
- 📘 [OpenSSL Documentation](https://www.openssl.org/docs/)
- 📘 [Nginx Proxy Manager Docs](https://nginxproxymanager.com/guide/)

---

## Итоговая шпаргалка

```bash
# Установка
sudo make install

# Конфигурация
sudo nano /etc/letsencrypt/regru_config.json

# Создать тестовый сертификат
sudo make test-cert

# Проверить
sudo make check-config
sudo make status

# Переход на production
sudo rm -rf /etc/letsencrypt/live/домен/
sudo make obtain

# Автоматическое обновление
sudo make run
```

**Готово!** 🎉 Теперь вы можете тестировать SSL сертификаты без ограничений!
