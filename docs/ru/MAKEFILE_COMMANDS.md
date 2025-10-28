# Makefile Commands - Quick Reference

## 📋 Категории команд

### 🛠️ Установка и развертывание

```bash
make install              # Полная установка приложения
make uninstall           # Удаление приложения
make status              # Проверка статуса установки
make check-config        # Проверка конфигурации
```

### 🔨 Сборка исполняемых файлов

```bash
make build               # Собрать для текущей ОС
make build-linux         # Собрать для Linux
make build-windows       # Собрать для Windows
make build-all           # Собрать для всех платформ
```

### 📦 Создание пакетов

```bash
make package-linux       # Создать tar.gz для Linux
make package-windows     # Создать zip для Windows
make release             # Полный цикл релиза
```

### 🧪 Тестирование

```bash
make test-run            # Тестовый запуск скрипта
make test-cert           # Создать тестовый сертификат
make test-build          # Протестировать собранный файл
```

### 🚀 Запуск операций

```bash
make run                 # Автоматическая проверка и обновление
make obtain              # Получить новый сертификат
make renew               # Обновить существующий сертификат
```

### 📊 Мониторинг

```bash
make logs                # Показать логи
make status              # Статус служб
```

### 🧹 Очистка

```bash
make clean               # Очистить временные файлы Python
make clean-build         # Очистить артефакты сборки
```

### ℹ️ Информация

```bash
make help                # Показать справку
make build-info          # Информация о среде сборки
```

---

## 🎯 Типовые сценарии

### Первоначальная установка
```bash
sudo make install
sudo make check-config
sudo make test-run
```

### Сборка релиза для GitHub
```bash
make clean-build
make release
# Файлы будут в dist/
```

### Создание тестового окружения
```bash
sudo make install
sudo make test-cert
sudo make status
```

### Обновление сертификата вручную
```bash
sudo make run
sudo make logs
```

### Удаление приложения
```bash
sudo make uninstall
```

---

## 📝 Переменные окружения

Основные переменные определены в Makefile:

```makefile
INSTALL_DIR = /opt/letsencrypt-regru
CONFIG_FILE = /etc/letsencrypt/regru_config.json
LOG_FILE = /var/log/letsencrypt_regru.log
SERVICE_NAME = letsencrypt-regru
PYTHON = python3
```

---

## 🔐 Требуемые права

**Требуют sudo:**
- `make install`
- `make uninstall`
- `make run`
- `make obtain`
- `make renew`
- `make test-run`
- `make test-cert`

**Не требуют sudo:**
- `make build*`
- `make package*`
- `make clean*`
- `make help`
- `make build-info`

---

## 💡 Полезные комбинации

```bash
# Полная переустановка
sudo make uninstall && sudo make install

# Сборка и тестирование
make build && make test-build

# Очистка и релиз
make clean-build && make release

# Проверка после установки
sudo make status && sudo make test-run && sudo make logs
```
