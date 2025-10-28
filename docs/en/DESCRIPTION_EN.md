# 🔒 SSL Certificate Manager for Let's Encrypt + reg.ru

**Automated Let's Encrypt SSL certificate management with DNS validation via reg.ru API and Nginx Proxy Manager integration**

## 📖 Description

Comprehensive solution for automating the creation, renewal, and management of Let's Encrypt SSL certificates for domains registered with reg.ru. Supports DNS-01 validation, wildcard certificates, automatic upload to Nginx Proxy Manager, and test certificate generation for development.

### ✨ Key Features

- 🔐 **Automatic SSL certificate issuance** via Let's Encrypt
- 🌐 **DNS-01 validation** via reg.ru API (wildcard domain support)
- 🔄 **Automatic renewal** with configurable threshold
- 📦 **Nginx Proxy Manager integration** - automatic upload and update
- 🧪 **Test certificates** - bypass Let's Encrypt rate limits (5 per week)
- ⚙️ **Full automation** via systemd/cron
- 🔀 **Repository synchronization** - automatic Gitea → GitHub sync

### 🚀 Quick Start

```bash
# Install via Makefile
sudo make install

# Configure
sudo nano /etc/letsencrypt/regru_config.json

# Create test certificate (no rate limits)
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

#### English Documentation
- [BUILD_GUIDE_EN.md](../en/BUILD_GUIDE_EN.md) - Complete build guide
- [QUICKSTART_BUILD_EN.md](../en/QUICKSTART_BUILD_EN.md) - Quick build start
- [RELEASE_GUIDE_EN.md](../en/RELEASE_GUIDE_EN.md) - Release creation guide
- [MAKEFILE_COMMANDS_EN.md](../en/MAKEFILE_COMMANDS_EN.md) - Makefile commands reference
- [TESTING_GUIDE_EN.md](../en/TESTING_GUIDE_EN.md) - Testing guide
- [CHEATSHEET_EN.md](../en/CHEATSHEET_EN.md) - Quick reference
- [GITEA_SYNC_EN.md](../en/GITEA_SYNC_EN.md) - Gitea → GitHub sync
- [PROJECT_STRUCTURE_EN.md](../en/PROJECT_STRUCTURE_EN.md) - Project structure

#### Russian Documentation / Русская документация
- [BUILD_GUIDE.md](../ru/BUILD_GUIDE.md) - Полное руководство по сборке
- [QUICKSTART_BUILD.md](../ru/QUICKSTART_BUILD.md) - Быстрый старт сборки
- [RELEASE_GUIDE.md](../ru/RELEASE_GUIDE.md) - Руководство по созданию релизов
- [MAKEFILE_COMMANDS.md](../ru/MAKEFILE_COMMANDS.md) - Справочник команд Makefile
- [TESTING_GUIDE.md](../ru/TESTING_GUIDE.md) - Руководство по тестированию
- [CHEATSHEET.md](../ru/CHEATSHEET.md) - Быстрая шпаргалка
- [GITEA_SYNC.md](../ru/GITEA_SYNC.md) - Синхронизация Gitea → GitHub
- [PROJECT_STRUCTURE.md](../ru/PROJECT_STRUCTURE.md) - Структура проекта

---

## 🔨 Building Executables

The project supports building standalone executables for Linux and Windows:

```bash
# Build for current OS
make build

# Build for all platforms
make build-all

# Create full release
make release
```

**Result:**
- Linux: `letsencrypt-regru` (~45-55 MB)
- Windows: `letsencrypt-regru.exe` (~40-50 MB)

See [BUILD_GUIDE_EN.md](../en/BUILD_GUIDE_EN.md) for details.

---

## 🎯 Automated Releases

### GitHub Actions

Create a tag to trigger automatic build and release:

```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

### Gitea Actions

Same workflow available for self-hosted Gitea:

```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

See [RELEASE_GUIDE_EN.md](../en/RELEASE_GUIDE_EN.md) for details.

---

## 👤 Author

**Dmitry Fofanov** @ 2025

## 📄 License

Open Source - Free to use

## 🤝 Contributing

Pull requests are welcome!

## 🔗 Links

- **reg.ru API Documentation**: https://www.reg.ru/support/api
- **Let's Encrypt**: https://letsencrypt.org/
- **Nginx Proxy Manager**: https://nginxproxymanager.com/
- **PyInstaller**: https://pyinstaller.org/

---

**Last Updated:** October 28, 2025
