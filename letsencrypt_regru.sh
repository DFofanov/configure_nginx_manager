#!/usr/bin/env bash

# ==============================================================================
# Скрипт автоматической установки Let's Encrypt Manager для reg.ru
# Автор: Фофанов Дмитрий
# Дата: 28.10.2025
# ==============================================================================

set -euo pipefail

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Конфигурация по умолчанию
APP_NAME="Let's Encrypt Manager"
APP_DIR="/opt/letsencrypt-regru"
CONFIG_DIR="/etc/letsencrypt-regru"
LOG_DIR="/var/log/letsencrypt-regru"
CERT_DIR="/etc/letsencrypt/live"
VENV_DIR="${APP_DIR}/venv"
PYTHON_VERSION="3"

# ==============================================================================
# Вспомогательные функции
# ==============================================================================

msg_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

msg_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

msg_error() {
    echo -e "${RED}✗${NC} $1"
}

msg_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Проверка запуска от root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        msg_error "Этот скрипт должен быть запущен от имени root"
        msg_info "Используйте: sudo $0"
        exit 1
    fi
}

# Определение дистрибутива
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        msg_error "Не удалось определить операционную систему"
        exit 1
    fi
    
    msg_info "Обнаружена ОС: $OS $VER"
}

# Проверка доступных ресурсов
check_resources() {
    local total_ram=$(free -m | awk 'NR==2{print $2}')
    local available_disk=$(df -m / | awk 'NR==2{print $4}')
    
    msg_info "Доступно RAM: ${total_ram}MB, Свободно на диске: ${available_disk}MB"
    
    if [ "$total_ram" -lt 512 ]; then
        msg_warn "Рекомендуется минимум 512MB RAM"
    fi
    
    if [ "$available_disk" -lt 1024 ]; then
        msg_warn "Рекомендуется минимум 1GB свободного места"
    fi
}

# Установка зависимостей
install_dependencies() {
    header "Установка зависимостей"
    
    case $OS in
        ubuntu|debian)
            msg_info "Обновление списка пакетов..."
            apt-get update -qq
            
            msg_info "Установка базовых пакетов..."
            apt-get install -y -qq \
                python3 \
                python3-pip \
                python3-venv \
                python3-dev \
                build-essential \
                libssl-dev \
                libffi-dev \
                curl \
                git \
                dnsutils \
                certbot \
                openssl
            ;;
        centos|rhel|fedora)
            msg_info "Обновление списка пакетов..."
            yum update -y -q
            
            msg_info "Установка базовых пакетов..."
            yum install -y -q \
                python3 \
                python3-pip \
                python3-devel \
                gcc \
                openssl-devel \
                libffi-devel \
                curl \
                git \
                bind-utils \
                certbot \
                openssl
            ;;
        *)
            msg_error "Неподдерживаемая ОС: $OS"
            exit 1
            ;;
    esac
    
    msg_ok "Зависимости установлены"
}

# Создание структуры директорий
create_directories() {
    header "Создание директорий"
    
    msg_info "Создание структуры директорий..."
    
    mkdir -p "$APP_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$CERT_DIR"
    
    chmod 755 "$APP_DIR"
    chmod 750 "$CONFIG_DIR"
    chmod 755 "$LOG_DIR"
    chmod 755 "$CERT_DIR"
    
    msg_ok "Директории созданы"
}

# Создание виртуального окружения Python
setup_python_venv() {
    header "Настройка Python окружения"
    
    msg_info "Создание виртуального окружения..."
    python3 -m venv "$VENV_DIR"
    
    msg_info "Активация виртуального окружения..."
    source "${VENV_DIR}/bin/activate"
    
    msg_info "Обновление pip..."
    pip install --quiet --upgrade pip setuptools wheel
    
    msg_info "Установка Python зависимостей..."
    pip install --quiet requests cryptography certbot
    
    msg_ok "Python окружение настроено"
}

