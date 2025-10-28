# 📋 Changelog

## [2.1.0] - 2025-10-27

### 🆕 Added

#### Test SSL Certificate Generation
- ✨ **New `TestCertificateGenerator` class** - self-signed certificate generation
- ✨ **`--test-cert` command** in Python script for test certificate creation
- ✨ **`test_certificate.sh` script** - standalone creation via OpenSSL
- ✨ **`make test-cert` command** in Makefile for quick testing

#### Documentation
- 📘 **TESTING_GUIDE.md** (370+ lines) - complete testing guide
  - Bypass Let's Encrypt limits (5 certificates per week)
  - Certificate creation method comparison
  - CI/CD and Docker examples
  - Transition from test to production
  - FAQ and solutions
  
- 📘 **TESTING_GUIDE_EN.md** - English version of testing guide

- 📘 **PROJECT_STRUCTURE.md** - project structure
  - All files description
  - Features list
  - Technologies
  
- 📘 **PROJECT_STRUCTURE_EN.md** - English version

- 📘 **CHEATSHEET.md** - quick reference
  - Main commands
  - Use case scenarios
  - Common errors and solutions
  - Development workflow

- 📘 **CHEATSHEET_EN.md** - English version

- 📘 **DESCRIPTION.md** - project description in Russian and English

- 📘 **CHANGELOG_EN.md** - English changelog

- 📘 **GITEA_SYNC.md** - Gitea → GitHub synchronization
  - 4 sync methods
  - Step-by-step setup
  - Troubleshooting
  
- 📘 **GITEA_SYNC_EN.md** - English version

- 📘 **README_EN.md** - Complete English main guide

#### Functionality
- ✨ Support for **unlimited** test certificates
- ✨ **Instant creation** (1-2 seconds) without DNS validation
- ✨ **Automatic upload** of test certificates to NPM
- ✨ **Full compatibility** of structure with Let's Encrypt
- ✨ **Wildcard support** for test certificates

#### Repository Synchronization
- ✨ **Automatic Gitea → GitHub sync** via Git Hooks
- ✨ **GitHub Actions workflow** for hourly sync check
- ✨ **Webhook integration** between Gitea and GitHub
- ✨ **Multiple sync methods** (Hooks, Actions, Mirror, Double Remote)

### 🔧 Improved

#### Python Script
- Added `cryptography` library import with installation check
- New command-line parameters:
  - `--test-cert` - create test certificate
  - `--auto` - explicit automatic mode
- Improved test certificate handling in NPM
- Detailed logging of generation process

#### Makefile
- Added `make test-cert` command with beautiful output
- Information messages about test certificate benefits
- Security warnings

#### README.md
- "Test Self-Signed Certificate Creation" section
- Updated table of contents with test certificates link
- Test certificate usage examples
- NPM integration for test certificates
- Links to additional documentation
- Gitea → GitHub sync section

### 🎯 Benefits

#### For Developers
- ✅ **No limits** - unlimited certificates
- ✅ **Fast** - creation in 1-2 seconds
- ✅ **Offline** - works without internet
- ✅ **Identical structure** - same files as Let's Encrypt

#### For Testing
- ✅ **CI/CD friendly** - quick creation in pipeline
- ✅ **Docker ready** - easily embeds in containers
- ✅ **Staging environments** - perfect for test servers
- ✅ **Local development** - HTTPS on localhost

#### For DevOps
- ✅ **Repository sync** - automatic Gitea → GitHub
- ✅ **Multiple methods** - choose what fits
- ✅ **Instant sync** - Git Hooks < 1 second
- ✅ **Reliable backup** - GitHub Actions hourly check

### 📊 Statistics

- **Lines of code**: 1,411 (Python script)
- **Makefile lines**: 415
- **Documentation lines**: 3,500+
- **Makefile commands**: 13
- **Operating modes**: 4 (obtain, renew, auto, test-cert)
- **Sync methods**: 4 (Hooks, Actions, Mirror, Remote)
- **Languages**: 2 (Russian, English)

---

## [2.0.0] - 2025-10-27

### 🆕 Added
- ✨ Nginx Proxy Manager (NPM) integration
- ✨ `NginxProxyManagerAPI` class for certificate management via API
- ✨ Automatic certificate upload to NPM
- ✨ Automatic certificate update in NPM
- ✨ Automatic expiration check
- ✨ Configurable renewal threshold (`renewal_days`)
- ✨ Makefile for installation/removal automation
- ✨ Systemd service + timer
- ✨ Cron automation

### 🔧 Improved
- Documentation consolidation into single README.md
- Detailed logging with operation statuses
- Configuration validation
- Improved error handling

### 📘 Documentation
- Complete NPM integration guide
- Quick start in 3 commands
- Automation examples

---

## [1.0.0] - 2025-10-26

### 🆕 First Release
- Python script for Let's Encrypt via reg.ru API
- Bash script with certbot-dns-regru
- PowerShell version for Windows
- DNS-01 validation
- Wildcard certificates
- Basic documentation

---

## Roadmap

### [2.2.0] - Planned
- [ ] Web interface for management
- [ ] Multiple domain support
- [ ] Notifications (email, telegram)
- [ ] Grafana dashboard for monitoring
- [ ] Certificate backups

### [3.0.0] - Future
- [ ] Other DNS provider support
- [ ] Cloudflare API
- [ ] Route53 (AWS)
- [ ] Google Cloud DNS

---

## Change Types
- `🆕 Added` - new functionality
- `🔧 Improved` - improvements to existing functionality
- `🐛 Fixed` - bug fixes
- `🗑️ Removed` - removed functionality
- `🔒 Security` - security changes
- `📘 Documentation` - documentation changes

---

**Versioning**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality with backward compatibility
- **PATCH**: Bug fixes
