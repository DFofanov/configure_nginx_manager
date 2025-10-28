# 🎯 Quick Guide: Automatic Releases

## For GitHub

### 1. Creating a Release

```bash
# Create tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag
git push origin v1.0.0
```

### 2. What Happens Automatically

GitHub Actions will run `.github/workflows/build-release.yml`:

1. ✅ Build Linux version (Ubuntu runner)
2. ✅ Build Windows version (Windows runner)
3. ✅ Create packages
4. ✅ Generate SHA256 checksums
5. ✅ Create GitHub Release
6. ✅ Upload artifacts

### 3. Result

Release will appear at: `https://github.com/USER/REPO/releases/tag/v1.0.0`

**Files:**
- `letsencrypt-regru-linux-x86_64.tar.gz`
- `letsencrypt-regru-linux-x86_64.tar.gz.sha256`
- `letsencrypt-regru-windows-x86_64.zip`
- `letsencrypt-regru-windows-x86_64.zip.sha256`

---

## For Gitea

### 1. Setup (one time)

#### Enable Actions in Gitea:

Edit `app.ini`:

```ini
[actions]
ENABLED = true
DEFAULT_ACTIONS_URL = https://gitea.com
```

#### Install Gitea Runner:

```bash
# Download
wget https://dl.gitea.com/act_runner/latest/act_runner-linux-amd64 -O act_runner
chmod +x act_runner

# Register
./act_runner register --no-interactive \
  --instance https://your-gitea.com \
  --token YOUR_RUNNER_TOKEN

# Run
./act_runner daemon
```

### 2. Creating a Release

```bash
# Create tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag
git push origin v1.0.0
```

### 3. What Happens

Gitea Actions will run `.gitea/workflows/release.yml`:

1. ✅ Build Linux version
2. ✅ Build Windows version
3. ✅ Create packages
4. ✅ Generate SHA256 + MD5 checksums
5. ✅ Create Gitea Release
6. ✅ Detailed release notes

### 4. Result

Release will appear at: `https://your-gitea.com/USER/REPO/releases/tag/v1.0.0`

---

## 🔧 Pre-Release Checklist

```bash
# 1. Local build
make clean-build
make release

# 2. Testing
make test-build

# 3. Check files
ls -lh dist/

# 4. If all OK - create tag
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

---

## 📊 Monitoring

### GitHub:
`https://github.com/USER/REPO/actions`

### Gitea:
`https://your-gitea.com/USER/REPO/actions`

---

## 🐛 If Something Goes Wrong

### Delete tag and release:

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push --delete origin v1.0.0

# Delete release manually via web interface
```

### Recreate release:

```bash
# Fix the issue
git commit -am "Fix build"

# Recreate tag
git tag -a v1.0.0 -m "Release 1.0.0" --force
git push origin v1.0.0 --force
```

---

## 📝 Semantic Versioning

```bash
# Major (breaking changes)
git tag v2.0.0

# Minor (new features)
git tag v1.1.0

# Patch (bug fixes)
git tag v1.0.1

# Pre-release
git tag v1.0.0-beta.1
git tag v1.0.0-rc.1
```

---

**See also:**
- [.gitea/README.md](../../.gitea/README.md) - Full Gitea Actions documentation
- [BUILD_GUIDE_EN.md](BUILD_GUIDE_EN.md) - Build guide

---

**Author:** Dmitry Fofanov  
**Last Updated:** October 28, 2025
