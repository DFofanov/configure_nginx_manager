# SSL Certificate Automation Scripts

**Author:** Фофанов Дмитрий

## 📖 Overview

This project contains scripts for automating the creation and renewal of Let's Encrypt SSL certificates using DNS-01 Challenge via the reg.ru API.

## 🎯 Quick Start

### Linux (Bash)

```bash
# 1. Install dependencies
sudo apt-get install certbot jq

# 2. Configure credentials
nano ~/.regru_credentials
# Add:
# export REGRU_USERNAME="your_login"
# export REGRU_PASSWORD="your_password"

# 3. Set permissions
chmod 600 ~/.regru_credentials

# 4. Run the script
./letsencrypt_regru.sh \
  -d "*.dfv24.com" \
  -e "dfofanov@dfv24.com"
```

### Linux (Python)

```bash
# 1. Install dependencies
pip install requests dnspython certbot

# 2. Configure
cp config.example.yml config.yml
nano config.yml

# 3. Run
python letsencrypt_regru.py

# 4. Setup auto-renewal (cron)
crontab -e
# Add:
# 0 3 * * 1 /usr/bin/python3 /path/to/letsencrypt_regru.py
```

### Windows (PowerShell)

```powershell
# 1. Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Configure credentials
$env:REGRU_USERNAME = "your_login"
$env:REGRU_PASSWORD = "your_password"

# 3. Run
.\letsencrypt_regru.ps1 `
  -Domain "*.dfv24.com" `
  -Email "dfofanov@dfv24.com"

# 4. Setup auto-renewal (Task Scheduler)
# Import-Module .\ScheduledTask.psm1
# Create-CertRenewalTask
```

## ⚙️ Configuration

### Bash Script (`letsencrypt_regru.sh`)

```bash
#!/bin/bash

# Required parameters
DOMAIN="*.dfv24.com"           # Your domain
EMAIL="dfofanov@dfv24.com"     # Contact email
REGRU_USERNAME="your_login"    # reg.ru login
REGRU_PASSWORD="your_password" # reg.ru password

# Optional parameters
DNS_PROPAGATION_WAIT=60        # Wait time for DNS propagation (seconds)
LOG_FILE="/var/log/letsencrypt_regru.log"
WEBSERVER="nginx"              # nginx or apache2
```

### Python Script (`letsencrypt_regru.py`)

Create `config.yml`:

```yaml
# reg.ru credentials
regru:
  username: "your_login"
  password: "your_password"

# Certificate settings
certificate:
  domain: "*.dfv24.com"
  email: "dfofanov@dfv24.com"
  dns_propagation_wait: 60

# Logging
logging:
  file: "/var/log/letsencrypt_regru.log"
  level: "INFO"

# Web server
webserver:
  type: "nginx"  # nginx, apache2, or null
  reload_command: "systemctl reload nginx"
```

### PowerShell Script (`letsencrypt_regru.ps1`)

```powershell
# Configuration
$Config = @{
    Domain = "*.dfv24.com"
    Email = "dfofanov@dfv24.com"
    RegRuUsername = $env:REGRU_USERNAME
    RegRuPassword = $env:REGRU_PASSWORD
    DnsPropagationWait = 60
    LogFile = ".\letsencrypt_regru.log"
}
```

## 📋 Requirements

### Bash Script
- **certbot** - Let's Encrypt client
- **jq** - JSON processor
- **curl** - HTTP requests
- **dig** (optional) - DNS queries

### Python Script
- **Python 3.6+**
- **requests** - HTTP library
- **dnspython** - DNS operations
- **certbot** - Let's Encrypt client
- **PyYAML** - YAML configuration

### PowerShell Script
- **PowerShell 5.1+** or **PowerShell Core 7+**
- **certbot** (via Chocolatey or manual installation)

## 🔄 Automatic Renewal

### Linux (cron)

```bash
# Edit crontab
crontab -e

# Add (runs every Monday at 3 AM):
0 3 * * 1 /path/to/letsencrypt_regru.sh >> /var/log/cert_renewal.log 2>&1

# Or for Python:
0 3 * * 1 /usr/bin/python3 /path/to/letsencrypt_regru.py
```

### Windows (Task Scheduler)

```powershell
# Create scheduled task
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-File C:\path\to\letsencrypt_regru.ps1"

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 3am

Register-ScheduledTask -TaskName "SSL Certificate Renewal" `
  -Action $Action -Trigger $Trigger -RunLevel Highest
```

## ✨ Features

✅ Automatic DNS validation via reg.ru API  
✅ Certificate expiration check  
✅ Automatic renewal before expiration  
✅ Web server reload after renewal  
✅ Detailed logging of all operations  

## 🔧 Using with Nginx Proxy Manager

After obtaining the certificate:

1. Log in to NPM: http://192.168.10.14:81/
2. SSL Certificates → Add SSL Certificate → Custom
3. Paste the content:
   - Certificate Key: `/etc/letsencrypt/live/domain.com/privkey.pem`
   - Certificate: `/etc/letsencrypt/live/domain.com/fullchain.pem`

## 📝 Logs

- Bash: `/var/log/letsencrypt_regru.log`
- Python: `/var/log/letsencrypt_regru.log`
- PowerShell: `.\letsencrypt_regru.log`
- Certbot: `/var/log/letsencrypt/letsencrypt.log`

## 🆘 Troubleshooting

### API Authentication Error
- Check your reg.ru credentials
- Ensure the domain is under your control

### DNS Record Not Propagating
- Increase `dns_propagation_wait` to 120 seconds
- Check DNS: `nslookup -type=TXT _acme-challenge.domain.com`

### Certbot Not Found
```bash
# Ubuntu/Debian
sudo apt-get install certbot

# Or via snap
sudo snap install --classic certbot
```

## 📚 Documentation

Detailed documentation in [USAGE.md](USAGE.md)

## 🔐 Security

- Keep credentials secure
- Use `chmod 600` for configuration files
- Regularly update passwords

## ⚠️ Important

- Let's Encrypt certificates are valid for 90 days
- Automatic renewal setup is recommended
- Wildcard certificates require DNS validation

## 📞 Support

- [reg.ru API Documentation](https://www.reg.ru/support/api)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)

## 📄 License

Scripts are provided "as is" for free use.

---

**Happy Automation! 🔒**
