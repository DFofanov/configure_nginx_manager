# 🎯 Quick Start - Building Executables

This is a quick guide for those who want to build an executable file fast.

## For Linux

### 1. Install dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip git make
```

### 2. Clone repository
```bash
git clone https://github.com/DFofanov/configure_nginx_manager.git
cd configure_nginx_manager
```

### 3. Build
```bash
make build-linux
```

### 4. Result
```bash
ls -lh dist/letsencrypt-regru
# Executable file is ready!
```

### 5. Install (optional)
```bash
sudo cp dist/letsencrypt-regru /usr/local/bin/
sudo chmod +x /usr/local/bin/letsencrypt-regru
```

### 6. Use
```bash
letsencrypt-regru --help
```

---

## For Windows

### 1. Install Python
Download from [python.org](https://www.python.org/downloads/) and install

### 2. Clone repository
```powershell
git clone https://github.com/DFofanov/configure_nginx_manager.git
cd configure_nginx_manager
```

### 3. Build
```powershell
make build-windows
```

### 4. Result
```powershell
dir dist\letsencrypt-regru.exe
# Executable file is ready!
```

### 5. Use
```powershell
.\dist\letsencrypt-regru.exe --help
```

---

## Creating Release for Both Platforms

```bash
# This will create packages for Linux and Windows
make release
```

**Result in `dist/`:**
- `letsencrypt-regru-linux-x86_64.tar.gz`
- `letsencrypt-regru-windows-x86_64.zip`

---

## Useful Commands

```bash
# Show help for all commands
make help

# Build environment information
make build-info

# Test built file
make test-build

# Clean artifacts
make clean-build
```

---

## ❓ Problems?

See [BUILD_GUIDE_EN.md](BUILD_GUIDE_EN.md) for detailed instructions and troubleshooting.

---

**File size:** ~40-60 MB (including Python runtime)  
**Build time:** ~2-5 minutes  
**Requirements:** Python 3.8+, PyInstaller