# Копирование файлов приложения
install_application() {
    header "Установка приложения"
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local github_raw_url="https://raw.githubusercontent.com/DFofanov/configure_nginx_manager/refs/heads/master"
    
    msg_info "Установка основного скрипта..."
    
    # Проверяем наличие файла в текущей директории
    if [ -f "${script_dir}/letsencrypt_regru_api.py" ]; then
        msg_info "Файл найден локально, копируем из ${script_dir}"
        cp "${script_dir}/letsencrypt_regru_api.py" "${APP_DIR}/"
        chmod 755 "${APP_DIR}/letsencrypt_regru_api.py"
        msg_ok "Файл скопирован из локальной директории"
    else
        msg_warn "Файл letsencrypt_regru_api.py не найден локально"
        msg_info "Скачивание с GitHub..."
        
        if command -v curl &> /dev/null; then
            if curl -fsSL "${github_raw_url}/letsencrypt_regru_api.py" -o "${APP_DIR}/letsencrypt_regru_api.py"; then
                chmod 755 "${APP_DIR}/letsencrypt_regru_api.py"
                msg_ok "Файл успешно скачан с GitHub"
            else
                msg_error "Не удалось скачать файл с GitHub"
                msg_info "URL: ${github_raw_url}/letsencrypt_regru_api.py"
                exit 1
            fi
        elif command -v wget &> /dev/null; then
            if wget -q "${github_raw_url}/letsencrypt_regru_api.py" -O "${APP_DIR}/letsencrypt_regru_api.py"; then
                chmod 755 "${APP_DIR}/letsencrypt_regru_api.py"
                msg_ok "Файл успешно скачан с GitHub (wget)"
            else
                msg_error "Не удалось скачать файл с GitHub"
                msg_info "URL: ${github_raw_url}/letsencrypt_regru_api.py"
                exit 1
            fi
        else
            msg_error "Не установлены curl или wget для скачивания файлов"
            msg_info "Установите один из них: sudo apt-get install curl"
            exit 1
        fi
    fi
    
    msg_info "Установка дополнительных файлов..."
    
    # config.json.example
    if [ -f "${script_dir}/config.json.example" ]; then
        cp "${script_dir}/config.json.example" "${CONFIG_DIR}/"
        msg_ok "Пример конфигурации скопирован"
    else
        msg_info "Скачивание config.json.example с GitHub..."
        if command -v curl &> /dev/null; then
            curl -fsSL "${github_raw_url}/config.json.example" -o "${CONFIG_DIR}/config.json.example" 2>/dev/null && \
                msg_ok "config.json.example скачан с GitHub" || \
                msg_warn "Не удалось скачать config.json.example"
        fi
    fi
    
    # README.md
    if [ -f "${script_dir}/README.md" ]; then
        cp "${script_dir}/README.md" "${APP_DIR}/"
        msg_ok "README.md скопирован"
    else
        msg_info "Скачивание README.md с GitHub..."
        if command -v curl &> /dev/null; then
            curl -fsSL "${github_raw_url}/README.md" -o "${APP_DIR}/README.md" 2>/dev/null && \
                msg_ok "README.md скачан с GitHub" || \
                msg_warn "Не удалось скачать README.md"
        fi
    fi
    
    msg_info "Установка systemd файлов..."
    
    # Systemd service
    if [ -f "${script_dir}/systemd/letsencrypt-regru.service" ]; then
        cp "${script_dir}/systemd/letsencrypt-regru.service" "/etc/systemd/system/"
        msg_ok "Service файл скопирован"
    else
        msg_info "Скачивание letsencrypt-regru.service с GitHub..."
        if command -v curl &> /dev/null; then
            curl -fsSL "${github_raw_url}/systemd/letsencrypt-regru.service" -o "/etc/systemd/system/letsencrypt-regru.service" 2>/dev/null && \
                msg_ok "Service файл скачан с GitHub" || \
                msg_warn "Не удалось скачать service файл, будет создан автоматически"
        fi
    fi
    
    # Systemd timer
    if [ -f "${script_dir}/systemd/letsencrypt-regru.timer" ]; then
        cp "${script_dir}/systemd/letsencrypt-regru.timer" "/etc/systemd/system/"
        msg_ok "Timer файл скопирован"
    else
        msg_info "Скачивание letsencrypt-regru.timer с GitHub..."
        if command -v curl &> /dev/null; then
            curl -fsSL "${github_raw_url}/systemd/letsencrypt-regru.timer" -o "/etc/systemd/system/letsencrypt-regru.timer" 2>/dev/null && \
                msg_ok "Timer файл скачан с GitHub" || \
                msg_warn "Не удалось скачать timer файл, будет создан автоматически"
        fi
    fi
    
    msg_ok "Приложение установлено"
}

