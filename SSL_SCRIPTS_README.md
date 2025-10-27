# Автоматизация SSL сертификатов Let's Encrypt для reg.ru

Набор скриптов для автоматического создания и обновления SSL сертификатов Let's Encrypt с использованием DNS-валидации через API reg.ru.

## 📁 Содержимое проекта

- **letsencrypt_regru_dns.sh** - Bash скрипт (Linux) с certbot-dns-regru
- **letsencrypt_regru_api.py** - Python скрипт с прямым API интеграцией
- **letsencrypt_regru.ps1** - PowerShell скрипт (Windows)
- **config.json.example** - Пример файла конфигурации
- **USAGE.md** - Подробная инструкция по использованию

## 🚀 Быстрый старт

### Linux (Bash)

```bash
# 1. Отредактируйте конфигурацию в скрипте
nano letsencrypt_regru_dns.sh

# 2. Установите права
chmod +x letsencrypt_regru_dns.sh

# 3. Запустите
sudo ./letsencrypt_regru_dns.sh
```

### Linux (Python)

```bash
# 1. Создайте конфигурацию
sudo python3 letsencrypt_regru_api.py --create-config /etc/letsencrypt/regru_config.json

# 2. Отредактируйте конфигурацию
sudo nano /etc/letsencrypt/regru_config.json

# 3. Получите сертификат
sudo python3 letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json --obtain
```

### Windows (PowerShell)

```powershell
# 1. Создайте файл конфигурации config.json на основе config.json.example

# 2. Запустите скрипт
.\letsencrypt_regru.ps1 -ConfigFile .\config.json
```

## ⚙️ Конфигурация

Отредактируйте `config.json`:

```json
{
    "regru_username": "ваш_логин",
    "regru_password": "ваш_пароль",
    "domain": "dfv24.com",
    "wildcard": true,
    "email": "admin@dfv24.com"
}
```

## 📋 Требования

### Linux
- certbot
- Python 3.6+
- pip3
- requests, cryptography (Python модули)
- certbot-dns-regru (опционально)

### Windows
- certbot
- PowerShell 5.1+
- openssl (для проверки сертификатов)

## 🔄 Автоматическое обновление

### Через cron (Linux)

```bash
# Добавьте в crontab
sudo crontab -e

# Проверка каждый день в 3:00
0 3 * * * /usr/bin/python3 /path/to/letsencrypt_regru_api.py -c /etc/letsencrypt/regru_config.json
```

### Через Task Scheduler (Windows)

1. Откройте Task Scheduler
2. Создайте новую задачу
3. Триггер: Ежедневно в 3:00
4. Действие: Запуск PowerShell скрипта

## 📖 Функции

✅ Создание wildcard сертификатов (*.domain.com)  
✅ Автоматическая DNS-валидация через API reg.ru  
✅ Проверка срока действия сертификата  
✅ Автоматическое обновление перед истечением  
✅ Перезагрузка веб-сервера после обновления  
✅ Подробное логирование всех операций  

## 🔧 Использование с Nginx Proxy Manager

После получения сертификата:

1. Войдите в NPM: http://192.168.10.14:81/
2. SSL Certificates → Add SSL Certificate → Custom
3. Вставьте содержимое:
   - Certificate Key: `/etc/letsencrypt/live/domain.com/privkey.pem`
   - Certificate: `/etc/letsencrypt/live/domain.com/fullchain.pem`

## 📝 Логи

- Bash: `/var/log/letsencrypt_regru.log`
- Python: `/var/log/letsencrypt_regru.log`
- PowerShell: `.\letsencrypt_regru.log`
- Certbot: `/var/log/letsencrypt/letsencrypt.log`

## 🆘 Устранение неполадок

### Ошибка аутентификации API
- Проверьте учетные данные reg.ru
- Убедитесь, что домен под вашим управлением

### DNS запись не распространяется
- Увеличьте `dns_propagation_wait` до 120 секунд
- Проверьте DNS: `nslookup -type=TXT _acme-challenge.domain.com`

### Certbot не найден
```bash
# Ubuntu/Debian
sudo apt-get install certbot

# Или через snap
sudo snap install --classic certbot
```

## 📚 Документация

Подробная документация в файле [USAGE.md](USAGE.md)

## 🔐 Безопасность

- Храните учетные данные в безопасности
- Используйте `chmod 600` для конфигурационных файлов
- Регулярно обновляйте пароли

## ⚠️ Важно

- Let's Encrypt сертификаты действительны 90 дней
- Рекомендуется настроить автоматическое обновление
- Для wildcard сертификатов требуется DNS-валидация

## 📞 Поддержка

- [Документация reg.ru API](https://www.reg.ru/support/api)
- [Документация Let's Encrypt](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)

## 📄 Лицензия

Скрипты предоставляются "как есть" для свободного использования.

---

**Успешной автоматизации! 🔒**
