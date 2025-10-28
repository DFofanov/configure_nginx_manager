# 🔨 Executable Build Guide

This guide describes the process of compiling the `letsencrypt_regru_api.py` Python script into executable files for Linux and Windows using PyInstaller.

## 📋 Table of Contents

- [Advantages of Executable Files](#advantages-of-executable-files)
- [Quick Start](#quick-start)
- [Detailed Instructions](#detailed-instructions)
- [Cross-Compilation](#cross-compilation)
- [Troubleshooting](#troubleshooting)

---

## ✅ Advantages of Executable Files

### Pros:
- ✅ **Single file** - easy to distribute and deploy
- ✅ **Standalone** - no Python installation required on target system
- ✅ **All dependencies included** - requests, cryptography, and certbot modules are bundled
- ✅ **Simple execution** - just download and run

### Cons:
- ❌ **Large size** - ~40-60 MB (including Python runtime and libraries)
- ❌ **Certbot dependency** - system certbot is still required
- ❌ **Slow first launch** - unpacking takes a few seconds
- ❌ **Rebuild required** - code changes require recompilation

---

## 🚀 Quick Start

### Build for current OS:
```bash
make build
```

### Build for all platforms:
```bash
make build-all
```

### Full release (build + packages):
```bash
make release
```

---

## 📖 Detailed Instructions

### 1. Install Dependencies

#### Option A: Automatic Installation
```bash
make install-pyinstaller
```

#### Option B: Manual Installation
```bash
pip install pyinstaller
pip install -r requirements.txt
```

### 2. Build for Linux

**On Linux system:**
```bash
make build-linux
```

**Result:**
- File: `dist/letsencrypt-regru`
- Size: ~45-55 MB
- Format: ELF 64-bit executable

**Testing:**
```bash
./dist/letsencrypt-regru --help
sudo ./dist/letsencrypt-regru --check -c /etc/letsencrypt-regru/config.json
```

### 3. Build for Windows

**On Windows system (PowerShell/CMD):**
```bash
make build-windows
```

**Result:**
- File: `dist/letsencrypt-regru.exe`
- Size: ~40-50 MB
- Format: PE32+ executable (Windows)

**Testing:**
```powershell
.\dist\letsencrypt-regru.exe --help
```

### 4. Create Distribution Packages

#### Linux package (tar.gz):
```bash
make package-linux
```

**Package contents:**
- `letsencrypt-regru` - executable file
- `README.md` - documentation
- `systemd/` - systemd unit files
- `config.json.example` - configuration example

**Result:** `dist/letsencrypt-regru-linux-x86_64.tar.gz`

#### Windows package (zip):
```bash
make package-windows
```

**Result:** `dist/letsencrypt-regru-windows-x86_64.zip`

### 5. Full Release Cycle

Create release with all artifacts:

```bash
make release
```

**What happens:**
1. Clean old artifacts (`clean-build`)
2. Install/update PyInstaller
3. Build for Linux (`build-linux`)
4. Build for Windows (`build-windows`)
5. Create Linux package (`package-linux`)
6. Create Windows package (`package-windows`)
7. Generate SHA256 checksums

**Result in `dist/`:**
```
letsencrypt-regru              # Linux executable
letsencrypt-regru.exe          # Windows executable
letsencrypt-regru-linux-x86_64.tar.gz
letsencrypt-regru-windows-x86_64.zip
```

---

## 🔄 Cross-Compilation

### ⚠️ Important Notes

**Not recommended:**
- Building Linux version on Windows
- Building Windows version on Linux
- Building macOS version on other OSes

**Reasons:**
- System library incompatibility
- Different executable formats
- Path and separator issues

### Recommendations

#### For Linux builds:
1. Use Ubuntu 20.04+ or Debian 10+
2. Install build-essential
3. Use Python virtual environment

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip build-essential
make build-linux
```

#### For Windows builds:
1. Use Windows 10/11
2. Install Python 3.8+
3. Use PowerShell or CMD

```powershell
python -m pip install --upgrade pip
make build-windows
```

#### For both platforms:
Use CI/CD (GitHub Actions, GitLab CI):

```yaml
# .github/workflows/build.yml
name: Build Releases

on:
  push:
    tags:
      - 'v*'

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Linux
        run: make build-linux

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Windows
        run: make build-windows
```

---

## 🛠️ All Makefile Commands

### Main Commands:

| Command | Description |
|---------|-------------|
| `make build` | Build for current OS |
| `make build-linux` | Build for Linux |
| `make build-windows` | Build for Windows |
| `make build-all` | Build for all platforms |
| `make package-linux` | Create tar.gz package |
| `make package-windows` | Create zip package |
| `make release` | Full release cycle |

### Supporting Commands:

| Command | Description |
|---------|-------------|
| `make install-pyinstaller` | Install PyInstaller |
| `make test-build` | Test built file |
| `make clean-build` | Clean build artifacts |
| `make build-info` | Show environment info |

---

## 🐛 Troubleshooting

### Issue: PyInstaller not found

**Error:**
```
make: pyinstaller: Command not found
```

**Solution:**
```bash
make install-pyinstaller
# or
pip install pyinstaller
```

---

### Issue: Module imports not working

**Error:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
pip install -r requirements.txt
# or add to PyInstaller command:
--hidden-import requests
--hidden-import certbot
--hidden-import cryptography
```

---

### Issue: Large file size

**Size ~100+ MB instead of 40-60 MB**

**Causes:**
- Extra modules included
- Not using `--onefile`
- Debug symbols included

**Solution:**
```bash
# Use optimization flags:
pyinstaller --onefile \
  --strip \
  --exclude-module tkinter \
  --exclude-module matplotlib \
  letsencrypt_regru_api.py
```

---

### Issue: Certbot not working in executable

**Error:**
```
certbot: command not found
```

**Solution:**

Certbot is called via `subprocess` and must be installed on the system:

**Linux:**
```bash
sudo apt-get install certbot
```

**Windows:**
- Not directly supported
- Use WSL or Docker

---

### Issue: File permission errors

**Error:**
```
Permission denied: /etc/letsencrypt/
```

**Solution:**
```bash
# Linux/macOS
sudo ./dist/letsencrypt-regru --check

# Or set proper permissions:
sudo chmod +x ./dist/letsencrypt-regru
sudo chown root:root ./dist/letsencrypt-regru
```

---

### Issue: Slow startup

**First launch takes 5-10 seconds**

**Reason:**
PyInstaller unpacks files to temporary directory on each run.

**Solution:**
- This is normal behavior for `--onefile`
- Use `--onedir` for faster startup (but many files)
- Temporary directory is cached automatically

---

### Issue: Antivirus blocking file

**Windows Defender marks .exe as virus**

**Reasons:**
- Self-extracting archive looks like malware
- No digital signature
- Unknown executable file

**Solution:**
1. **Add to exclusions:**
   - Windows Defender → Settings → Exclusions
   
2. **Sign file with digital signature:**
   ```bash
   # Requires Code Signing certificate
   signtool sign /f cert.pfx /p password dist/letsencrypt-regru.exe
   ```

3. **Check on VirusTotal:**
   - Upload file to virustotal.com
   - Add results to README

---

## 📊 Comparison: Python vs Executable

| Feature | Python Script | Executable File |
|---------|---------------|-----------------|
| Size | ~50 KB | ~40-60 MB |
| Dependencies | Requires Python + pip | Standalone |
| Startup Speed | Fast (~1 sec) | Slow (~5-10 sec) |
| Updates | Just replace .py | Requires rebuild |
| Compatibility | Any OS with Python | Only target OS |
| Installation | Requires venv setup | Download and run |
| Certbot | Via subprocess | Via subprocess |

---

## 🎯 Recommendations

### Use Python script if:
- ✅ Python already installed on system
- ✅ Frequent code updates needed
- ✅ Using virtual environment
- ✅ Working on servers (production)

### Use executable file if:
- ✅ Python not installed
- ✅ Simple deployment needed
- ✅ Distributing to end users
- ✅ Testing on clean systems

---

## 📦 Using Built File Examples

### Linux:

```bash
# Download and extract
wget https://github.com/user/repo/releases/download/v1.0/letsencrypt-regru-linux-x86_64.tar.gz
tar -xzf letsencrypt-regru-linux-x86_64.tar.gz

# Install
sudo mv letsencrypt-regru /usr/local/bin/
sudo chmod +x /usr/local/bin/letsencrypt-regru

# Use
sudo letsencrypt-regru --help
sudo letsencrypt-regru --check -c /etc/letsencrypt-regru/config.json
```

### Windows:

```powershell
# Download and extract
Invoke-WebRequest -Uri "https://github.com/user/repo/releases/download/v1.0/letsencrypt-regru-windows-x86_64.zip" -OutFile "letsencrypt-regru.zip"
Expand-Archive -Path letsencrypt-regru.zip -DestinationPath "C:\Program Files\LetsEncrypt-RegRu"

# Use
cd "C:\Program Files\LetsEncrypt-RegRu"
.\letsencrypt-regru.exe --help
```

---

## 📝 Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller FAQ](https://pyinstaller.org/en/stable/FAQ.html)
- [Building Cross-Platform Applications](https://pyinstaller.org/en/stable/operating-mode.html)

---

## 📄 License

This project uses the license as specified in the main README.md.

---

**Author:** Dmitry Fofanov  
**Last Updated:** October 28, 2025
