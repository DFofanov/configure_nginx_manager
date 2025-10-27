# 🔄 Gitea → GitHub Synchronization

Automatic repository synchronization from Gitea to GitHub after each push.

---

## 📋 Available Methods

| Method | Complexity | Speed | Reliability | Recommendation |
|--------|------------|-------|-------------|----------------|
| **1. Git Hooks** | ⭐⭐ | ⚡ Instant | ✅ High | Recommended |
| **2. GitHub Actions** | ⭐⭐⭐ | ⏱️ 1-5 min | ✅ High | Complex scenarios |
| **3. Gitea Mirror** | ⭐ | ⏱️ Scheduled | ⭐⭐ Medium | Simplest |
| **4. Double Remote** | ⭐ | ⚡ Instant | ⭐⭐ Medium | Local work |

---

## 🚀 Method 1: Git Hooks (Recommended)

### Installation

**1. On Gitea server, find repository path:**
```bash
# Usually:
/var/lib/gitea/data/gitea-repositories/username/configure_nginx_manager.git
# Or
/home/git/gitea-repositories/username/configure_nginx_manager.git
```

**2. Create post-receive hook:**
```bash
cd /path/to/gitea/repos/username/configure_nginx_manager.git/hooks/
nano post-receive
```

**3. Insert content** from `gitea-hooks/post-receive` file (in this repository)

**4. Configure parameters:**
```bash
# In post-receive file, change:
GITHUB_REPO="git@github.com:YOUR_USERNAME/configure_nginx_manager.git"
# Or for HTTPS with token:
GITHUB_REPO="https://YOUR_TOKEN@github.com/YOUR_USERNAME/configure_nginx_manager.git"
```

**5. Make script executable:**
```bash
chmod +x post-receive
```

**6. Create log directory:**
```bash
mkdir -p /var/log/gitea
chown git:git /var/log/gitea
```

### SSH Key Setup (for git@github.com)

**On Gitea server:**
```bash
# Switch to git user
sudo su - git

# Create SSH key
ssh-keygen -t ed25519 -C "gitea-to-github-sync"

# Copy public key
cat ~/.ssh/id_ed25519.pub
```

**On GitHub:**
1. Settings → SSH and GPG keys
2. New SSH key
3. Paste public key
4. Save

**Verification:**
```bash
ssh -T git@github.com
# Should output: Hi username! You've successfully authenticated...
```

### Token Setup (for HTTPS)

**On GitHub:**
1. Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Select scope: `repo` (full repository access)
4. Copy token

**In hook file:**
```bash
GITHUB_REPO="https://ghp_YOUR_TOKEN_HERE@github.com/username/configure_nginx_manager.git"
```

### Testing

```bash
# Make test commit in Gitea
cd /tmp
git clone http://gitea.example.com/username/configure_nginx_manager.git
cd configure_nginx_manager
echo "test" >> README.md
git add README.md
git commit -m "Test sync to GitHub"
git push

# Check log
tail -f /var/log/gitea/github-sync.log

# Check GitHub - changes should appear
```

---

## 🔄 Method 2: GitHub Actions

### Installation

**1. Create workflow in GitHub repository:**

File already created: `.github/workflows/sync-from-gitea.yml`

**2. Configure secrets in GitHub:**

GitHub Repository → Settings → Secrets and variables → Actions → New repository secret

Add:
- **Name**: `GITEA_URL`
  - **Value**: `https://gitea.example.com/username/configure_nginx_manager.git`

- **Name**: `GITEA_TOKEN`
  - **Value**: Gitea access token

### Getting Gitea Token

**In Gitea:**
1. Settings → Applications → Generate New Token
2. Token Name: "GitHub Sync"
3. Select permissions: `read:repository`
4. Generate Token
5. Copy token

### Running Sync

**Automatically (scheduled):**
- Checks for changes every hour

**Manually:**
1. GitHub → Actions
2. Select workflow "Sync from Gitea"
3. Run workflow

**Via Gitea webhook:**

In Gitea repository:
1. Settings → Webhooks → Add Webhook → Gitea
2. Target URL: `https://api.github.com/repos/USERNAME/configure_nginx_manager/dispatches`
3. HTTP Method: `POST`
4. POST Content Type: `application/json`
5. Trigger On: `Push events`
6. Body:
```json
{
  "event_type": "gitea-push"
}
```

---

## 🪞 Method 3: Gitea Mirror (Built-in)

### Setup

**In Gitea repository:**
1. Settings → Repository
2. Scroll to "Mirror Settings"
3. Click "Add Push Mirror"
4. Fill in:
   - **Git Remote Repository URL**: `https://github.com/username/configure_nginx_manager.git`
   - **Username**: your GitHub username
   - **Password**: GitHub Personal Access Token
   - **Sync Interval**: `8h` (every 8 hours) or `0` (manual only)
