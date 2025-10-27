#!/bin/bash

###############################################################################
# Скрипт для создания и обновления SSL сертификата Let's Encrypt
# с использованием DNS-валидации через API reg.ru
#
# Автор: GitHub Copilot
# Дата: 27.10.2025
# Описание: Автоматизация получения wildcard сертификата через Certbot
#           с использованием DNS-01 challenge и API reg.ru
###############################################################################

# ==============================================================================
# КОНФИГУРАЦИЯ
# ==============================================================================

# Учетные данные API reg.ru (получить на https://www.reg.ru/user/account/)
REGRU_USERNAME="your_username"           # Имя пользователя reg.ru
REGRU_PASSWORD="your_password"           # Пароль от аккаунта reg.ru

# Параметры домена и сертификата
DOMAIN="dfv24.com"                       # Основной домен
WILDCARD_DOMAIN="*.dfv24.com"            # Wildcard домен
EMAIL="admin@dfv24.com"                  # Email для уведомлений Let's Encrypt

# Директории для хранения сертификатов
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
CREDENTIALS_DIR="/etc/letsencrypt/credentials"
CREDENTIALS_FILE="$CREDENTIALS_DIR/regru.ini"

# Логирование
LOG_FILE="/var/log/letsencrypt_regru.log"
TIMESTAMP=$(date '+%d.%m.%Y %H:%M:%S')

# ==============================================================================
# ФУНКЦИИ
# ==============================================================================

# Логирование сообщений
log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Проверка установки необходимых пакетов
check_dependencies() {
    log "Проверка зависимостей..."
    
    # Проверка certbot
    if ! command -v certbot &> /dev/null; then
        log "ОШИБКА: certbot не установлен. Установите: apt-get install certbot"
        exit 1
    fi
    
    # Проверка curl
    if ! command -v curl &> /dev/null; then
        log "ОШИБКА: curl не установлен. Установите: apt-get install curl"
        exit 1
    fi
    
    # Проверка jq для обработки JSON
    if ! command -v jq &> /dev/null; then
        log "ОШИБКА: jq не установлен. Установите: apt-get install jq"
        exit 1
    fi
    
    log "Все зависимости установлены"
}

# Создание директории для credentials
setup_credentials_dir() {
    log "Настройка директории для учетных данных..."
    
    if [ ! -d "$CREDENTIALS_DIR" ]; then
        mkdir -p "$CREDENTIALS_DIR"
        chmod 700 "$CREDENTIALS_DIR"
    fi
}

# Создание файла с учетными данными для certbot-dns-regru
create_credentials_file() {
    log "Создание файла с учетными данными reg.ru..."
    
    cat > "$CREDENTIALS_FILE" <<EOF
# Учетные данные API reg.ru для DNS-валидации
dns_regru_username = $REGRU_USERNAME
dns_regru_password = $REGRU_PASSWORD
EOF
    
    chmod 600 "$CREDENTIALS_FILE"
    log "Файл учетных данных создан: $CREDENTIALS_FILE"
}

# Установка плагина certbot-dns-regru (если еще не установлен)
install_certbot_plugin() {
    log "Проверка плагина certbot-dns-regru..."
    
    if ! pip3 list | grep -q certbot-dns-regru; then
        log "Установка certbot-dns-regru..."
        pip3 install certbot-dns-regru
        
        if [ $? -eq 0 ]; then
            log "Плагин certbot-dns-regru успешно установлен"
        else
            log "ОШИБКА: Не удалось установить certbot-dns-regru"
            exit 1
        fi
    else
        log "Плагин certbot-dns-regru уже установлен"
    fi
}

# Получение нового сертификата
obtain_certificate() {
    log "Запрос нового SSL сертификата для домена: $DOMAIN и $WILDCARD_DOMAIN"
    
    certbot certonly \
        --dns-regru \
        --dns-regru-credentials "$CREDENTIALS_FILE" \
        --dns-regru-propagation-seconds 60 \
        -d "$DOMAIN" \
        -d "$WILDCARD_DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive \
        --preferred-challenges dns-01
    
    if [ $? -eq 0 ]; then
        log "Сертификат успешно получен!"
        log "Путь к сертификатам: $CERT_DIR"
        return 0
    else
        log "ОШИБКА: Не удалось получить сертификат"
        return 1
    fi
}

# Обновление существующего сертификата
renew_certificate() {
    log "Проверка и обновление существующих сертификатов..."
    
    certbot renew \
        --dns-regru \
        --dns-regru-credentials "$CREDENTIALS_FILE" \
        --dns-regru-propagation-seconds 60 \
        --non-interactive
    
    if [ $? -eq 0 ]; then
        log "Проверка обновления завершена успешно"
        return 0
    else
        log "ОШИБКА: Проблема при обновлении сертификата"
        return 1
    fi
}

