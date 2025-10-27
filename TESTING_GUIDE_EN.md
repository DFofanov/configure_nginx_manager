# 🧪 SSL Certificate Testing Guide

## Why do you need test certificates?

Let's Encrypt has **strict limits**:
- ⚠️ Maximum **5 certificates per week** per domain
- ⚠️ Maximum **50 certificates per week** per account
- ⚠️ **1 week ban** if limits exceeded

**Solution**: Use self-signed test certificates for development!

---

## Quick Start

### Option 1: Via Makefile (Recommended)

```bash
# After script installation (make install)
sudo make test-cert
```

**Result**: Certificate created in `/etc/letsencrypt/live/your-domain/`

### Option 2: Via Python Script

```bash
sudo python3 letsencrypt_regru_api.py \
    --config /etc/letsencrypt/regru_config.json \
    --test-cert -v
```

### Option 3: Via Bash Script (Standalone)

```bash
# Simple domain
sudo ./test_certificate.sh example.com no

# With wildcard
sudo ./test_certificate.sh example.com yes
```

---

## Method Comparison

| Method | Speed | Requirements | NPM Integration | Limits |
|--------|-------|--------------|-----------------|--------|
| **Let's Encrypt** | 2-5 min | Internet, DNS | ✅ Yes | ⚠️ 5/week |
| **Test (Python)** | 1-2 sec | Python only | ✅ Yes | ✅ None |
| **Test (Bash)** | 1-2 sec | OpenSSL only | ❌ Manual | ✅ None |

---

## Detailed Instructions

### 1. Configuration Setup

```bash
# Create configuration
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

### 2. Create Test Certificate

```bash
sudo make test-cert
```

### 3. Verify Created Files

```bash
ls -la /etc/letsencrypt/live/test.example.com/
# Should contain:
# - privkey.pem     (private key)
# - cert.pem        (certificate)
# - fullchain.pem   (full chain)
# - chain.pem       (CA chain)
```

### 4. View Certificate Information

```bash
openssl x509 -in /etc/letsencrypt/live/test.example.com/cert.pem -text -noout
```

---

## Using in Nginx

### Direct Usage

```nginx
server {
    listen 443 ssl;
    server_name test.example.com;

    ssl_certificate /etc/letsencrypt/live/test.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/test.example.com/privkey.pem;

    # ... rest of configuration
}
```

### Via Nginx Proxy Manager

If `npm_enabled: true` in configuration, certificate will automatically upload to NPM.

**Check in NPM:**
1. Open NPM web interface
2. Go to **SSL Certificates**
3. Find your domain in the list
4. ⚠️ Will be marked as "Custom" (not Let's Encrypt)

---

## Test Automation

### CI/CD Script

```bash
#!/bin/bash
# test_ssl_integration.sh

set -e

echo "🧪 Testing SSL integration..."

# 1. Create test certificate
sudo python3 letsencrypt_regru_api.py \
    --config test_config.json \
    --test-cert

# 2. Verify files
if [ ! -f "/etc/letsencrypt/live/test.example.com/fullchain.pem" ]; then
    echo "❌ Certificate not created"
    exit 1
fi

# 3. Check validity
openssl x509 -in /etc/letsencrypt/live/test.example.com/cert.pem -noout -checkend 0
if [ $? -eq 0 ]; then
    echo "✅ Certificate is valid"
else
    echo "❌ Certificate is invalid"
    exit 1
fi

echo "✅ All tests passed"
```

### Makefile for Testing

```makefile
.PHONY: test-ssl test-npm test-all

test-ssl:
	@echo "Creating test certificate..."
	sudo make test-cert
	@echo "Verifying files..."
	test -f /etc/letsencrypt/live/$(DOMAIN)/fullchain.pem
	@echo "✅ SSL test passed"

test-npm:
	@echo "Checking NPM integration..."
	# Your NPM API checks
	@echo "✅ NPM test passed"

test-all: test-ssl test-npm
	@echo "✅ All tests passed"
```

---

## Transition to Production

### Step 1: Testing

```bash
# 1. Create test certificate
sudo make test-cert

# 2. Verify with NPM
# Open https://your-domain and check

# 3. Ensure everything works
```

### Step 2: Switch to Let's Encrypt

```bash
# 1. Remove test certificate
sudo rm -rf /etc/letsencrypt/live/your-domain/

# 2. Get real certificate
sudo make obtain

# 3. Verify update in NPM
sudo make status
```

---

## FAQ

### Q: Why does browser show warning?

**A:** Self-signed certificates are not trusted by browsers. This is normal for testing.

To avoid browser warning (local testing only):
1. Chrome: `chrome://flags/#allow-insecure-localhost`
2. Firefox: Click "Advanced" → "Accept the Risk"

### Q: Can I use in production?

**A:** ❌ **NO!** Test certificates are for development and testing only.

### Q: How often can I create test certificates?

**A:** ✅ Unlimited! No limits whatsoever.

### Q: Do they upload to NPM automatically?

**A:** ✅ Yes, if `npm_enabled: true` in configuration.

### Q: Do they work with wildcard domains?

**A:** ✅ Yes! Just set `"wildcard": true` in configuration.

### Q: How to check expiration date?

```bash
openssl x509 -in /etc/letsencrypt/live/your-domain/cert.pem -noout -dates
```

### Q: How to change validity period?

Edit `validity_days` in `generate_self_signed_certificate()` function:

```python
validity_days: int = 365  # Change to desired number of days
```

---

## Troubleshooting

### Error: Permission denied

```bash
# Run with sudo
sudo make test-cert
```

### Error: Module 'cryptography' not found

```bash
# Install dependencies
sudo pip3 install cryptography
```

### NPM doesn't show certificate

1. Check NPM settings in configuration
2. Check logs: `sudo make logs`
3. Try uploading manually via NPM web interface

### Certificate not created

```bash
# Check permissions
ls -la /etc/letsencrypt/live/

# Create directory manually
sudo mkdir -p /etc/letsencrypt/live/

# Check configuration
sudo make check-config
```

---

## Usage Examples

### Docker Development

```dockerfile
FROM nginx:alpine

# Copy test certificate
COPY test-certs/ /etc/nginx/ssl/

# Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 443
```

### Local Testing

```bash
# Create certificate for localhost
sudo python3 letsencrypt_regru_api.py --test-cert

# Add to /etc/hosts
echo "127.0.0.1 test.example.com" | sudo tee -a /etc/hosts

# Start nginx
sudo nginx -t && sudo nginx -s reload

# Open in browser
open https://test.example.com
```

### Automated Testing Before Deployment

```bash
#!/bin/bash
# pre-deploy.sh

# Test SSL check
sudo make test-cert
if [ $? -eq 0 ]; then
    echo "✅ Test certificate created successfully"
    echo "✅ Ready for production certificate"
    sudo make obtain
else
    echo "❌ Error creating test certificate"
    exit 1
fi
```

---

## Additional Resources

- 📘 [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)
- 📘 [OpenSSL Documentation](https://www.openssl.org/docs/)
- 📘 [Nginx Proxy Manager Docs](https://nginxproxymanager.com/guide/)

---

## Quick Reference

```bash
# Installation
sudo make install

# Configuration
sudo nano /etc/letsencrypt/regru_config.json

# Create test certificate
sudo make test-cert

# Verify
sudo make check-config
sudo make status

# Switch to production
sudo rm -rf /etc/letsencrypt/live/domain/
sudo make obtain

# Automatic renewal
sudo make run
```

**Done!** 🎉 Now you can test SSL certificates without limits!