5. Save

### Manual Sync

Settings → Repository → Mirror Settings → Sync Now

### Advantages
- ✅ Built-in feature
- ✅ No scripts required
- ✅ Web interface management

### Disadvantages
- ⚠️ Works on schedule (not instant)
- ⚠️ Not available in all Gitea versions

---

## 🔀 Method 4: Double Remote

### For Local Work

**Setup:**
```bash
# In your local repository
cd configure_nginx_manager

# Add GitHub as second remote
git remote add github git@github.com:username/configure_nginx_manager.git

# Or configure push to both repositories simultaneously
git remote set-url --add --push origin git@github.com:username/configure_nginx_manager.git

# Verify
git remote -v
```

**Usage:**
```bash
# Normal push (Gitea only)
git push origin main

# Push to GitHub
git push github main

# Push to both repositories
git push origin main
git push github main

# Or create alias
git config alias.pushall '!git push origin main && git push github main'
git pushall
```

---

## 🔍 Sync Verification

### Check via Git

```bash
# Compare commits
git ls-remote git@gitea.example.com:username/configure_nginx_manager.git
git ls-remote git@github.com:username/configure_nginx_manager.git

# Should have identical SHA
```

### Check Logs (Method 1 - Hooks)

```bash
# On Gitea server
tail -f /var/log/gitea/github-sync.log
```

### Check GitHub Actions (Method 2)

1. GitHub Repository → Actions
2. View recent runs
3. Check execution logs

---

## ⚙️ Recommended Configuration

For maximum reliability, use **combination of methods**:

1. **Git Hook** (primary) - instant sync
2. **GitHub Actions** (backup) - hourly check in case of hook failure

### Installing Both Methods

```bash
# 1. Install Git Hook on Gitea server
# (see Method 1)

# 2. Configure GitHub Actions
# (see Method 2)

# 3. GitHub Actions will catch missed changes
```

---

## 🐛 Troubleshooting

### Problem: Hook not firing

**Check:**
```bash
# On Gitea server
ls -la /path/to/repo.git/hooks/post-receive
# Should be -rwxr-xr-x

# Check permissions
chmod +x /path/to/repo.git/hooks/post-receive
chown git:git /path/to/repo.git/hooks/post-receive

# Check Gitea error log
tail -f /var/log/gitea/gitea.log
```

### Problem: Permission denied (SSH)

**Solution:**
```bash
# Ensure SSH key is added to GitHub
ssh -T git@github.com

# Check .ssh permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
```

### Problem: Authentication failed (HTTPS)

**Solution:**
- Check GitHub token (should have `repo` scope)
- Token not expired
- Correct URL format: `https://TOKEN@github.com/user/repo.git`

### Problem: GitHub Actions not triggering

**Solution:**
1. Check secrets in Settings → Secrets
2. Verify webhook format from Gitea
3. Run manually for test

---

## 📊 Method Comparison

### Sync Speed
- **Git Hooks**: ⚡ < 1 second
- **GitHub Actions (webhook)**: ⏱️ 10-30 seconds
- **GitHub Actions (schedule)**: ⏱️ up to 1 hour
- **Gitea Mirror**: ⏱️ scheduled

### Reliability
- **Git Hooks**: ⭐⭐⭐⭐⭐ (when properly configured)
- **GitHub Actions**: ⭐⭐⭐⭐⭐ (very reliable)
- **Gitea Mirror**: ⭐⭐⭐ (depends on Gitea version)
- **Double Remote**: ⭐⭐ (requires manual action)

---

## 🎯 Final Recommendation

For `configure_nginx_manager` project:

**1. Primary method: Git Hook**
- Fast
- Reliable
- Automatic

**2. Backup method: GitHub Actions**
- Hourly check
- Catches missed changes
- Can run manually

**3. Monitoring:**
```bash
# Weekly verification
git ls-remote origin | head -1
git ls-remote github | head -1
# SHA should match
```

---

## 📝 Quick Setup

```bash
# On Gitea server
sudo su - git
cd /path/to/gitea-repositories/username/configure_nginx_manager.git/hooks/

# Download hook
wget https://raw.githubusercontent.com/username/configure_nginx_manager/main/gitea-hooks/post-receive

# Configure
nano post-receive
# Change GITHUB_REPO

# Permissions
chmod +x post-receive

# Test
echo "test" | ./post-receive
```

Done! 🎉

---

## 📚 Additional Resources

- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Gitea Documentation](https://docs.gitea.io/)

---

**Version**: 1.0  
**Author**: Фофанов Дмитрий  
**Date**: October 27, 2025
