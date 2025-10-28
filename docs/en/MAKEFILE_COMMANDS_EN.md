# Makefile Commands - Quick Reference

## 📋 Command Categories

### 🛠️ Installation and Deployment

```bash
make install              # Full application installation
make uninstall           # Remove application
make status              # Check installation status
make check-config        # Verify configuration
```

### 🔨 Building Executables

```bash
make build               # Build for current OS
make build-linux         # Build for Linux
make build-windows       # Build for Windows
make build-all           # Build for all platforms
```

### 📦 Creating Packages

```bash
make package-linux       # Create tar.gz for Linux
make package-windows     # Create zip for Windows
make release             # Full release cycle
```

### 🧪 Testing

```bash
make test-run            # Test script run
make test-cert           # Create test certificate
make test-build          # Test built file
```

### 🚀 Running Operations

```bash
make run                 # Automatic check and renewal
make obtain              # Obtain new certificate
make renew               # Renew existing certificate
```

### 📊 Monitoring

```bash
make logs                # Show logs
make status              # Service status
```

### 🧹 Cleanup

```bash
make clean               # Clean Python temporary files
make clean-build         # Clean build artifacts
```

### ℹ️ Information

```bash
make help                # Show help
make build-info          # Build environment information
```

---

## 🎯 Common Scenarios

### Initial Installation
```bash
sudo make install
sudo make check-config
sudo make test-run
```

### Building Release for GitHub
```bash
make clean-build
make release
# Files will be in dist/
```

### Creating Test Environment
```bash
sudo make install
sudo make test-cert
sudo make status
```

### Manual Certificate Renewal
```bash
sudo make run
sudo make logs
```

### Removing Application
```bash
sudo make uninstall
```

---

## 📝 Environment Variables

Main variables defined in Makefile:

```makefile
INSTALL_DIR = /opt/letsencrypt-regru
CONFIG_FILE = /etc/letsencrypt/regru_config.json
LOG_FILE = /var/log/letsencrypt_regru.log
SERVICE_NAME = letsencrypt-regru
PYTHON = python3
```

---

## 🔐 Required Permissions

**Require sudo:**
- `make install`
- `make uninstall`
- `make run`
- `make obtain`
- `make renew`
- `make test-run`
- `make test-cert`

**Don't require sudo:**
- `make build*`
- `make package*`
- `make clean*`
- `make help`
- `make build-info`

---

## 💡 Useful Combinations

```bash
# Full reinstallation
sudo make uninstall && sudo make install

# Build and test
make build && make test-build

# Clean and release
make clean-build && make release

# Post-installation check
sudo make status && sudo make test-run && sudo make logs
```

---

**Author:** Dmitry Fofanov  
**Last Updated:** October 28, 2025
