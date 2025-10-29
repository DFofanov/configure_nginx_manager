# 🔧 reg.ru API Troubleshooting Guide

## ❌ Issue: "Access to API from this IP denied"

This error occurs when reg.ru API is blocked for your IP address due to security settings.

### 🔍 Diagnostics

First, determine your current IP address:

```bash
# Method 1: Using script's built-in function
sudo letsencrypt-regru --test-api

# Method 2: Using curl
curl -s https://ipinfo.io/ip

# Method 3: Using website
# Open https://whatismyipaddress.com/
```

### ✅ Solution

#### Method 1: Add IP to whitelist (recommended)

1. **Login to reg.ru control panel**
   - Open https://www.reg.ru/
   - Login to your account

2. **Navigate to API settings**
   - Menu → "Settings" (Настройки)
   - Section "Security" (Безопасность)
   - Subsection "API"

3. **Configure IP access**
   - Find "IP Restrictions" section
   - Click "Add IP address"
   - Enter your current IP address
   - Save settings

4. **Test settings**
   ```bash
   sudo letsencrypt-regru --test-api
   ```

#### Method 2: Disable IP restrictions (less secure)

⚠️ **WARNING**: This reduces your account security!

1. In reg.ru API settings find "IP Restrictions"
2. Disable "Allow access only from specified IPs" option
3. Save settings

### 🔒 Security Recommendations

1. **Use static IP**
   - If you have dynamic IP, consider purchasing static IP
   - Or regularly update allowed IP list

2. **Limit API access**
   - Add only necessary IP addresses
   - Regularly review and clean up the list

3. **Use strong passwords**
   - Complex password for reg.ru account
   - Two-factor authentication if available

## ❌ Issue: "Invalid username or password"

### ✅ Solution

1. **Check credentials**
   ```bash
   sudo nano /etc/letsencrypt-regru/config.json
   ```
   
   Make sure you have correct:
   - `regru_username` - reg.ru login
   - `regru_password` - reg.ru password

2. **Check file permissions**
   ```bash
   sudo chmod 600 /etc/letsencrypt-regru/config.json
   sudo chown root:root /etc/letsencrypt-regru/config.json
   ```

3. **Test connection**
   ```bash
   sudo letsencrypt-regru --test-api
   ```

## ❌ Issue: Connection timeout

### ✅ Solution

1. **Check internet connection**
   ```bash
   ping -c 4 api.reg.ru
   curl -I https://api.reg.ru/api/regru2
   ```

2. **Check firewall**
   ```bash
   # Temporarily disable firewall for testing
   sudo ufw status
   sudo iptables -L
   ```

3. **Check proxy settings**
   - Ensure `HTTP_PROXY`, `HTTPS_PROXY` environment variables don't interfere

## 🧪 API Testing

Always test API before use:

```bash
# Full API test
sudo letsencrypt-regru --test-api

# Test with verbose output
sudo letsencrypt-regru --test-api -v

# Check configuration
sudo letsencrypt-regru --check
```

## 📞 Getting Help

### reg.ru Technical Support

- **Email**: support@reg.ru
- **Phone**: 8 (495) 580-11-11
- **Online chat**: on reg.ru website

### Documentation

- **reg.ru API**: https://www.reg.ru/support/api
- **Usage examples**: https://www.reg.ru/support/api/examples
- **API FAQ**: https://www.reg.ru/support/api/faq

### Diagnostic Logs

Always include logs when contacting support:

```bash
# Enable verbose logs
sudo letsencrypt-regru --test-api -v

# View recent logs
sudo tail -n 50 /var/log/letsencrypt-regru/letsencrypt_regru.log

# Certbot logs
sudo tail -n 50 /var/log/letsencrypt/letsencrypt.log
```

## 🔄 Alternative DNS Providers

If reg.ru API issues are critical, consider alternatives:

1. **Cloudflare** - excellent API, free DNS
2. **Route53** (AWS) - powerful but paid
3. **DigitalOcean DNS** - simple and reliable
4. **Google Cloud DNS** - GCP integration

These require script modification or other certbot plugins.

---

**Last Updated**: October 29, 2025  
**Document Version**: 1.0