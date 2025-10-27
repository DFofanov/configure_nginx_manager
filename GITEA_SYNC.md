# 🔄 Синхронизация Gitea → GitHub

Автоматическая синхронизация репозитория из Gitea в GitHub после каждого push.

---

## 📋 Доступные методы

| Метод | Сложность | Скорость | Надежность | Рекомендация |
|-------|-----------|----------|------------|--------------|
| **1. Git Hooks** | ⭐⭐ | ⚡ Мгновенно | ✅ Высокая | Рекомендуется |
| **2. GitHub Actions** | ⭐⭐⭐ | ⏱️ 1-5 мин | ✅ Высокая | Для сложных сценариев |
| **3. Gitea Mirror** | ⭐ | ⏱️ По расписанию | ⭐⭐ Средняя | Самый простой |
| **4. Двойной Remote** | ⭐ | ⚡ Мгновенно | ⭐⭐ Средняя | Локальная работа |

---

## 🚀 Метод 1: Git Hooks (Рекомендуется)

### Установка

**1. На сервере Gitea найдите путь к репозиторию:**
```bash
# Обычно это:
/var/lib/gitea/data/gitea-repositories/username/configure_nginx_manager.git
# Или
/home/git/gitea-repositories/username/configure_nginx_manager.git
```

**2. Создайте post-receive hook:**
```bash
cd /path/to/gitea/repos/username/configure_nginx_manager.git/hooks/
nano post-receive
```

**3. Вставьте содержимое** из файла `gitea-hooks/post-receive` (в этом репозитории)

**4. Настройте параметры:**
```bash
# В файле post-receive измените:
GITHUB_REPO="git@github.com:YOUR_USERNAME/configure_nginx_manager.git"
# Или для HTTPS с токеном:
GITHUB_REPO="https://YOUR_TOKEN@github.com/YOUR_USERNAME/configure_nginx_manager.git"
```

**5. Сделайте скрипт исполняемым:**
```bash
chmod +x post-receive
```

**6. Создайте директорию для логов:**
```bash
mkdir -p /var/log/gitea
chown git:git /var/log/gitea
```

### Настройка SSH ключей (для git@github.com)

**На сервере Gitea:**

**Шаг 1: Определите пользователя Gitea**
```bash
# Проверьте под каким пользователем запущен Gitea
ps aux | grep gitea | grep -v grep

# Обычно это один из:
# - git (стандартная установка)
# - gitea (установка через Docker/LXC)
```

**Шаг 2: Переключитесь на этого пользователя**
```bash
# Попробуйте git:
sudo su - git

# Если не работает, попробуйте gitea:
sudo su - gitea

# Проверьте текущего пользователя
whoami  # Должно быть: git или gitea
```

**Шаг 3: Создайте SSH ключ**
```bash
# Создайте SSH ключ (если его ещё нет)
ssh-keygen -t ed25519 -C "gitea-to-github-sync" -f ~/.ssh/id_ed25519 -N ""

# Скопируйте публичный ключ
cat ~/.ssh/id_ed25519.pub
```

**На GitHub:**
1. Settings → SSH and GPG keys
2. New SSH key
3. Вставьте публичный ключ
4. Save

**⚠️ ВАЖНО: Добавьте GitHub в known_hosts:**
```bash
# От того же пользователя (git или gitea)
ssh-keyscan -H github.com >> ~/.ssh/known_hosts

# Проверьте что ключ добавлен
cat ~/.ssh/known_hosts | grep github.com
```

**Проверка подключения:**
```bash
ssh -T git@github.com
# Должно вывести: Hi username! You've successfully authenticated...
```

### Настройка токена (для HTTPS)

**На GitHub:**
1. Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Выберите scope: `repo` (полный доступ к репозиториям)
4. Скопируйте токен

**В hook файле:**
```bash
GITHUB_REPO="https://ghp_YOUR_TOKEN_HERE@github.com/username/configure_nginx_manager.git"
```

### Тестирование

```bash
# Сделайте тестовый commit в Gitea
cd /tmp
git clone http://gitea.example.com/username/configure_nginx_manager.git
cd configure_nginx_manager
echo "test" >> README.md
git add README.md
git commit -m "Test sync to GitHub"
git push

# Проверьте лог
tail -f /var/log/gitea/github-sync.log

# Проверьте GitHub - изменения должны появиться
```

---

## 🔄 Метод 2: GitHub Actions

### Установка

**1. Создайте workflow в GitHub репозитории:**

Файл уже создан: `.github/workflows/sync-from-gitea.yml`

**2. Настройте секреты в GitHub:**

GitHub Repository → Settings → Secrets and variables → Actions → New repository secret

Добавьте:
- **Name**: `GITEA_URL`
  - **Value**: `https://gitea.example.com/username/configure_nginx_manager.git`

- **Name**: `GITEA_TOKEN`
  - **Value**: Токен доступа Gitea

### Получение токена Gitea

**В Gitea:**
1. Settings → Applications → Generate New Token
2. Token Name: "GitHub Sync"
3. Select permissions: `read:repository`
4. Generate Token
5. Скопируйте токен

### Запуск синхронизации

**Автоматически (по расписанию):**
- Каждый час проверяет изменения

**Вручную:**
1. GitHub → Actions
2. Выберите workflow "Sync from Gitea"
3. Run workflow

**Через webhook от Gitea:**

В Gitea репозитории:
1. Settings → Webhooks → Add Webhook → Gitea
2. Target URL: `https://api.github.com/repos/USERNAME/configure_nginx_manager/dispatches`
3. HTTP Method: `POST`
4. POST Content Type: `application/json`
5. Secret: оставьте пустым или используйте
6. Trigger On: `Push events`
7. Body:
```json
{
  "event_type": "gitea-push"
}
```

