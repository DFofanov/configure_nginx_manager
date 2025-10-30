# ⚡ SSL Certificate Cheatsheet

## 🚀 Quick Start

### Installation in 3 Commands
```bash
sudo make install
sudo nano /etc/letsencrypt/regru_config.json  # Fill in data
sudo make test-cert                            # Test
```

---

## 🧪 Testing (NO Let's Encrypt Limits)

```bash
# Create test certificate (unlimited)
sudo make test-cert

# Check status
sudo make status

# View logs
sudo make logs
```

**When to use:**
- ⚠️ Let's Encrypt: max 5 certificates/week
- ✅ Test: UNLIMITED
- ⚡ Creation: 1-2 seconds vs 2-5 minutes

---

## 🔒 Production (Let's Encrypt)

```bash
# Get real certificate
sudo make obtain

# Automatic mode (check + renewal)
sudo make run

# Force renewal
sudo make renew
```

---

## 📋 Main Commands

### letsencrypt-regru Commands

| Command | Description | Limits | Use Case |
|---------|-------------|--------|----------|
| `--check` | Check certificate expiration | - | Monitoring |
| `--obtain` | Obtain new certificate | ⚠️ 5/week | Initial creation |
| `--renew` | Renew existing certificate | ⚠️ 5/week | Renewal |
| `--auto` | Auto-check and renewal | ⚠️ 5/week | Cron/systemd |
| `--test-cert` | Test certificate | ✅ None | Development |
| `--test-api` | Check API reg.ru access | - | Diagnostics |
| `--test-dns` | Test DNS record creation | - | Pre-SSL check |
| `--help` | Show help | - | Help |
| `-v` | Verbose output | - | Debugging |

### Makefile Commands

| Command | Description | Equivalent |
|---------|-------------|------------|
| `make test-cert` | Test certificate | `letsencrypt-regru --test-cert` |
| `make obtain` | New Let's Encrypt | `letsencrypt-regru --obtain` |
| `make renew` | Renew existing | `letsencrypt-regru --renew` |
| `make run` | Auto mode | `letsencrypt-regru --auto` |
| `make status` | System status | - |
| `make logs` | Show logs | `journalctl -u letsencrypt-regru` |
| `make check-config` | Check configuration | - |

### letsencrypt_regru.sh Commands

| Command | Description |
|---------|-------------|
| `sudo bash letsencrypt_regru.sh install` | Install application |
| `sudo bash letsencrypt_regru.sh update` | Update application |
| `sudo bash letsencrypt_regru.sh uninstall` | Uninstall application |

---

## 📝 Configuration

### Minimal (testing)
```json
{
    "domain": "test.example.com",
    "wildcard": true,
    "cert_dir": "/etc/letsencrypt/live"
}
```

### Full (production + NPM)
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

### Development → Production

```bash
# 1. Development (test certificates)
sudo make test-cert              # Create test
# Test application...

# 2. Production (Let's Encrypt)
sudo rm -rf /etc/letsencrypt/live/example.com/  # Remove test
sudo make obtain                 # Create production
```

---

## 📁 Important Paths

```bash
# Configuration
/etc/letsencrypt/regru_config.json

# Certificates
/etc/letsencrypt/live/example.com/
├── privkey.pem      # Private key
├── cert.pem         # Certificate
├── fullchain.pem    # Full chain (for nginx)
└── chain.pem        # CA chain

# Scripts
/opt/letsencrypt-regru/letsencrypt_regru_api.py

# Logs
/var/log/letsencrypt_regru.log
```

---

## 🔍 Verification

```bash
# Check configuration
sudo make check-config

# Check certificate
openssl x509 -in /etc/letsencrypt/live/example.com/cert.pem -text -noout

# Check expiration date
openssl x509 -in /etc/letsencrypt/live/example.com/cert.pem -noout -dates

# Check systemd
sudo systemctl status letsencrypt-regru.timer
sudo systemctl list-timers letsencrypt-regru.timer

# Check cron
sudo crontab -l | grep letsencrypt
```

---

## 🐛 Debugging

```bash
# Detailed logs
sudo make logs

# Test run with details
sudo python3 /opt/letsencrypt-regru/letsencrypt_regru_api.py \
    -c /etc/letsencrypt/regru_config.json --check -v

# Certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Systemd logs
sudo journalctl -u letsencrypt-regru.service -f
```

---

## ⚠️ Common Errors

### Let's Encrypt: Rate limit exceeded
```bash
# SOLUTION: Use test certificates
sudo make test-cert
```

### NPM: Certificate not found
```bash
# SOLUTION: Check NPM settings
sudo make check-config

# Check connection
curl -k https://npm.example.com
```

### Permission denied
```bash
# SOLUTION: Run with sudo
sudo make test-cert
```

---

## 🎯 Use Case Scenarios

### Local Development
```bash
sudo make test-cert
# Open https://localhost (ignore warning)
```

### CI/CD Testing
```bash
# In pipeline
sudo make test-cert
# Run tests...
sudo make status
```

### Staging Environment
```bash
sudo make test-cert  # Or
sudo make obtain     # If domain available
```

### Production Environment
```bash
sudo make install
sudo make obtain
# Automatic renewal via cron/systemd
```

---

## 📚 Documentation

- **README.md** - Complete guide (1420+ lines)
- **TESTING_GUIDE.md** - Testing guide (370+ lines)
- **PROJECT_STRUCTURE.md** - Project structure
- **CHEATSHEET.md** - This cheatsheet

---

## 🆘 Quick Help

```bash
# Show all commands
make help

# Check installation
sudo make status

# Complete reinstall
sudo make uninstall
sudo make install
```

---

## 💡 Tips

1. **Always start with test certificates** - avoid limits
2. **Check configuration** - `make check-config`
3. **Monitor logs** - `make logs`
4. **Automate** - systemd/cron already configured
5. **Keep backups** of configuration

---

**Version**: 2.1  
**Updated**: 27.10.2025
