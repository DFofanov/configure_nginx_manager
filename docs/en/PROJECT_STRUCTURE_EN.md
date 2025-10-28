# 📁 configure_nginx_manager Project Structure

## Main Scripts

### Python (Recommended)
- **letsencrypt_regru_api.py** (1,411 lines)
  - Full-featured Python script
  - Direct reg.ru API integration
  - Nginx Proxy Manager integration
  - Automatic certificate check and renewal
  - Test self-signed certificate generation
  - Wildcard domain support

### Bash
- **letsencrypt_regru_dns.sh**
  - Bash script with certbot-dns-regru plugin
  - Easy to use
  - Minimal dependencies

### PowerShell
- **letsencrypt_regru.ps1**
  - Windows version
  - Similar to Bash script

### Testing
- **test_certificate.sh**
  - Quick test certificate creation via OpenSSL
  - Standalone operation without Python
  - Wildcard domain support

## Automation

### Makefile
- **Makefile** (415 lines)
  - `make install` - Complete installation and setup
  - `make uninstall` - Clean removal
  - `make status` - Check status
  - `make test-cert` - Create test certificate
  - `make obtain` - Get Let's Encrypt certificate
  - `make renew` - Renew certificate
  - `make logs` - View logs
  - `make check-config` - Validate configuration

## Configuration

### config.json.example
Example configuration with all parameters:
- reg.ru API credentials
- Domain and email settings
- Renewal parameters (renewal_days)
- Nginx Proxy Manager settings
- Directory and log paths

## Documentation

### README.md (1,420+ lines)
Main documentation:
- Introduction and features
- Quick start
- Makefile installation
- Test certificate creation
- Requirements and dependencies
- Configuration and usage
- NPM integration
- Automatic check and renewal
- Automation via cron/systemd
- Troubleshooting

### README_EN.md (English version)
Complete English translation of main guide

### TESTING_GUIDE.md (370+ lines)
Testing guide:
- Why test certificates are needed
- Bypass Let's Encrypt limits (5 per week)
- Quick start with test certificates
- Method comparison
- Development usage
- Test automation
- Transition from test to production
- FAQ
- CI/CD and Docker examples

### TESTING_GUIDE_EN.md (English version)
Complete English translation of testing guide

### GITEA_SYNC.md
Gitea → GitHub synchronization:
- 4 sync methods (Git Hooks, GitHub Actions, Gitea Mirror, Double Remote)
- Step-by-step installation
- SSH and token setup
- Webhook integration
- Troubleshooting
- Method comparison

### GITEA_SYNC_EN.md (English version)
Complete English translation of sync guide

### CHEATSHEET.md
Quick reference:
- Main commands
- Development workflow
- Use case scenarios
- Common errors and solutions
- Checking and debugging

### CHEATSHEET_EN.md (English version)
Complete English translation of cheatsheet

### PROJECT_STRUCTURE.md (this file)
- All project files description
- Component overview

### PROJECT_STRUCTURE_EN.md (English version)
Complete English translation of structure

### DESCRIPTION.md
Project description:
- Russian description
- English description
- Quick start
- Features overview

### CHANGELOG.md
Change history:
- Versions and updates
- New features
- Bug fixes
- Roadmap

### CHANGELOG_EN.md (English version)
Complete English translation of changelog

## Git Integration

### .github/workflows/sync-from-gitea.yml
GitHub Actions for synchronization:
- Automatic check every hour
- Webhook trigger from Gitea
- Manual run
- Merge changes from Gitea
- Push to GitHub

### gitea-hooks/
Git hooks for Gitea server:

**post-receive**
- Automatic push to GitHub after commit
- Instant sync (< 1 second)
- Operation logging
- Tag synchronization
- SSH and HTTPS support

**README.md**
- Hook installation instructions
- Authentication setup
- Troubleshooting

**README_EN.md** (English version)
Complete English translation

## Additional Files

### Markdown Documents
- **Add Let's Encrypt Certificate для провайдера reg.ru.md**
  - Initial instructions (Russian)
  
- **Создание и продление SSL сертификата.md**
  - Additional process information (Russian)

## Features

### ✅ Core Features
- [x] Let's Encrypt certificates via reg.ru DNS API
- [x] Wildcard certificates (*.domain.com)
- [x] Automatic certificate renewal
- [x] DNS-01 validation
- [x] Nginx Proxy Manager integration
- [x] Automatic upload/update to NPM

### ✅ Advanced Features
- [x] Automatic expiration check
- [x] Configurable renewal threshold (renewal_days)
- [x] Systemd service + timer
- [x] Cron automation
- [x] Detailed logging
- [x] Configuration validation

### 🆕 Testing
- [x] Self-signed test certificate generation
- [x] Bypass Let's Encrypt limits (5/week)
- [x] Instant creation without DNS
- [x] Test certificate NPM integration
- [x] Full structure compatibility with Let's Encrypt

### 🔄 Repository Sync
- [x] Automatic Gitea → GitHub sync
- [x] Git Hooks (instant sync)
- [x] GitHub Actions (hourly check)
- [x] Webhook integration
- [x] SSH and HTTPS authentication

## Installation

### Quick Install
```bash
sudo make install
sudo nano /etc/letsencrypt/regru_config.json
sudo make test-cert  # For testing
sudo make obtain     # For production
```

### Post-Install Structure
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

## Usage

### Testing (no limits)
```bash
sudo make test-cert              # Create test certificate
sudo make status                 # Check status
```

### Production
```bash
sudo make obtain                 # Get Let's Encrypt certificate
sudo make renew                  # Renew certificate
sudo make run                    # Automatic mode
```

### Monitoring
```bash
sudo make logs                   # View logs
sudo make status                 # Service status
sudo make check-config           # Check configuration
```

## Technologies

- **Python 3.6+** - Main language
- **Certbot** - Let's Encrypt client
- **requests** - HTTP API requests
- **cryptography** - Test certificate generation
- **systemd** - Launch automation
- **cron** - Alternative automation
- **Make** - Installation management
- **OpenSSL** - Alternative certificate generation

## License

Open Source - Free to use

## Author

Фофанов Дмитрий @ 2025

## Support

See documentation:
- [README.md](README.md) / [README_EN.md](README_EN.md) - Main guide
- [TESTING_GUIDE.md](TESTING_GUIDE.md) / [TESTING_GUIDE_EN.md](TESTING_GUIDE_EN.md) - Testing guide
- [GITEA_SYNC.md](GITEA_SYNC.md) / [GITEA_SYNC_EN.md](GITEA_SYNC_EN.md) - Repository sync

---

**Version**: 2.1  
**Date**: October 27, 2025  
**Status**: ✅ Production Ready