# Создание конфигурационного файла
create_config() {
    header "Создание конфигурации"
    
    local config_file="${CONFIG_DIR}/config.json"
    
    if [ -f "$config_file" ]; then
        msg_warn "Файл конфигурации уже существует: $config_file"
        read -p "Перезаписать? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            msg_info "Пропуск создания конфигурации"
            return
        fi
    fi
    
    msg_info "Интерактивная настройка конфигурации..."
    echo ""
    
    read -p "Введите ваш домен (например, example.com): " domain
    read -p "Введите email для уведомлений Let's Encrypt: " email
    read -p "Введите имя пользователя reg.ru: " regru_user
    read -s -p "Введите пароль reg.ru: " regru_pass
    echo ""
    
    read -p "Создать wildcard сертификат (*.${domain})? (Y/n): " -n 1 -r
    echo ""
    wildcard="true"
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        wildcard="false"
    fi
    
    read -p "Включить интеграцию с Nginx Proxy Manager? (y/N): " -n 1 -r
    echo ""
    npm_enabled="false"
    npm_host="http://10.10.10.14:81"
    npm_email="admin@example.com"
    npm_password="changeme"
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm_enabled="true"
        read -p "Введите адрес NPM (например, http://10.10.10.14:81): " npm_host
        read -p "Введите email для входа в NPM: " npm_email
        read -s -p "Введите пароль NPM: " npm_password
        echo ""
    fi
    
    cat > "$config_file" <<EOF
{
    "regru_username": "${regru_user}",
    "regru_password": "${regru_pass}",
    "domain": "${domain}",
    "wildcard": ${wildcard},
    "email": "${email}",
    "cert_dir": "${CERT_DIR}",
    "log_file": "${LOG_DIR}/letsencrypt_regru.log",
    "dns_propagation_wait": 60,
    "dns_check_attempts": 10,
    "dns_check_interval": 10,
    "renewal_days": 30,
    "npm_enabled": ${npm_enabled},
    "npm_host": "${npm_host}",
    "npm_email": "${npm_email}",
    "npm_password": "${npm_password}"
}
EOF
    
    chmod 600 "$config_file"
    
    msg_ok "Конфигурация создана: $config_file"
}

# Создание systemd сервиса для автоматического обновления
create_systemd_service() {
    header "Настройка systemd сервиса"
    
    msg_info "Создание systemd service..."
    
    cat > /etc/systemd/system/letsencrypt-regru.service <<EOF
[Unit]
Description=Let's Encrypt Certificate Manager for reg.ru
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=root
WorkingDirectory=${APP_DIR}
ExecStart=${VENV_DIR}/bin/python ${APP_DIR}/letsencrypt_regru_api.py --config ${CONFIG_DIR}/config.json --auto
StandardOutput=journal
StandardError=journal
SyslogIdentifier=letsencrypt-regru

[Install]
WantedBy=multi-user.target
EOF
    
    msg_info "Создание systemd timer для автоматической проверки..."
    
    cat > /etc/systemd/system/letsencrypt-regru.timer <<EOF
[Unit]
Description=Let's Encrypt Certificate Auto-Renewal Timer
Requires=letsencrypt-regru.service

[Timer]
OnBootSec=15min
OnUnitActiveSec=12h
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    msg_info "Перезагрузка systemd..."
    systemctl daemon-reload
    
    msg_info "Включение timer..."
    systemctl enable letsencrypt-regru.timer
    systemctl start letsencrypt-regru.timer
    
    msg_ok "Systemd сервис настроен и запущен"
}

# Создание удобных алиасов
create_aliases() {
    header "Создание алиасов команд"
    
    msg_info "Создание символической ссылки для команды..."
    
    cat > /usr/local/bin/letsencrypt-regru <<EOF
#!/bin/bash
${VENV_DIR}/bin/python ${APP_DIR}/letsencrypt_regru_api.py --config ${CONFIG_DIR}/config.json "\$@"
EOF
    
    chmod +x /usr/local/bin/letsencrypt-regru
    
    msg_ok "Команда 'letsencrypt-regru' доступна глобально"
}

# Тестовая генерация сертификата
test_certificate() {
    header "Тестирование генерации сертификата"
    
    read -p "Хотите сгенерировать тестовый самоподписанный сертификат? (Y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        msg_info "Генерация тестового сертификата..."
        ${VENV_DIR}/bin/python ${APP_DIR}/letsencrypt_regru_api.py \
            --config ${CONFIG_DIR}/config.json \
            --test-cert
        
        if [ $? -eq 0 ]; then
            msg_ok "Тестовый сертификат успешно создан"
        else
            msg_error "Ошибка при создании тестового сертификата"
        fi
    fi
}