---

## 🪞 Метод 3: Gitea Mirror (Встроенная функция)

### Настройка

**В Gitea репозитории:**
1. Settings → Repository
2. Прокрутите до "Mirror Settings"
3. Нажмите "Add Push Mirror"
4. Заполните:
   - **Git Remote Repository URL**: `https://github.com/username/configure_nginx_manager.git`
   - **Username**: ваш GitHub username
   - **Password**: GitHub Personal Access Token
   - **Sync Interval**: `8h` (каждые 8 часов) или `0` (только вручную)
5. Save

### Ручная синхронизация

Settings → Repository → Mirror Settings → Sync Now

### Преимущества
- ✅ Встроенная функция
- ✅ Не требует скриптов
- ✅ Управление через веб-интерфейс

### Недостатки
- ⚠️ Работает по расписанию (не мгновенно)
- ⚠️ Доступно не во всех версиях Gitea

---

## 🔀 Метод 4: Двойной Remote

### Для локальной работы

**Настройка:**
```bash
# В вашем локальном репозитории
cd configure_nginx_manager

# Добавьте GitHub как второй remote
git remote add github git@github.com:username/configure_nginx_manager.git

# Или настройте push в оба репозитория одновременно
git remote set-url --add --push origin git@github.com:username/configure_nginx_manager.git

# Проверьте
git remote -v
```

**Использование:**
```bash
# Обычный push (только в Gitea)
git push origin main

# Push в GitHub
git push github main

# Push в оба репозитория
git push origin main
git push github main

# Или создайте alias
git config alias.pushall '!git push origin main && git push github main'
git pushall
```

---

## 🔍 Проверка синхронизации

### Проверка через Git

```bash
# Сравнить коммиты
git ls-remote git@gitea.example.com:username/configure_nginx_manager.git
git ls-remote git@github.com:username/configure_nginx_manager.git

# Должны быть одинаковые SHA
```

### Проверка логов (Метод 1 - Hooks)

```bash
# На сервере Gitea
tail -f /var/log/gitea/github-sync.log
```

### Проверка GitHub Actions (Метод 2)

1. GitHub Repository → Actions
2. Смотрите последние запуски
3. Проверьте логи выполнения

---

## ⚙️ Рекомендованная конфигурация

Для максимальной надежности используйте **комбинацию методов**:

1. **Git Hook** (основной) - мгновенная синхронизация
2. **GitHub Actions** (резервный) - проверка каждый час на случай сбоя hook

### Установка обоих методов

```bash
# 1. Установите Git Hook на сервере Gitea
# (см. Метод 1)

# 2. Настройте GitHub Actions
# (см. Метод 2)

# 3. GitHub Actions будет подхватывать пропущенные изменения
```

---

## 🐛 Устранение проблем

### Проблема: Hook не срабатывает

**Проверка:**
```bash
# На сервере Gitea
ls -la /path/to/repo.git/hooks/post-receive
# Должно быть -rwxr-xr-x

# Проверьте права
chmod +x /path/to/repo.git/hooks/post-receive
chown git:git /path/to/repo.git/hooks/post-receive

# Проверьте лог ошибок Gitea
tail -f /var/log/gitea/gitea.log
```

### Проблема: Permission denied (SSH)

**Решение:**
```bash
# Убедитесь что SSH ключ добавлен в GitHub
ssh -T git@github.com

# Проверьте права на .ssh
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
```

### Проблема: Authentication failed (HTTPS)

**Решение:**
- Проверьте токен GitHub (должен иметь scope `repo`)
- Токен не истёк
- Правильный формат URL: `https://TOKEN@github.com/user/repo.git`

### Проблема: GitHub Actions не запускается

**Решение:**
1. Проверьте секреты в Settings → Secrets
2. Проверьте формат webhook от Gitea
3. Запустите вручную для теста

---

## 📊 Сравнение методов

### Скорость синхронизации
- **Git Hooks**: ⚡ < 1 секунды
- **GitHub Actions (webhook)**: ⏱️ 10-30 секунд
- **GitHub Actions (schedule)**: ⏱️ до 1 часа
- **Gitea Mirror**: ⏱️ по расписанию

### Надежность
- **Git Hooks**: ⭐⭐⭐⭐⭐ (при правильной настройке)
- **GitHub Actions**: ⭐⭐⭐⭐⭐ (очень надежно)
- **Gitea Mirror**: ⭐⭐⭐ (зависит от версии Gitea)
- **Двойной Remote**: ⭐⭐ (требует ручного действия)

---

## 🎯 Итоговая рекомендация

Для проекта `configure_nginx_manager`:

**1. Основной метод: Git Hook**
- Быстро
- Надежно
- Автоматически

**2. Резервный метод: GitHub Actions**
- Проверка каждый час
- Подхватит пропущенные изменения
- Можно запустить вручную

**3. Мониторинг:**
```bash
# Еженедельная проверка
git ls-remote origin | head -1
git ls-remote github | head -1
# SHA должны совпадать
```

---

## 📝 Быстрая установка

```bash
# На сервере Gitea
sudo su - git
cd /path/to/gitea-repositories/username/configure_nginx_manager.git/hooks/

# Скачайте hook
wget https://raw.githubusercontent.com/username/configure_nginx_manager/main/gitea-hooks/post-receive

# Настройте
nano post-receive
# Измените GITHUB_REPO

# Права
chmod +x post-receive

# Тест
echo "test" | ./post-receive
```

Готово! 🎉
