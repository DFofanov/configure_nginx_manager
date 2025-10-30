# Installation Guide for letsencrypt_regru.sh

**Author:** Dmitry Fofanov  
**Date:** October 28, 2025

## Description

`letsencrypt_regru.sh` is an automated installer for Let's Encrypt Manager with reg.ru and Nginx Proxy Manager integration.

The script automates:
- Installation of all system dependencies
- Python virtual environment creation
- Python library installation (requests, cryptography, certbot)
- Interactive configuration setup
- Creating and configuring systemd services
- Automatic certificate renewal setup

## Requirements

- Linux (Debian/Ubuntu, CentOS/RHEL/Fedora)
- Root access (sudo)
- Minimum 512MB RAM
- Minimum 1GB free disk space
- Internet connection

## Quick Installation

**Method 1: Automatic Installation (Recommended)**

The fastest way - run installation directly from GitHub:

```bash
sudo bash -c "$(curl -fsSL https://github.com/DFofanov/configure_nginx_manager/raw/refs/heads/master/letsencrypt_regru.sh)"
```

This command will:
- Automatically download the installation script
- Run it with root privileges
- Guide you through interactive setup

**Method 2: Clone Repository**

If you want to review the code before installation:

```bash
# 1. Download repository
git clone https://github.com/DFofanov/configure_nginx_manager.git
cd configure_nginx_manager

# 2. Make executable
chmod +x letsencrypt_regru.sh

# 3. Run installation
sudo ./letsencrypt_regru.sh
```

## Interactive Setup

During installation, the script will ask for:

1. **Domain** - your main domain (e.g., `example.com`)
2. **Email** - for Let's Encrypt notifications
3. **reg.ru credentials:**
   - Username
   - Password
4. **Wildcard certificate** - create `*.example.com` (recommended: Yes)
5. **NPM integration** (optional):
   - NPM address (e.g., `http://10.10.10.14:81`)
   - NPM login email
   - NPM password

## Structure After Installation

```
/opt/letsencrypt-regru/           # Application
├── letsencrypt_regru_api.py      # Main script
├── venv/                         # Python virtual environment
└── docs/                         # Documentation

/etc/letsencrypt-regru/           # Configuration
└── config.json                   # Settings (credentials, domain, NPM)

/var/log/letsencrypt-regru/       # Logs
└── letsencrypt_regru.log

/etc/letsencrypt/live/            # Let's Encrypt certificates
└── example.com/
    ├── privkey.pem
    ├── cert.pem
    ├── chain.pem
    └── fullchain.pem

/etc/systemd/system/              # Systemd services
├── letsencrypt-regru.service     # Renewal service
└── letsencrypt-regru.timer       # Timer (every 12 hours)

/usr/local/bin/
└── letsencrypt-regru             # Global command
```

## Using letsencrypt-regru Command

After installation, a convenient global command with multiple functions is available:

### 🔧 Main Commands

```bash
# Check current certificate expiration
letsencrypt-regru --check

# Obtain new Let's Encrypt certificate
letsencrypt-regru --obtain

# Renew existing certificate
letsencrypt-regru --renew

# Automatically check and renew if needed
letsencrypt-regru --auto

# Create test self-signed certificate
letsencrypt-regru --test-cert
```

### 🧪 Diagnostic and Testing Commands

```bash
# Check API access to reg.ru
# - Shows current IP address
# - Tests API connection
# - Displays account balance
letsencrypt-regru --test-api

# Test DNS TXT record creation
# - Full SSL certification process simulation
# - Creates temporary _acme-challenge TXT record
# - Waits for DNS propagation (60 seconds)
# - Verifies via public DNS servers
# - Automatically removes test record
letsencrypt-regru --test-dns

# Show help for all commands
letsencrypt-regru --help

# Enable verbose output
letsencrypt-regru --obtain -v
letsencrypt-regru --check -v
```

### ⚙️ Service Commands (internal use)

```bash
# Certbot authentication hook (used by certbot automatically)
letsencrypt-regru --auth-hook

# Certbot cleanup hook (used by certbot automatically)
letsencrypt-regru --cleanup-hook
```

### 📋 Command Reference

| Command | Description | Use Case |
|---------|-------------|----------|
| `--check` | Check certificate expiration | Regular monitoring |
| `--obtain` | Obtain new certificate from Let's Encrypt | Initial creation |
| `--renew` | Renew existing certificate | Renewal |
| `--auto` | Automatic check and renewal | For cron/systemd |
| `--test-cert` | Create test self-signed certificate | Development/testing |
| `--test-api` | Check API access to reg.ru | Connection diagnostics |
| `--test-dns` | Test DNS record creation | Pre-SSL verification |
| `--auth-hook` | Certbot hook (DNS creation) | Internal |
| `--cleanup-hook` | Certbot hook (DNS deletion) | Internal |
| `--help` | Show help | Help |
| `-v` | Verbose output | Debugging |

## Automatic Renewal

The installer configures a systemd timer for automatic checks:

