# 🎯 Краткое руководство: Автоматические релизы

## Для GitHub

### 1. Создание релиза

```bash
# Создать тег
git tag -a v1.0.0 -m "Release version 1.0.0"

# Отправить тег
git push origin v1.0.0
```

### 2. Что произойдет автоматически

GitHub Actions запустит `.github/workflows/build-release.yml`:

1. ✅ Сборка Linux версии (Ubuntu runner)
2. ✅ Сборка Windows версии (Windows runner)
3. ✅ Создание пакетов
4. ✅ Генерация SHA256 checksums
5. ✅ Создание GitHub Release
6. ✅ Загрузка артефактов

### 3. Результат

Релиз появится на: `https://github.com/USER/REPO/releases/tag/v1.0.0`

**Файлы:**
- `letsencrypt-regru-linux-x86_64.tar.gz`
- `letsencrypt-regru-linux-x86_64.tar.gz.sha256`
- `letsencrypt-regru-windows-x86_64.zip`
- `letsencrypt-regru-windows-x86_64.zip.sha256`

---

## Для Gitea

### 1. Настройка (один раз)

#### Включить Actions в Gitea:

Отредактируйте `app.ini`:

```ini
[actions]
ENABLED = true
DEFAULT_ACTIONS_URL = https://gitea.com
```

#### Установить Gitea Runner:

```bash
# Скачать
wget https://dl.gitea.com/act_runner/latest/act_runner-linux-amd64 -O act_runner
chmod +x act_runner

# Зарегистрировать
./act_runner register --no-interactive \
  --instance https://your-gitea.com \
  --token YOUR_RUNNER_TOKEN

# Запустить
./act_runner daemon
```

### 2. Создание релиза

```bash
# Создать тег
git tag -a v1.0.0 -m "Release version 1.0.0"

# Отправить тег
git push origin v1.0.0
```

### 3. Что произойдет

Gitea Actions запустит `.gitea/workflows/release.yml`:

1. ✅ Сборка Linux версии
2. ✅ Сборка Windows версии
3. ✅ Создание пакетов
4. ✅ Генерация SHA256 + MD5 checksums
5. ✅ Создание Gitea Release
6. ✅ Детальные release notes

### 4. Результат

Релиз появится на: `https://your-gitea.com/USER/REPO/releases/tag/v1.0.0`

---

## 🔧 Проверка перед релизом

```bash
# 1. Локальная сборка
make clean-build
make release

# 2. Тестирование
make test-build

# 3. Проверка файлов
ls -lh dist/

# 4. Если все OK - создать тег
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

---

## 📊 Мониторинг

### GitHub:
`https://github.com/USER/REPO/actions`

### Gitea:
`https://your-gitea.com/USER/REPO/actions`

---

## 🐛 Если что-то пошло не так

### Удалить тег и релиз:

```bash
# Удалить локальный тег
git tag -d v1.0.0

# Удалить удаленный тег
git push --delete origin v1.0.0

# Удалить релиз вручную через веб-интерфейс
```

### Пересоздать релиз:

```bash
# Исправить проблему
git commit -am "Fix build"

# Пересоздать тег
git tag -a v1.0.0 -m "Release 1.0.0" --force
git push origin v1.0.0 --force
```

---

## 📝 Semantic Versioning

```bash
# Major (несовместимые изменения)
git tag v2.0.0

# Minor (новые функции)
git tag v1.1.0

# Patch (исправления)
git tag v1.0.1

# Pre-release
git tag v1.0.0-beta.1
git tag v1.0.0-rc.1
```

---

**См. также:**
- [.gitea/README.md](.gitea/README.md) - Полная документация по Gitea Actions
- [BUILD_GUIDE.md](BUILD_GUIDE.md) - Руководство по сборке
