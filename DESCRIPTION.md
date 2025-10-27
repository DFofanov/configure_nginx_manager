# 🔒 SSL Certificate Manager для Let's Encrypt + reg.ru

**Автоматическое управление SSL сертификатами Let's Encrypt с DNS-валидацией через API reg.ru и интеграцией с Nginx Proxy Manager**

## 📖 Описание

Комплексное решение для автоматизации создания, обновления и управления SSL сертификатами Let's Encrypt для доменов, зарегистрированных на reg.ru. Поддерживает DNS-01 валидацию, wildcard сертификаты, автоматическую загрузку в Nginx Proxy Manager и генерацию тестовых сертификатов для разработки.

### ✨ Основные возможности

- 🔐 **Автоматическое получение SSL сертификатов** через Let's Encrypt
- 🌐 **DNS-01 валидация** через API reg.ru (поддержка wildcard доменов)
- 🔄 **Автоматическое обновление** сертификатов с настраиваемым порогом
- 📦 **Интеграция с Nginx Proxy Manager** - автоматическая загрузка и обновление
- 🧪 **Тестовые сертификаты** - обход лимитов Let's Encrypt (5 в неделю)
- ⚙️ **Полная автоматизация** через systemd/cron
- 🔀 **Синхронизация репозиториев** - автоматическая синхронизация Gitea → GitHub

### 🚀 Быстрый старт

```bash
# Установка через Makefile
sudo make install

# Настройка конфигурации
sudo nano /etc/letsencrypt/regru_config.json

# Создание тестового сертификата (без лимитов)
sudo make test-cert

# Получение production сертификата
sudo make obtain
```

### 📋 Требования

- **ОС**: Linux (Ubuntu/Debian/CentOS)
- **Python**: 3.6+
- **Зависимости**: certbot, requests, cryptography
- **API**: reg.ru (доступ к DNS управлению)
- **Опционально**: Nginx Proxy Manager

### 🎯 Сценарии использования

- ✅ Автоматизация SSL сертификатов для web-серверов
- ✅ Централизованное управление через Nginx Proxy Manager
- ✅ Тестирование и разработка с самоподписанными сертификатами
- ✅ CI/CD интеграция
- ✅ Мультидоменные конфигурации с wildcard

### 📚 Документация

- [README.md](README.md) - Полное руководство (1400+ строк)
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Руководство по тестированию
- [GITEA_SYNC.md](GITEA_SYNC.md) - Синхронизация Gitea → GitHub
- [CHEATSHEET.md](CHEATSHEET.md) - Быстрая шпаргалка

---

## 📖 Description (English)

**Automated Let's Encrypt SSL Certificate Manager with DNS validation via reg.ru API and Nginx Proxy Manager integration**

Comprehensive solution for automating the creation, renewal, and management of Let's Encrypt SSL certificates for domains registered with reg.ru. Supports DNS-01 validation, wildcard certificates, automatic upload to Nginx Proxy Manager, and test certificate generation for development.

### ✨ Key Features

- 🔐 **Automatic SSL certificate** issuance via Let's Encrypt
- 🌐 **DNS-01 validation** via reg.ru API (wildcard domain support)
- 🔄 **Automatic renewal** with configurable threshold
- 📦 **Nginx Proxy Manager integration** - automatic upload and update
- 🧪 **Test certificates** - bypass Let's Encrypt rate limits (5 per week)
- ⚙️ **Full automation** via systemd/cron
- 🔀 **Repository sync** - automatic Gitea → GitHub synchronization

### 🚀 Quick Start

```bash
# Install via Makefile
sudo make install

# Configure
sudo nano /etc/letsencrypt/regru_config.json

# Create test certificate (no limits)
sudo make test-cert

# Get production certificate
sudo make obtain
```

### 📋 Requirements

- **OS**: Linux (Ubuntu/Debian/CentOS)
- **Python**: 3.6+
- **Dependencies**: certbot, requests, cryptography
- **API**: reg.ru (DNS management access)
- **Optional**: Nginx Proxy Manager

### 🎯 Use Cases

- ✅ SSL certificate automation for web servers
- ✅ Centralized management via Nginx Proxy Manager
- ✅ Development and testing with self-signed certificates
- ✅ CI/CD integration
- ✅ Multi-domain configurations with wildcards

### 📚 Documentation

- [README.md](README.md) - Complete guide (1400+ lines)
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing guide
- [GITEA_SYNC.md](GITEA_SYNC.md) - Gitea → GitHub sync
- [CHEATSHEET.md](CHEATSHEET.md) - Quick reference

---

## 👤 Автор / Author

**Фофанов Дмитрий** @ 2025

## 📄 Лицензия / License

Open Source - Free to use

## 🤝 Вклад / Contributing

Pull requests приветствуются / Pull requests are welcome!

## 🔗 Ссылки / Links

- **Документация reg.ru API**: https://www.reg.ru/support/api
- **Let's Encrypt**: https://letsencrypt.org/
- **Nginx Proxy Manager**: https://nginxproxymanager.com/