# Вывод итоговой информации
display_summary() {
    header "Установка завершена!"
    
    echo -e "${GREEN}✓ ${APP_NAME} успешно установлен!${NC}"
    echo ""
    echo "📁 Расположение файлов:"
    echo "   • Приложение:    ${APP_DIR}"
    echo "   • Конфигурация:  ${CONFIG_DIR}/config.json"
    echo "   • Логи:          ${LOG_DIR}"
    echo "   • Сертификаты:   ${CERT_DIR}"
    echo ""
    echo "🔧 Основные команды:"
    echo "   • letsencrypt-regru --check          # Проверить срок действия сертификата"
    echo "   • letsencrypt-regru --obtain         # Получить новый production сертификат"
    echo "   • letsencrypt-regru --renew          # Обновить существующий сертификат"
    echo "   • letsencrypt-regru --auto           # Автоматическая проверка и обновление"
    echo ""
    echo "🧪 Команды тестирования:"
    echo "   • letsencrypt-regru --staging        # Тестовый Let's Encrypt (БЕЗ лимитов!)"
    echo "   • letsencrypt-regru --test-cert      # Самоподписанный (локальная разработка)"
    echo "   • letsencrypt-regru --test-api       # Проверить доступ к API reg.ru"
    echo "   • letsencrypt-regru --test-dns       # Протестировать DNS записи"
    echo ""
    echo "📋 Дополнительные команды:"
    echo "   • letsencrypt-regru --help           # Показать полную справку"
    echo "   • letsencrypt-regru --obtain -v      # Подробный вывод (verbose)"
    echo ""
    echo "💡 Рекомендуемый workflow:"
    echo "   1. letsencrypt-regru --test-api      # Проверить API"
    echo "   2. letsencrypt-regru --test-dns      # Проверить DNS"
    echo "   3. letsencrypt-regru --staging       # Тестовый сертификат (сколько угодно раз)"
    echo "   4. letsencrypt-regru --obtain        # Production сертификат"
    echo ""
    echo "⏰ Автоматическое обновление:"
    echo "   • Сервис запускается каждые 12 часов"
    echo "   • Управление: systemctl status letsencrypt-regru.timer"
    echo ""
    echo "� Просмотр логов:"
    echo "   • journalctl -u letsencrypt-regru -f    # Системные логи (реальное время)"
    echo "   • tail -f ${LOG_DIR}/letsencrypt_regru.log  # Файл логов"
    echo ""
    echo "�📖 Документация:"
    echo "   • README: ${APP_DIR}/README.md"
    echo "   • GitHub: https://github.com/DFofanov/configure_nginx_manager"
    echo ""
    
    echo "🔍 Сравнение режимов тестирования:"
    echo ""
    echo "   --staging (рекомендуется для тестирования):"
    echo "     ✅ Полный процесс Let's Encrypt"
    echo "     ✅ Тестирует DNS и автоматизацию"
    echo "     ✅ БЕЗ лимитов (неограниченно)"
    echo "     ⚠️  Браузеры не доверяют (staging CA)"
    echo "     ⏱  ~2-3 минуты"
    echo ""
    echo "   --test-cert (для локальной разработки):"
    echo "     ✅ Мгновенное создание (~1 сек)"
    echo "     ✅ Работает без интернета"
    echo "     ❌ НЕ тестирует DNS/автоматизацию"
    echo "     ⚠️  Браузеры не доверяют (самоподпись)"
    echo ""
    echo "   --test-dns (проверка DNS):"
    echo "     ✅ Тестирует только DNS"
    echo "     ✅ Не создает сертификат"
    echo "     ⏱  ~1-2 минуты"
    echo ""
    
    if grep -q '"npm_enabled": true' "${CONFIG_DIR}/config.json" 2>/dev/null; then
        echo "🔗 Интеграция с Nginx Proxy Manager: ВКЛЮЧЕНА"
        echo "   Production сертификаты будут автоматически синхронизироваться с NPM"
        echo "   (Staging и test-cert сертификаты НЕ загружаются в NPM)"
        echo ""
    fi
    
    msg_warn "ВАЖНО: Отредактируйте конфигурацию при необходимости:"
    echo "        nano ${CONFIG_DIR}/config.json"
    echo ""
    echo "🎉 Готово к использованию! Начните с команды:"
    echo "   letsencrypt-regru --test-api"
    echo ""
}