```bash
# Check timer status
systemctl status letsencrypt-regru.timer

# When is next run
systemctl list-timers letsencrypt-regru.timer

# View run history
journalctl -u letsencrypt-regru

# Follow logs in real-time
journalctl -u letsencrypt-regru -f
```

### Timer Settings

Default settings:
- First run: 15 minutes after system boot
- Frequency: every 12 hours
- Random delay: up to 1 hour (to avoid creating load)

Can be modified in `/etc/systemd/system/letsencrypt-regru.timer`.

## Editing Configuration

```bash
# Open configuration in editor
sudo nano /etc/letsencrypt-regru/config.json

# After changes, restart timer
sudo systemctl restart letsencrypt-regru.timer
```

### Example config.json

```json
{
    "regru_username": "your_username",
    "regru_password": "your_password",
    "domain": "example.com",
    "wildcard": true,
    "email": "admin@example.com",
    "cert_dir": "/etc/letsencrypt/live",
    "log_file": "/var/log/letsencrypt-regru/letsencrypt_regru.log",
    "dns_propagation_wait": 60,
    "dns_check_attempts": 10,
    "dns_check_interval": 10,
    "renewal_days": 30,
    "npm_enabled": true,
    "npm_host": "http://10.10.10.14:81",
    "npm_email": "admin@npm.local",
    "npm_password": "secure_password"
}
```

## Updating Application

```bash
# Download latest version
cd configure_nginx_manager
git pull

# Run update
sudo ./letsencrypt_regru.sh update
```

Update will:
- Stop timer
- Update script
- Update Python dependencies
- Restart timer

## Uninstallation

```bash
# Complete application removal
sudo ./letsencrypt_regru.sh uninstall
```

Script will remove:
- Application from `/opt/letsencrypt-regru/`
- Systemd services
- Global command

Certificates in `/etc/letsencrypt/live/` are preserved!

Optionally you can remove:
- Configuration `/etc/letsencrypt-regru/`
- Logs `/var/log/letsencrypt-regru/`

## Viewing Logs

```bash
# Systemd logs (recommended)
journalctl -u letsencrypt-regru -f

# Log file
tail -f /var/log/letsencrypt-regru/letsencrypt_regru.log

# Last 100 lines
tail -n 100 /var/log/letsencrypt-regru/letsencrypt_regru.log
```

## Troubleshooting

### Installation Check

```bash
# Check command availability
which letsencrypt-regru

# Check Python environment
ls -la /opt/letsencrypt-regru/venv/

# Check systemd services
systemctl list-unit-files | grep letsencrypt-regru
```

### Installation Errors

**Error: "Permission denied"**
```bash
# Run with sudo
sudo ./letsencrypt_regru.sh
```

**Error: "Package not found"**
```bash
# Update package lists
sudo apt-get update  # Debian/Ubuntu
sudo yum update      # CentOS/RHEL
```

**Error: "Python module not found"**
```bash
# Reinstall virtual environment
sudo rm -rf /opt/letsencrypt-regru/venv
sudo ./letsencrypt_regru.sh
```

### Certificate Issues

**Certificate not created**
```bash
# Check logs
tail -n 50 /var/log/letsencrypt-regru/letsencrypt_regru.log

# Check configuration
cat /etc/letsencrypt-regru/config.json

# Try manually
letsencrypt-regru --obtain -v
```

**DNS not updating**
```bash
# Increase wait time in config.json
"dns_propagation_wait": 120,
"dns_check_attempts": 20
```

### NPM Issues

**Not uploading to NPM**
```bash
# Check NPM availability
curl http://192.168.10.14:81

# Check credentials in config.json
# Try manually
letsencrypt-regru --test-cert -v
```

## Supported OS

✅ Debian 10, 11, 12  
✅ Ubuntu 20.04, 22.04, 24.04  
✅ CentOS 7, 8  
✅ RHEL 7, 8, 9  
✅ Fedora 35+  

## Additional Features

### Test Certificate

For testing without Let's Encrypt rate limits:

```bash
letsencrypt-regru --test-cert
```

Creates self-signed certificate valid for 90 days.

### Manual Renewal Run

```bash
# Start service manually
sudo systemctl start letsencrypt-regru.service

# Check status
systemctl status letsencrypt-regru.service
```

### Change Check Frequency

Edit `/etc/systemd/system/letsencrypt-regru.timer`:

```ini
[Timer]
# Every 6 hours instead of 12
OnUnitActiveSec=6h
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart letsencrypt-regru.timer
```

## Security

- Configuration with passwords has `600` permissions (root only)
- Certificate private keys have `600` permissions
- All operations run as root
- Logs accessible only to root

## Support

- GitHub Issues: https://github.com/DFofanov/configure_nginx_manager/issues
- Documentation: `/opt/letsencrypt-regru/docs/`
- Email: admin@dfv24.com

---

**Developed by:** Dmitry Fofanov  
**Date:** October 28, 2025  
**Version:** 2.0
