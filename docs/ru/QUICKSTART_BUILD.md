# 🎯 Быстрый старт - Сборка исполняемых файлов

Это краткое руководство для тех, кто хочет быстро собрать исполняемый файл.

## Для Linux

### 1. Установите зависимости
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip git make
```

### 2. Клонируйте репозиторий
```bash
git clone https://github.com/DFofanov/configure_nginx_manager.git
cd configure_nginx_manager
```

### 3. Соберите
```bash
make build-linux
```

### 4. Результат
```bash
ls -lh dist/letsencrypt-regru
# Исполняемый файл готов!
```

### 5. Установите (опционально)
```bash
sudo cp dist/letsencrypt-regru /usr/local/bin/
sudo chmod +x /usr/local/bin/letsencrypt-regru
```

### 6. Используйте
```bash
letsencrypt-regru --help
```

---

## Для Windows

### 1. Установите Python
Скачайте с [python.org](https://www.python.org/downloads/) и установите

### 2. Клонируйте репозиторий
```powershell
git clone https://github.com/DFofanov/configure_nginx_manager.git
cd configure_nginx_manager
```

### 3. Соберите
```powershell
make build-windows
```

### 4. Результат
```powershell
dir dist\letsencrypt-regru.exe
# Исполняемый файл готов!
```

### 5. Используйте
```powershell
.\dist\letsencrypt-regru.exe --help
```

---

## Создание релиза для обеих платформ

```bash
# Это создаст пакеты для Linux и Windows
make release
```

**Результат в `dist/`:**
- `letsencrypt-regru-linux-x86_64.tar.gz`
- `letsencrypt-regru-windows-x86_64.zip`

---

## Полезные команды

```bash
# Показать справку по всем командам
make help

# Информация о среде сборки
make build-info

# Протестировать собранный файл
make test-build

# Очистить артефакты
make clean-build
```

---

## ❓ Проблемы?

См. [BUILD_GUIDE.md](BUILD_GUIDE.md) для подробных инструкций и решения проблем.

---

**Размер файла:** ~40-60 MB (включая Python runtime)  
**Время сборки:** ~2-5 минут  
**Требования:** Python 3.8+, PyInstaller
