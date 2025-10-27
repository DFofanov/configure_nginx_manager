#!/bin/bash

# ==============================================================================
# Скрипт для быстрого создания тестового самоподписанного SSL сертификата
# Использует: openssl (альтернатива Python скрипту)
# ==============================================================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Параметры по умолчанию
DOMAIN="${1:-example.com}"
WILDCARD="${2:-yes}"
CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"
VALIDITY_DAYS=90

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Создание тестового самоподписанного SSL сертификата           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Параметры:${NC}"
echo -e "  Домен: ${GREEN}${DOMAIN}${NC}"
echo -e "  Wildcard: ${GREEN}${WILDCARD}${NC}"
echo -e "  Срок действия: ${GREEN}${VALIDITY_DAYS} дней${NC}"
echo -e "  Директория: ${GREEN}${CERT_DIR}${NC}"
echo ""
echo -e "${YELLOW}⚠️  ВНИМАНИЕ: Это тестовый сертификат для разработки!${NC}"
echo -e "${YELLOW}   Браузеры будут показывать предупреждение безопасности.${NC}"
echo ""

# Проверка прав root
if [ "$(id -u)" != "0" ]; then
    echo -e "${RED}✗ Требуются права root${NC}"
    echo -e "Запустите: sudo $0 $@"
    exit 1
fi

# Создание директории
echo -e "${YELLOW}→ Создание директории...${NC}"
mkdir -p "${CERT_DIR}"
cd "${CERT_DIR}"

# Подготовка конфигурации для альтернативных имен (SAN)
if [ "${WILDCARD}" = "yes" ]; then
    SAN="DNS:${DOMAIN},DNS:*.${DOMAIN}"
else
    SAN="DNS:${DOMAIN}"
fi

# Создание конфигурации OpenSSL
cat > openssl.cnf <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=RU
ST=Moscow
L=Moscow
O=Test Certificate
CN=${DOMAIN}

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = ${SAN}
EOF

# Генерация приватного ключа
echo -e "${YELLOW}→ Генерация приватного ключа RSA 2048 бит...${NC}"
openssl genrsa -out privkey.pem 2048 2>/dev/null
chmod 600 privkey.pem
echo -e "${GREEN}✓ Приватный ключ сохранен: ${CERT_DIR}/privkey.pem${NC}"

# Генерация сертификата
echo -e "${YELLOW}→ Генерация самоподписанного сертификата...${NC}"
openssl req \
    -new \
    -x509 \
    -key privkey.pem \
    -out cert.pem \
    -days ${VALIDITY_DAYS} \
    -config openssl.cnf \
    -extensions v3_req \
    2>/dev/null

echo -e "${GREEN}✓ Сертификат сохранен: ${CERT_DIR}/cert.pem${NC}"

# Создание fullchain (копия cert для самоподписанного)
cp cert.pem fullchain.pem
echo -e "${GREEN}✓ Fullchain сохранен: ${CERT_DIR}/fullchain.pem${NC}"

# Создание пустого chain.pem
touch chain.pem
echo -e "${GREEN}✓ Chain файл создан: ${CERT_DIR}/chain.pem${NC}"

# Удаление временного файла конфигурации
rm -f openssl.cnf

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Информация о сертификате                                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# Вывод информации о сертификате
openssl x509 -in cert.pem -noout -subject -dates -ext subjectAltName

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Тестовый сертификат успешно создан                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📁 Файлы сертификата:${NC}"
echo -e "  • Приватный ключ: ${CERT_DIR}/privkey.pem"
echo -e "  • Сертификат: ${CERT_DIR}/cert.pem"
echo -e "  • Fullchain: ${CERT_DIR}/fullchain.pem"
echo -e "  • Chain: ${CERT_DIR}/chain.pem"
echo ""
echo -e "${YELLOW}⚠️  ВНИМАНИЕ:${NC}"
echo -e "  Это самоподписанный тестовый сертификат!"
echo -e "  Браузеры будут показывать предупреждение о безопасности."
echo -e "  Используйте ТОЛЬКО для тестирования и разработки!"
echo ""
echo -e "${YELLOW}Использование в Nginx:${NC}"
echo -e "  ssl_certificate ${CERT_DIR}/fullchain.pem;"
echo -e "  ssl_certificate_key ${CERT_DIR}/privkey.pem;"
echo ""

# Предложение загрузить в NPM
echo -e "${YELLOW}Загрузить в Nginx Proxy Manager?${NC}"
echo -e "  Используйте Python скрипт с опцией --test-cert"
echo -e "  или загрузите вручную через веб-интерфейс NPM"
echo ""