# Функция обновления
update_application() {
    header "Обновление приложения"
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local github_raw_url="https://raw.githubusercontent.com/DFofanov/configure_nginx_manager/refs/heads/master"
    
    msg_info "Остановка сервиса..."
    systemctl stop letsencrypt-regru.timer || true
    
    msg_info "Обновление файлов..."
    
    # Попытка скопировать локально или скачать с GitHub
    if [ -f "${script_dir}/letsencrypt_regru_api.py" ]; then
        msg_info "Копирование из локальной директории..."
        cp "${script_dir}/letsencrypt_regru_api.py" "${APP_DIR}/"
        chmod 755 "${APP_DIR}/letsencrypt_regru_api.py"
        msg_ok "Файл скопирован локально"
    else
        msg_info "Локальный файл не найден, скачивание с GitHub..."
        if command -v curl &> /dev/null; then
            if curl -fsSL "${github_raw_url}/letsencrypt_regru_api.py" -o "${APP_DIR}/letsencrypt_regru_api.py"; then
                chmod 755 "${APP_DIR}/letsencrypt_regru_api.py"
                msg_ok "Файл успешно скачан с GitHub"
            else
                msg_error "Не удалось скачать файл с GitHub"
                return 1
            fi
        else
            msg_error "Не установлен curl для скачивания файлов"
            msg_info "Установите: sudo apt-get install curl"
            return 1
        fi
    fi
    
    msg_info "Обновление Python зависимостей..."
    source "${VENV_DIR}/bin/activate"
    pip install --quiet --upgrade requests cryptography certbot
    
    msg_info "Перезапуск сервиса..."
    systemctl daemon-reload
    systemctl start letsencrypt-regru.timer
    
    msg_ok "Приложение обновлено"
}

# Функция удаления
uninstall_application() {
    header "Удаление приложения"
    
    msg_warn "ВНИМАНИЕ: Это удалит следующие компоненты:"
    echo "   • Приложение:        ${APP_DIR}"
    echo "   • Systemd сервисы:   /etc/systemd/system/letsencrypt-regru.*"
    echo "   • Команда:           /usr/local/bin/letsencrypt-regru"
    echo ""
    msg_info "Будут сохранены:"
    echo "   • Сертификаты:       ${CERT_DIR}"
    echo "   • Конфигурация:      ${CONFIG_DIR}/config.json (можно удалить отдельно)"
    echo "   • Логи:              ${LOG_DIR} (можно удалить отдельно)"
    echo ""
    read -p "Продолжить удаление? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        msg_info "Отмена удаления"
        exit 0
    fi
    
    msg_info "Остановка и отключение сервисов..."
    systemctl stop letsencrypt-regru.timer || true
    systemctl stop letsencrypt-regru.service || true
    systemctl disable letsencrypt-regru.timer || true
    systemctl disable letsencrypt-regru.service || true
    
    msg_info "Удаление systemd файлов..."
    rm -f /etc/systemd/system/letsencrypt-regru.service
    rm -f /etc/systemd/system/letsencrypt-regru.timer
    systemctl daemon-reload
    
    msg_info "Удаление файлов приложения..."
    rm -rf "$APP_DIR"
    rm -f /usr/local/bin/letsencrypt-regru
    
    msg_ok "Приложение удалено"
    echo ""
    
    # Опционально удаляем конфигурацию
    if [ -d "$CONFIG_DIR" ]; then
        msg_warn "Удалить конфигурацию?"
        echo "   Путь: ${CONFIG_DIR}/config.json"
        read -p "Удалить конфигурацию? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$CONFIG_DIR"
            msg_ok "Конфигурация удалена"
        else
            msg_info "Конфигурация сохранена: ${CONFIG_DIR}/config.json"
        fi
    fi
    
    # Опционально удаляем логи
    if [ -d "$LOG_DIR" ]; then
        msg_warn "Удалить логи?"
        echo "   Путь: ${LOG_DIR}"
        read -p "Удалить логи? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$LOG_DIR"
            msg_ok "Логи удалены"
        else
            msg_info "Логи сохранены: ${LOG_DIR}"
        fi
    fi
    
    echo ""
    msg_ok "Удаление завершено!"
    msg_info "Сертификаты сохранены в: ${CERT_DIR}"
}

# ==============================================================================
# Основная логика
# ==============================================================================

main() {
    clear
    header "${APP_NAME} - Установка"
    
    # Проверка аргументов
    case "${1:-install}" in
        install)
            check_root
            detect_os
            check_resources
            install_dependencies
            create_directories
            setup_python_venv
            install_application
            create_config
            create_systemd_service
            create_aliases
            test_certificate
            display_summary
            ;;
        update)
            check_root
            update_application
            msg_ok "Обновление завершено"
            ;;
        uninstall)
            check_root
            uninstall_application
            ;;
        *)
            echo "Использование: $0 {install|update|uninstall}"
            echo ""
            echo "  install    - Установить приложение (по умолчанию)"
            echo "  update     - Обновить приложение"
            echo "  uninstall  - Удалить приложение"
            exit 1
            ;;
    esac
}

# Запуск
main "${@}"