# Проверка срока действия сертификата
check_certificate_expiry() {
    log "Проверка срока действия сертификата..."
    
    if [ -f "$CERT_DIR/cert.pem" ]; then
        EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$CERT_DIR/cert.pem" | cut -d= -f2)
        EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
        CURRENT_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
        
        log "Сертификат истекает: $EXPIRY_DATE (осталось дней: $DAYS_LEFT)"
        
        if [ $DAYS_LEFT -lt 30 ]; then
            log "ВНИМАНИЕ: Сертификат истекает менее чем через 30 дней. Требуется обновление!"
            return 1
        else
            log "Сертификат действителен"
            return 0
        fi
    else
        log "Сертификат не найден. Требуется создание нового сертификата."
        return 2
    fi
}

# Перезагрузка веб-сервера (Nginx/Apache)
reload_webserver() {
    log "Перезагрузка веб-сервера..."
    
    # Определяем, какой веб-сервер используется
    if systemctl is-active --quiet nginx; then
        systemctl reload nginx
        log "Nginx перезагружен"
    elif systemctl is-active --quiet apache2; then
        systemctl reload apache2
        log "Apache перезагружен"
    elif systemctl is-active --quiet httpd; then
        systemctl reload httpd
        log "Apache (httpd) перезагружен"
    else
        log "ВНИМАНИЕ: Веб-сервер не найден или не активен. Пропускаем перезагрузку."
    fi
}

# Отправка уведомления (опционально)
send_notification() {
    local MESSAGE=$1
    log "Уведомление: $MESSAGE"
    
    # Здесь можно добавить отправку email, Telegram, Slack и т.д.
    # Пример: echo "$MESSAGE" | mail -s "SSL Certificate Update" admin@example.com
}

# Вывод информации о сертификате
display_certificate_info() {
    if [ -f "$CERT_DIR/cert.pem" ]; then
        log "=========================================="
        log "Информация о сертификате:"
        log "=========================================="
        openssl x509 -in "$CERT_DIR/cert.pem" -text -noout | grep -E "(Subject:|Issuer:|Not Before|Not After|DNS:)" | tee -a "$LOG_FILE"
        log "=========================================="
        log "Пути к файлам сертификата:"
        log "  Сертификат: $CERT_DIR/cert.pem"
        log "  Приватный ключ: $CERT_DIR/privkey.pem"
        log "  Цепочка: $CERT_DIR/chain.pem"
        log "  Полная цепочка: $CERT_DIR/fullchain.pem"
        log "=========================================="
    fi
}

# ==============================================================================
# ОСНОВНАЯ ЛОГИКА
# ==============================================================================

main() {
    log "=========================================="
    log "Запуск скрипта управления SSL сертификатом"
    log "=========================================="
    
    # Проверка, что скрипт запущен от root
    if [ "$EUID" -ne 0 ]; then 
        log "ОШИБКА: Скрипт должен быть запущен от имени root (sudo)"
        exit 1
    fi
    
    # Проверка зависимостей
    check_dependencies
    
    # Настройка директории и файла учетных данных
    setup_credentials_dir
    create_credentials_file
    
    # Установка плагина certbot-dns-regru
    install_certbot_plugin
    
    # Проверка существования сертификата
    check_certificate_expiry
    CERT_STATUS=$?
    
    if [ $CERT_STATUS -eq 2 ]; then
        # Сертификат не существует - создаем новый
        obtain_certificate
        if [ $? -eq 0 ]; then
            display_certificate_info
            reload_webserver
            send_notification "Новый SSL сертификат успешно создан для $DOMAIN"
        else
            send_notification "ОШИБКА: Не удалось создать SSL сертификат для $DOMAIN"
            exit 1
        fi
    elif [ $CERT_STATUS -eq 1 ]; then
        # Сертификат скоро истекает - обновляем
        renew_certificate
        if [ $? -eq 0 ]; then
            display_certificate_info
            reload_webserver
            send_notification "SSL сертификат успешно обновлен для $DOMAIN"
        else
            send_notification "ОШИБКА: Не удалось обновить SSL сертификат для $DOMAIN"
            exit 1
        fi
    else
        # Сертификат действителен - только проверяем обновление
        log "Сертификат действителен. Выполняем проверку на наличие обновлений..."
        renew_certificate
        display_certificate_info
    fi
    
    log "=========================================="
    log "Скрипт завершен успешно"
    log "=========================================="
}

# Запуск основной функции
main
