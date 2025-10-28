# 🔨 Руководство по сборке исполняемых файлов

Данное руководство описывает процесс компиляции Python-скрипта `letsencrypt_regru_api.py` в исполняемые файлы для Linux и Windows с использованием PyInstaller.

## 📋 Содержание

- [Преимущества исполняемых файлов](#преимущества-исполняемых-файлов)
- [Быстрый старт](#быстрый-старт)
- [Подробные инструкции](#подробные-инструкции)
- [Кросс-компиляция](#кросс-компиляция)
- [Troubleshooting](#troubleshooting)

---

## ✅ Преимущества исполняемых файлов

### Плюсы:
- ✅ **Один файл** - легко распространять и развертывать
- ✅ **Автономность** - не требует установленного Python на целевой системе
- ✅ **Все зависимости включены** - requests, cryptography и certbot модули упакованы
- ✅ **Простота запуска** - просто скачать и запустить

### Минусы:
- ❌ **Большой размер** - ~40-60 MB (включая Python runtime и библиотеки)
- ❌ **Certbot зависимость** - системный certbot все равно требуется
- ❌ **Медленный первый запуск** - распаковка занимает несколько секунд
- ❌ **Требуется пересборка** - при изменении кода нужно пересобирать

---

## 🚀 Быстрый старт

### Сборка для текущей ОС:
```bash
make build
```

### Сборка для всех платформ:
```bash
make build-all
```

### Полный релиз (сборка + пакеты):
```bash
make release
```

---

## 📖 Подробные инструкции

### 1. Установка зависимостей

#### Вариант А: Автоматическая установка
```bash
make install-pyinstaller
```

#### Вариант Б: Ручная установка
```bash
pip install pyinstaller
pip install -r requirements.txt
```

### 2. Сборка для Linux

**На Linux системе:**
```bash
make build-linux
```

**Результат:**
- Файл: `dist/letsencrypt-regru`
- Размер: ~45-55 MB
- Формат: ELF 64-bit executable

**Тестирование:**
```bash
./dist/letsencrypt-regru --help
sudo ./dist/letsencrypt-regru --check -c /etc/letsencrypt-regru/config.json
```

### 3. Сборка для Windows

**На Windows системе (PowerShell/CMD):**
```bash
make build-windows
```

**Результат:**
- Файл: `dist/letsencrypt-regru.exe`
- Размер: ~40-50 MB
- Формат: PE32+ executable (Windows)

**Тестирование:**
```powershell
.\dist\letsencrypt-regru.exe --help
```

### 4. Создание пакетов для распространения

#### Linux пакет (tar.gz):
```bash
make package-linux
```

**Содержимое пакета:**
- `letsencrypt-regru` - исполняемый файл
- `README.md` - документация
- `systemd/` - systemd unit файлы
- `config.json.example` - пример конфигурации

**Результат:** `dist/letsencrypt-regru-linux-x86_64.tar.gz`

#### Windows пакет (zip):
```bash
make package-windows
```

**Результат:** `dist/letsencrypt-regru-windows-x86_64.zip`

### 5. Полный цикл релиза

Создание релиза со всеми артефактами:

```bash
make release
```

**Что происходит:**
1. Очистка старых артефактов (`clean-build`)
2. Установка/обновление PyInstaller
3. Сборка для Linux (`build-linux`)
4. Сборка для Windows (`build-windows`)
5. Создание пакета для Linux (`package-linux`)
6. Создание пакета для Windows (`package-windows`)
7. Генерация SHA256 контрольных сумм

**Результат в `dist/`:**
```
letsencrypt-regru              # Linux executable
letsencrypt-regru.exe          # Windows executable
letsencrypt-regru-linux-x86_64.tar.gz
letsencrypt-regru-windows-x86_64.zip
```

---

## 🔄 Кросс-компиляция

### ⚠️ Важные замечания

**Не рекомендуется:**
- Собирать Linux версию на Windows
- Собирать Windows версию на Linux
- Собирать macOS версию на других ОС

**Причины:**
- Несовместимость системных библиотек
- Разные форматы исполняемых файлов
- Проблемы с путями и разделителями

### Рекомендации

#### Для Linux сборки:
1. Используйте Ubuntu 20.04+ или Debian 10+
2. Установите build-essential
3. Используйте виртуальное окружение Python

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip build-essential
make build-linux
```

#### Для Windows сборки:
1. Используйте Windows 10/11
2. Установите Python 3.8+
3. Используйте PowerShell или CMD

```powershell
python -m pip install --upgrade pip
make build-windows
```

#### Для обеих платформ:
Используйте CI/CD (GitHub Actions, GitLab CI):

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

## 🛠️ Все команды Makefile

### Основные команды:

| Команда | Описание |
|---------|----------|
| `make build` | Собрать для текущей ОС |
| `make build-linux` | Собрать для Linux |
| `make build-windows` | Собрать для Windows |
| `make build-all` | Собрать для всех платформ |
| `make package-linux` | Создать tar.gz пакет |
| `make package-windows` | Создать zip пакет |
| `make release` | Полный цикл релиза |

### Вспомогательные команды:

| Команда | Описание |
|---------|----------|
| `make install-pyinstaller` | Установить PyInstaller |
| `make test-build` | Протестировать собранный файл |
| `make clean-build` | Очистить артефакты сборки |
| `make build-info` | Показать информацию о среде |

---

## 🐛 Troubleshooting

### Проблема: PyInstaller не найден

**Ошибка:**
```
make: pyinstaller: Command not found
```

**Решение:**
```bash
make install-pyinstaller
# или
pip install pyinstaller
```

---

### Проблема: Импорт модулей не работает

**Ошибка:**
```
ModuleNotFoundError: No module named 'requests'
```

**Решение:**
```bash
pip install -r requirements.txt
# или добавьте в PyInstaller команду:
--hidden-import requests
--hidden-import certbot
--hidden-import cryptography
```

---

### Проблема: Большой размер файла

**Размер ~100+ MB вместо 40-60 MB**

**Причины:**
- Включены лишние модули
- Не используется `--onefile`
- Включены debug символы

**Решение:**
```bash
# Используйте флаги оптимизации:
pyinstaller --onefile \
  --strip \
  --exclude-module tkinter \
  --exclude-module matplotlib \
  letsencrypt_regru_api.py
```

---

### Проблема: Certbot не работает в исполняемом файле

**Ошибка:**
```
certbot: command not found
```

**Решение:**

Certbot вызывается через `subprocess` и должен быть установлен в системе:

**Linux:**
```bash
sudo apt-get install certbot
```

**Windows:**
- Не поддерживается напрямую
- Используйте WSL или Docker

---

### Проблема: Права доступа к файлам

**Ошибка:**
```
Permission denied: /etc/letsencrypt/
```

**Решение:**
```bash
# Linux/macOS
sudo ./dist/letsencrypt-regru --check

# Или установите правильные права:
sudo chmod +x ./dist/letsencrypt-regru
sudo chown root:root ./dist/letsencrypt-regru
```

---

### Проблема: Медленный запуск

**Первый запуск занимает 5-10 секунд**

**Причина:**
PyInstaller распаковывает файлы во временную директорию при каждом запуске.

**Решение:**
- Это нормальное поведение для `--onefile`
- Используйте `--onedir` для более быстрого запуска (но будет много файлов)
- Кэшируйте временную директорию (автоматически)

---

### Проблема: Антивирус блокирует файл

**Windows Defender помечает .exe как вирус**

**Причины:**
- Самораспаковывающийся архив похож на вредоносное ПО
- Отсутствие цифровой подписи
- Малоизвестный исполняемый файл

**Решение:**
1. **Добавьте в исключения:**
   - Windows Defender → Settings → Exclusions
   
2. **Подпишите файл цифровой подписью:**
   ```bash
   # Требуется сертификат Code Signing
   signtool sign /f cert.pfx /p password dist/letsencrypt-regru.exe
   ```

3. **Проверьте на VirusTotal:**
   - Загрузите файл на virustotal.com
   - Добавьте результаты в README

---

## 📊 Сравнение: Python vs Исполняемый файл

| Характеристика | Python скрипт | Исполняемый файл |
|----------------|---------------|------------------|
| Размер | ~50 KB | ~40-60 MB |
| Зависимости | Требует Python + pip | Автономный |
| Скорость запуска | Быстро (~1 сек) | Медленно (~5-10 сек) |
| Обновление | Просто заменить .py | Требуется пересборка |
| Совместимость | Любая ОС с Python | Только для целевой ОС |
| Установка | Требует venv setup | Скачать и запустить |
| Certbot | Через subprocess | Через subprocess |

---

## 🎯 Рекомендации

### Используйте Python скрипт если:
- ✅ Python уже установлен в системе
- ✅ Нужны частые обновления кода
- ✅ Используете виртуальное окружение
- ✅ Работаете на серверах (production)

### Используйте исполняемый файл если:
- ✅ Python не установлен
- ✅ Нужна простота развертывания
- ✅ Распространяете для конечных пользователей
- ✅ Тестирование на чистых системах

---

## 📦 Пример использования собранного файла

### Linux:

```bash
# Скачать и распаковать
wget https://github.com/user/repo/releases/download/v1.0/letsencrypt-regru-linux-x86_64.tar.gz
tar -xzf letsencrypt-regru-linux-x86_64.tar.gz

# Установить
sudo mv letsencrypt-regru /usr/local/bin/
sudo chmod +x /usr/local/bin/letsencrypt-regru

# Использовать
sudo letsencrypt-regru --help
sudo letsencrypt-regru --check -c /etc/letsencrypt-regru/config.json
```

### Windows:

```powershell
# Скачать и распаковать
Invoke-WebRequest -Uri "https://github.com/user/repo/releases/download/v1.0/letsencrypt-regru-windows-x86_64.zip" -OutFile "letsencrypt-regru.zip"
Expand-Archive -Path letsencrypt-regru.zip -DestinationPath "C:\Program Files\LetsEncrypt-RegRu"

# Использовать
cd "C:\Program Files\LetsEncrypt-RegRu"
.\letsencrypt-regru.exe --help
```

---

## 📝 Дополнительные ресурсы

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller FAQ](https://pyinstaller.org/en/stable/FAQ.html)
- [Building Cross-Platform Applications](https://pyinstaller.org/en/stable/operating-mode.html)

---

## 📄 Лицензия

Этот проект использует лицензию согласно основному README.md.

---

**Автор:** Фофанов Дмитрий  
**Дата обновления:** 28.10.2025
