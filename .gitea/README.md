# Настройка Gitea Actions для автоматической сборки

## 📋 Предварительные требования

### 1. Gitea с поддержкой Actions

Убедитесь, что ваш Gitea имеет включенные Actions:

```ini
# В app.ini Gitea
[actions]
ENABLED = true
DEFAULT_ACTIONS_URL = https://gitea.com
```

### 2. Gitea Runner

Установите и настройте Gitea Act Runner:

```bash
# Скачать runner
wget https://dl.gitea.com/act_runner/latest/act_runner-linux-amd64 -O act_runner
chmod +x act_runner

# Зарегистрировать runner
./act_runner register --no-interactive \
  --instance https://your-gitea-instance.com \
  --token YOUR_RUNNER_TOKEN \
  --name my-runner

# Запустить runner
./act_runner daemon
```

Или через Docker:

```bash
docker run -d \
  --name gitea-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $PWD/runner-data:/data \
  -e GITEA_INSTANCE_URL=https://your-gitea-instance.com \
  -e GITEA_RUNNER_REGISTRATION_TOKEN=YOUR_TOKEN \
  gitea/act_runner:latest
```

---

## 🚀 Использование

### Создание релиза автоматически

1. **Создайте и отправьте тег:**

```bash
# Создать тег
git tag -a v1.0.0 -m "Release version 1.0.0"

# Отправить тег на сервер
git push origin v1.0.0
```

2. **Gitea автоматически:**
   - Запустит workflow `.gitea/workflows/release.yml`
   - Соберет Linux версию на Ubuntu runner
   - Соберет Windows версию на Windows runner
   - Создаст релиз с артефактами
   - Добавит контрольные суммы SHA256 и MD5

### Ручной запуск workflow

В веб-интерфейсе Gitea:

1. Перейдите в **Repository → Actions**
2. Выберите workflow **Build and Release**
3. Нажмите **Run workflow**
4. Укажите версию (опционально)

---

## 📂 Структура workflows

```
.gitea/
└── workflows/
    ├── build-release.yml    # Простой workflow (совместим с GitHub)
    └── release.yml          # Расширенный workflow с уведомлениями
```

### build-release.yml

Базовый workflow, совместимый с GitHub Actions:
- Сборка для Linux и Windows
- Создание пакетов
- Генерация контрольных сумм
- Создание релиза

**Использование:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

### release.yml

Расширенный workflow с дополнительными возможностями:
- Детальные release notes
- MD5 + SHA256 checksums
- Уведомления после релиза
- Поддержка ручного запуска

**Использование:**
```bash
# Автоматически при теге
git tag v1.0.0
git push origin v1.0.0

# Или вручную через веб-интерфейс
```

---

## 🔧 Настройка

### Переменные окружения

Workflow использует следующие переменные:

| Переменная | Описание | Где установить |
|------------|----------|----------------|
| `GITEA_TOKEN` | Токен для создания релиза | Repository Secrets |
| `GITHUB_TOKEN` | Автоматически (fallback) | Встроенный |

### Создание GITEA_TOKEN

1. В Gitea: **Settings → Applications → Generate New Token**
2. Выберите права: `repo`, `write:packages`
3. Скопируйте токен
4. В репозитории: **Settings → Secrets → Add Secret**
   - Name: `GITEA_TOKEN`
   - Value: ваш токен

---

## 📦 Артефакты релиза

После успешной сборки в релизе будут доступны:

```
letsencrypt-regru-linux-x86_64.tar.gz
letsencrypt-regru-linux-x86_64.tar.gz.sha256
letsencrypt-regru-linux-x86_64.tar.gz.md5
letsencrypt-regru-windows-x86_64.zip
letsencrypt-regru-windows-x86_64.zip.sha256
letsencrypt-regru-windows-x86_64.zip.md5
```

---

## 🐛 Troubleshooting

### Workflow не запускается

**Проблема:** После push тега workflow не запускается

**Решение:**
1. Проверьте, что Actions включены в настройках репозитория
2. Проверьте `.gitea/workflows/*.yml` на синтаксические ошибки
3. Убедитесь, что runner зарегистрирован и запущен

```bash
# Проверить статус runner
./act_runner status

# Посмотреть логи runner
./act_runner daemon --debug
```

---

### Ошибка при сборке Windows

**Проблема:** `make: command not found` на Windows

**Решение:**

Установите Make для Windows или используйте альтернативный workflow:

```yaml
- name: Build Windows executable (без make)
  run: |
    pyinstaller --onefile --name letsencrypt-regru letsencrypt_regru_api.py
```

---

### Релиз создается без файлов

**Проблема:** Релиз создан, но артефакты отсутствуют

**Решение:**

Проверьте логи job `create-release`:

1. Перейдите в **Actions → Build and Release → create-release**
2. Проверьте шаг "Download artifacts"
3. Убедитесь, что предыдущие jobs (`build-linux`, `build-windows`) завершились успешно

---

### Permission denied при создании релиза

**Проблема:** `Error: Resource not accessible by integration`

**Решение:**

1. Проверьте права токена:
   - `GITEA_TOKEN` должен иметь права `repo` и `write:packages`

2. Или используйте встроенный `GITHUB_TOKEN`:
   - Убедитесь, что в настройках репозитория включены Actions

---

## 📊 Мониторинг сборок

### Просмотр логов

1. **Web UI:**
   - Repository → Actions
   - Выберите workflow run
   - Кликните на job для просмотра логов

2. **API:**
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" \
     https://your-gitea.com/api/v1/repos/USER/REPO/actions/runs
   ```

### Статус badges

Добавьте в README.md:

```markdown
[![Build Status](https://your-gitea.com/USER/REPO/actions/workflows/release.yml/badge.svg)](https://your-gitea.com/USER/REPO/actions)
```

---

## 🔄 Автоматизация релизов

### Semantic Versioning

Используйте теги с семантическим версионированием:

```bash
# Major release (несовместимые изменения)
git tag v2.0.0

# Minor release (новые функции)
git tag v1.1.0

# Patch release (исправления)
git tag v1.0.1
```

### Pre-release

Для тестовых релизов используйте suffix:

```bash
git tag v1.0.0-beta.1
git tag v1.0.0-rc.1
```

В workflow автоматически будет установлен `prerelease: true` для таких тегов.

---

## 📝 Changelog автоматизация

### Использование conventional commits

```bash
git commit -m "feat: добавлена поддержка wildcard сертификатов"
git commit -m "fix: исправлена ошибка загрузки в NPM"
git commit -m "docs: обновлена документация"
```

### Генерация CHANGELOG.md

Добавьте в workflow:

```yaml
- name: Generate Changelog
  run: |
    git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"- %s" > CHANGELOG.md
```

---

## 🎯 Рекомендации

1. **Используйте теги только для стабильных релизов**
   - Тестируйте перед созданием тега
   - Проверяйте сборку локально: `make release`

2. **Проверяйте контрольные суммы**
   - Всегда включайте SHA256 и MD5
   - Документируйте процесс проверки для пользователей

3. **Версионирование**
   - Следуйте семантическому версионированию
   - Документируйте breaking changes

4. **Тестирование**
   - Запускайте workflow вручную перед тегированием
   - Проверяйте артефакты после сборки

---

## 🔗 Полезные ссылки

- [Gitea Actions Documentation](https://docs.gitea.com/next/usage/actions/overview)
- [Act Runner GitHub](https://github.com/nektos/act)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

**Примечание:** Эти workflows совместимы с GitHub Actions и могут использоваться на обеих платформах.
