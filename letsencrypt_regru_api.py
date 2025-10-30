#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для создания и обновления SSL сертификата Let's Encrypt
с использованием DNS-валидации через API reg.ru

Автор: Фофанов Дмитрий
Дата: 27.10.2025

Описание:
    Этот скрипт автоматизирует процесс получения и обновления SSL сертификатов
    Let's Encrypt для доменов, зарегистрированных на reg.ru, используя DNS-01 challenge.
    Скрипт напрямую работает с API reg.ru для управления DNS записями.

Требования:
    - Python 3.6+
    - requests
    - certbot
    - cryptography

Установка зависимостей:
    pip install requests certbot cryptography
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("ОШИБКА: Необходимо установить модуль 'requests'")
    print("Выполните: pip install requests")
    sys.exit(1)

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID, ExtensionOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("ОШИБКА: Необходимо установить модуль 'cryptography'")
    print("Выполните: pip install cryptography")
    sys.exit(1)

# ==============================================================================
# КОНФИГУРАЦИЯ
# ==============================================================================

# Настройки по умолчанию
DEFAULT_CONFIG = {
    # Учетные данные API reg.ru
    "regru_username": "your_username",
    "regru_password": "your_password",
    
    # Параметры домена
    "domain": "example.com",
    "wildcard": True,  # Создавать wildcard сертификат (*.domain.com)
    
    # Email для уведомлений Let's Encrypt
    "email": "admin@example.com",
    
    # Директории
    "cert_dir": "/etc/letsencrypt/live",
    "log_file": "/var/log/letsencrypt_regru.log",
    
    # Параметры DNS
    "dns_propagation_wait": 60,  # Время ожидания распространения DNS (секунды)
    "dns_check_attempts": 10,     # Количество попыток проверки DNS
    "dns_check_interval": 10,     # Интервал между проверками DNS (секунды)
    
    # Параметры обновления сертификата
    "renewal_days": 30,           # За сколько дней до истечения обновлять (по умолчанию 30)
    
    # Настройки Nginx Proxy Manager
    "npm_enabled": False,         # Включить интеграцию с NPM
    "npm_host": "http://10.10.10.14:81",  # Адрес NPM
    "npm_email": "admin@example.com",       # Email для входа в NPM
    "npm_password": "changeme",             # Пароль NPM
}

# API endpoints для reg.ru
REGRU_API_URL = "https://api.reg.ru/api/regru2"

# ==============================================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ==============================================================================

def setup_logging(log_file: str, verbose: bool = False) -> logging.Logger:
    """
    Настройка системы логирования
    
    Args:
        log_file: Путь к файлу лога
        verbose: Режим подробного вывода
        
    Returns:
        Logger объект
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Создаем директорию для логов, если не существует
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S'
    )
    
    # Создаем logger
    logger = logging.getLogger('LetsEncrypt_RegRU')
    logger.setLevel(log_level)
    
    # Обработчик для файла
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ==============================================================================
# КЛАСС ДЛЯ РАБОТЫ С API REG.RU
# ==============================================================================

class RegRuAPI:
    """Класс для работы с API reg.ru"""
    
    def __init__(self, username: str, password: str, logger: logging.Logger):
        """
        Инициализация API клиента
        
        Args:
            username: Имя пользователя reg.ru
            password: Пароль reg.ru
            logger: Logger объект
        """
        self.username = username
        self.password = password
        self.logger = logger
        self.session = requests.Session()
    
    def _make_request(self, method: str, params: Dict) -> Dict:
        """
        Выполнение запроса к API reg.ru
        
        Args:
            method: Название метода API
            params: Параметры запроса
            
        Returns:
            Ответ API в формате dict
        """
        url = f"{REGRU_API_URL}/{method}"
        
        # Добавляем учетные данные к параметрам
        params.update({
            "username": self.username,
            "password": self.password,
            "output_format": "json"
        })
        
        try:
            self.logger.debug(f"Отправка запроса к API: {method}")
            response = self.session.post(url, data=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("result") == "success":
                self.logger.debug(f"Запрос {method} выполнен успешно")
                return result
            else:
                error_msg = result.get("error_text", "Неизвестная ошибка")
                error_code = result.get("error_code", "unknown")
                
                # Обработка специфических ошибок
                if "Access to API from this IP denied" in error_msg or error_code == "IP_DENIED":
                    self.logger.error("=" * 80)
                    self.logger.error("🚫 ОШИБКА ДОСТУПА К API REG.RU")
                    self.logger.error("=" * 80)
                    self.logger.error("❌ Доступ к API заблокирован для текущего IP адреса")
                    self.logger.error("")
                    self.logger.error("🔧 РЕШЕНИЕ ПРОБЛЕМЫ:")
                    self.logger.error("1. Войдите в личный кабинет reg.ru")
                    self.logger.error("2. Перейдите в 'Настройки' → 'Безопасность' → 'API'")
                    self.logger.error("3. Добавьте текущий IP адрес в список разрешенных")
                    self.logger.error("4. Или отключите ограничение по IP (менее безопасно)")
                    self.logger.error("")
                    self.logger.error("🌐 Текущий IP можно узнать командой:")
                    self.logger.error("   curl -s https://ipinfo.io/ip")
                    self.logger.error("   или на сайте: https://whatismyipaddress.com/")
                    self.logger.error("")
                    self.logger.error("📚 Документация API: https://www.reg.ru/support/api")
                    self.logger.error("=" * 80)
                elif "Invalid username or password" in error_msg:
                    self.logger.error("=" * 80)
                    self.logger.error("🔐 ОШИБКА АУТЕНТИФИКАЦИИ")
                    self.logger.error("=" * 80)
                    self.logger.error("❌ Неверные учетные данные")
                    self.logger.error("🔧 Проверьте username и password в конфигурации")
                    self.logger.error("=" * 80)
                elif "IP exceeded allowed connection rate" in error_msg or error_code == "IP_EXCEEDED_ALLOWED_CONNECTION_RATE":
                    self.logger.error("=" * 80)
                    self.logger.error("⏱️  ОШИБКА: ПРЕВЫШЕН ЛИМИТ ЗАПРОСОВ К API")
                    self.logger.error("=" * 80)
                    self.logger.error("❌ IP адрес превысил допустимую частоту подключений к API reg.ru")
                    self.logger.error("")
                    self.logger.error("🔧 РЕШЕНИЕ ПРОБЛЕМЫ:")
                    self.logger.error("1. Подождите 5-10 минут перед следующей попыткой")
                    self.logger.error("2. Не запускайте скрипт слишком часто")
                    self.logger.error("3. Используйте --test-api только для диагностики")
                    self.logger.error("4. Настройте systemd timer для автоматических проверок (раз в день)")
                    self.logger.error("")
                    self.logger.error("📊 ЛИМИТЫ API REG.RU:")
                    self.logger.error("   • Обычно: не более 10-20 запросов в минуту с одного IP")
                    self.logger.error("   • Рекомендация: проверка сертификатов 1-2 раза в день")
                    self.logger.error("")
                    self.logger.error("⚙️  АВТОМАТИЗАЦИЯ:")
                    self.logger.error("   sudo systemctl enable letsencrypt-regru.timer")
                    self.logger.error("   sudo systemctl start letsencrypt-regru.timer")
                    self.logger.error("=" * 80)
                else:
                    self.logger.error(f"Ошибка API reg.ru: {error_msg} (код: {error_code})")
                
                raise Exception(f"API Error: {error_msg}")
                
        except requests.exceptions.Timeout:
            self.logger.error("Таймаут при обращении к API reg.ru (30 сек)")
            raise
        except requests.exceptions.ConnectionError:
            self.logger.error("Ошибка соединения с API reg.ru. Проверьте интернет подключение")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка HTTP запроса: {e}")
            raise
    
    def get_zone_records(self, domain: str) -> List[Dict]:
        """
        Получение DNS записей домена
        
        Args:
            domain: Доменное имя
            
        Returns:
            Список DNS записей
        """
        self.logger.info(f"Получение DNS записей для домена: {domain}")
        
        # Задержка перед запросом (защита от rate limit)
        import time
        time.sleep(1)
        
        params = {
            "domain_name": domain,
        }
        
        result = self._make_request("zone/get_resource_records", params)
        
        if "answer" in result and "records" in result["answer"]:
            records = result["answer"]["records"]
            self.logger.info(f"Получено {len(records)} DNS записей")
            return records
        else:
            self.logger.warning("DNS записи не найдены")
            return []
    
    def add_txt_record(self, domain: str, subdomain: str, txt_value: str) -> bool:
        """
        Добавление TXT записи для DNS валидации
        
        Args:
            domain: Основной домен
            subdomain: Поддомен (например, _acme-challenge)
            txt_value: Значение TXT записи
            
        Returns:
            True если успешно, False в противном случае
        """
        self.logger.info(f"Добавление TXT записи: {subdomain}.{domain} = {txt_value}")
        
        # Задержка перед запросом (защита от rate limit)
        import time
        time.sleep(2)
        
        params = {
            "domain_name": domain,
            "subdomain": subdomain,
            "text": txt_value,
            "output_content_type": "plain"
        }
        
        try:
            self._make_request("zone/add_txt", params)
            self.logger.info("TXT запись успешно добавлена")
            return True
        except Exception as e:
            self.logger.error(f"Не удалось добавить TXT запись: {e}")
            return False
    
    def get_current_ip(self) -> str:
        """
        Получение текущего публичного IP адреса
        
        Returns:
            IP адрес или 'Неизвестно'
        """
        try:
            response = requests.get("https://ipinfo.io/ip", timeout=10)
            if response.status_code == 200:
                return response.text.strip()
        except:
            try:
                response = requests.get("https://api.ipify.org", timeout=10)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                pass
        return "Неизвестно"
    
    def test_api_access(self) -> bool:
        """
        Проверка доступности API reg.ru
        
        Returns:
            True если API доступен
        """
        # Получаем текущий IP
        current_ip = self.get_current_ip()
        self.logger.info(f"Текущий IP адрес: {current_ip}")
        self.logger.info("Проверка доступности API reg.ru...")
        
        try:
            # Небольшая задержка перед запросом (защита от rate limit)
            import time
            time.sleep(1)
            
            # Простой запрос для проверки доступа
            params = {}
            result = self._make_request("user/get_balance", params)
            
            if result and result.get("result") == "success":
                balance = result.get("answer", {}).get("prepay", "Неизвестно")
                self.logger.info(f"✅ API reg.ru доступен. Баланс: {balance} руб.")
                return True
            else:
                self.logger.error("❌ API reg.ru недоступен")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Не удалось подключиться к API reg.ru: {e}")
            return False
    
    def remove_txt_record(self, domain: str, subdomain: str, txt_value: str) -> bool:
        """
        Удаление TXT записи
        
        Args:
            domain: Основной домен
            subdomain: Поддомен
            txt_value: Значение TXT записи
            
        Returns:
            True если успешно, False в противном случае
        """
        self.logger.info(f"Удаление TXT записи: {subdomain}.{domain}")
        
        try:
            # Сначала получаем список всех записей
            records = self.get_zone_records(domain)
            
            # Ищем нужную TXT запись
            record_id = None
            for record in records:
                if (record.get("rectype") == "TXT" and 
                    record.get("subdomain") == subdomain and 
                    record.get("text") == txt_value):
                    record_id = record.get("id")
                    break
            
            if not record_id:
                self.logger.warning("TXT запись для удаления не найдена")
                # Не считаем это критической ошибкой
                return True
            
            params = {
                "domain_name": domain,
                "record_id": record_id
            }
            
            self._make_request("zone/remove_record", params)
            self.logger.info("TXT запись успешно удалена")
            return True
            
        except Exception as e:
            self.logger.error(f"Не удалось удалить TXT запись: {e}")
            # Для cleanup hook не критично, если не удалось удалить
            self.logger.warning("Продолжаем выполнение, несмотря на ошибку удаления")
            return True


# ==============================================================================
# КЛАСС ДЛЯ РАБОТЫ С NGINX PROXY MANAGER
# ==============================================================================

class NginxProxyManagerAPI:
    """Класс для работы с API Nginx Proxy Manager"""
    
    def __init__(self, host: str, email: str, password: str, logger: logging.Logger):
        """
        Инициализация API клиента NPM
        
        Args:
            host: URL адрес NPM (например, http://10.10.10.14:81)
            email: Email для входа
            password: Пароль
            logger: Logger объект
        """
        self.host = host.rstrip('/')
        self.email = email
        self.password = password
        self.logger = logger
        self.session = requests.Session()
        self.token = None
    
    def login(self) -> bool:
        """
        Авторизация в Nginx Proxy Manager
        
        Returns:
            True если успешно
        """
        url = f"{self.host}/api/tokens"
        
        payload = {
            "identity": self.email,
            "secret": self.password
        }
        
        try:
            self.logger.info("Авторизация в Nginx Proxy Manager...")
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get("token")
            
            if self.token:
                # Устанавливаем токен в заголовки для последующих запросов
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                self.logger.info("Авторизация в NPM успешна")
                return True
            else:
                self.logger.error("Токен не получен при авторизации")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при авторизации в NPM: {e}")
            return False
    
    def get_certificates(self) -> List[Dict]:
        """
        Получение списка сертификатов
        
        Returns:
            Список сертификатов
        """
        url = f"{self.host}/api/nginx/certificates"
        
        try:
            self.logger.debug("Получение списка сертификатов из NPM...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            certificates = response.json()
            self.logger.debug(f"Получено {len(certificates)} сертификатов")
            return certificates
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при получении списка сертификатов: {e}")
            return []

    def get_certificate_by_id(self, cert_id: int) -> Optional[Dict]:
        """Возвращает данные сертификата по ID из NPM"""
        url = f"{self.host}/api/nginx/certificates/{cert_id}"
        try:
            self.logger.debug(f"Запрос сертификата ID={cert_id} из NPM...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Не удалось получить сертификат ID {cert_id}: {e}")
            return None

    def wait_for_certificate_parse(self, cert_id: int, timeout_seconds: int = 30, interval_seconds: float = 2.0) -> Optional[Dict]:
        """
        Ожидает, пока NPM распарсит загруженный сертификат и заполнит поля domain_names и expires_on.

        Возвращает актуальные данные сертификата или None по таймауту.
        """
        start = time.time()
        last: Optional[Dict] = None
        while time.time() - start < timeout_seconds:
            cert = self.get_certificate_by_id(cert_id)
            if cert:
                last = cert
                domains = cert.get('domain_names', []) or []
                created_on = cert.get('created_on')
                expires_on = cert.get('expires_on')
                self.logger.debug(f"Проверка парсинга NPM: domains={domains}, expires_on={expires_on}, created_on={created_on}")
                # Готово: домены определены и expires_on отличается от created_on
                if domains and expires_on and (not created_on or expires_on != created_on):
                    self.logger.info("NPM завершил парсинг сертификата")
                    return cert
            time.sleep(interval_seconds)
        return last
    
    def find_certificate_by_domain(self, domain: str) -> Optional[Dict]:
        """
        Поиск сертификата по домену
        
        Args:
            domain: Доменное имя
            
        Returns:
            Данные сертификата или None
        """
        certificates = self.get_certificates()
        
        self.logger.debug(f"Поиск сертификата для домена: {domain}")
        self.logger.debug(f"Всего сертификатов в NPM: {len(certificates)}")
        
        # Список доменов для поиска (основной домен и wildcard)
        search_domains = [domain, f"*.{domain}"]
        
        for cert in certificates:
            cert_id = cert.get("id")
            cert_name = cert.get("nice_name", "Unknown")
            domains = cert.get("domain_names", [])
            
            self.logger.debug(f"Проверка сертификата ID={cert_id}, name='{cert_name}', domains={domains}")
            
            # Проверяем точное совпадение доменов
            for search_domain in search_domains:
                if search_domain in domains:
                    self.logger.info(f"✅ Найден существующий сертификат для {domain}")
                    self.logger.info(f"   ID: {cert_id}, Домены: {', '.join(domains)}")
                    return cert
            
            # Если NPM ещё не распарсил домены (domains == []), проверяем по nice_name
            # Это предотвращает дублирование сертификатов при первичной загрузке
            if not domains:
                if cert_name.strip().lower() == domain.strip().lower() or cert_name.strip().lower() == f"*.{domain.strip().lower()}":
                    self.logger.info(f"✅ Найден сертификат по имени (домены ещё не распознаны NPM)")
                    self.logger.info(f"   ID: {cert_id}, Имя: {cert_name}")
                    return cert
        
        self.logger.debug(f"Сертификат для {domain} не найден")
        return None
    
    def upload_certificate(self, domain: str, cert_path: str, key_path: str, 
                          chain_path: Optional[str] = None) -> Optional[Dict]:
        """
        Загрузка нового сертификата в NPM
        
        ВАЖНО: NPM автоматически извлекает информацию из сертификата.
        Мы загружаем сертификат через веб-интерфейс формы (multipart/form-data),
        а не через JSON API, так как JSON endpoint имеет строгую валидацию схемы.
        
        Args:
            domain: Основной домен
            cert_path: Путь к файлу сертификата
            key_path: Путь к приватному ключу
            chain_path: Путь к цепочке сертификатов (опционально)
            
        Returns:
            Данные созданного сертификата или None
        """
        url = f"{self.host}/api/nginx/certificates"
        
        try:
            # Читаем приватный ключ
            with open(key_path, 'r') as f:
                certificate_key = f.read()
            
            # Определяем, какие файлы использовать
            cert_dir = os.path.dirname(cert_path)
            cert_only_path = os.path.join(cert_dir, "cert.pem")
            chain_only_path = os.path.join(cert_dir, "chain.pem")
            
            # Используем отдельные файлы cert.pem и chain.pem
            # NPM лучше работает с разделенными файлами
            if os.path.exists(cert_only_path) and os.path.exists(chain_only_path):
                self.logger.info("Загружаем cert.pem и chain.pem отдельно")
                with open(cert_only_path, 'rb') as f:
                    certificate = f.read().decode('utf-8')
                with open(chain_only_path, 'rb') as f:
                    intermediate_certificate = f.read().decode('utf-8')
                self.logger.info(f"Загружено: cert.pem ({len(certificate)} байт), chain.pem ({len(intermediate_certificate)} байт)")
            else:
                # Fallback: загружаем fullchain целиком
                self.logger.info("cert.pem/chain.pem не найдены, загружаем fullchain.pem")
                with open(cert_path, 'rb') as f:
                    certificate = f.read().decode('utf-8')
                intermediate_certificate = ""
                self.logger.info(f"Загружено: fullchain.pem ({len(certificate)} байт)")
            
            # Проверяем корректность сертификатов
            if not certificate.strip().startswith('-----BEGIN CERTIFICATE-----'):
                self.logger.error("Ошибка: Основной сертификат не начинается с BEGIN CERTIFICATE")
                return None
            
            if intermediate_certificate and not intermediate_certificate.strip().startswith('-----BEGIN CERTIFICATE-----'):
                self.logger.error("Ошибка: Промежуточный сертификат не начинается с BEGIN CERTIFICATE")
                return None
            
            # Показываем первые строки для диагностики
            self.logger.debug(f"Основной сертификат начинается с: {certificate[:60]}...")
            if intermediate_certificate:
                self.logger.debug(f"Промежуточный сертификат начинается с: {intermediate_certificate[:60]}...")
            
            # NPM Web UI использует multipart/form-data для загрузки custom сертификатов
            # Загружаем cert.pem и chain.pem отдельно
            files = {
                'certificate': ('cert.pem', certificate, 'application/x-pem-file'),
                'certificate_key': ('privkey.pem', certificate_key, 'application/x-pem-file'),
            }
            
            # Добавляем intermediate_certificate если есть
            if intermediate_certificate and intermediate_certificate.strip():
                files['intermediate_certificate'] = ('chain.pem', intermediate_certificate, 'application/x-pem-file')
                self.logger.info(f"Загружаем cert ({len(certificate)} байт) + chain ({len(intermediate_certificate)} байт) + privkey")
            else:
                self.logger.info(f"Загружаем cert ({len(certificate)} байт) + privkey (без chain)")
            
            # Дополнительные поля формы (только разрешенные NPM поля)
            data = {
                'nice_name': domain,
                'provider': 'other',  # other для custom сертификатов
            }
            
            self.logger.debug("NPM будет автоматически извлекать домены и дату истечения из сертификата")
            
            self.logger.debug(f"Uploading certificate as multipart/form-data")
            self.logger.debug(f"Files: {list(files.keys())}")
            self.logger.debug(f"Data: {data}")
            self.logger.info(f"Загрузка сертификата для {domain} в NPM...")
            
            # Отправляем как multipart/form-data
            response = self.session.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            cert_id = result.get("id")
            
            if cert_id:
                self.logger.info(f"Сертификат успешно загружен в NPM (ID: {cert_id})")
                
                # Показываем что вернул NPM
                self.logger.debug(f"Полный ответ NPM: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                expires = result.get("expires_on")
                if expires:
                    self.logger.info(f"NPM определил дату истечения: {expires}")
                else:
                    self.logger.warning("NPM не вернул дату истечения сертификата!")
                
                # Проверяем meta.letsencrypt_email - если есть, значит NPM считает это Let's Encrypt
                meta = result.get("meta", {})
                if meta:
                    self.logger.debug(f"NPM meta: {json.dumps(meta, indent=2, ensure_ascii=False)}")
                
                # После загрузки подождём, пока NPM распарсит сертификат (domain_names, expires_on)
                try:
                    parsed = self.wait_for_certificate_parse(cert_id, timeout_seconds=12, interval_seconds=1)
                    if parsed:
                        self.logger.info(
                            f"Итоговые данные NPM: домены={parsed.get('domain_names', [])}, истекает={parsed.get('expires_on')}"
                        )
                        return parsed
                except Exception as e:
                    self.logger.warning(f"Не удалось дождаться парсинга сертификата в NPM: {e}")
                
                return result
            else:
                self.logger.error("Не удалось получить ID созданного сертификата")
                self.logger.error(f"Ответ NPM: {result}")
                return None
                
        except FileNotFoundError as e:
            self.logger.error(f"Файл сертификата не найден: {e}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при загрузке сертификата в NPM: {e}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Ответ сервера: {e.response.text}")
            return None
    
    def update_certificate(self, cert_id: int, cert_path: str, key_path: str,
                          chain_path: Optional[str] = None) -> bool:
        """
        Обновление существующего сертификата
        
        Args:
            cert_id: ID сертификата в NPM
            cert_path: Путь к файлу сертификата
            key_path: Путь к приватному ключу
            chain_path: Путь к цепочке сертификатов (опционально)
            
        Returns:
            True если успешно
        """
        url = f"{self.host}/api/nginx/certificates/{cert_id}"
        
        try:
            # Читаем приватный ключ
            with open(key_path, 'r') as f:
                certificate_key = f.read()
            
            # Определяем, какие файлы использовать
            cert_dir = os.path.dirname(cert_path)
            cert_only_path = os.path.join(cert_dir, "cert.pem")
            chain_only_path = os.path.join(cert_dir, "chain.pem")
            
            # Используем cert.pem и chain.pem при обновлении, при отсутствии – fullchain
            files: Dict[str, Tuple[str, str, str]]
            if os.path.exists(cert_only_path) and os.path.exists(chain_only_path):
                self.logger.info("Обновление: используем cert.pem и chain.pem")
                with open(cert_only_path, 'rb') as f:
                    certificate = f.read().decode('utf-8')
                with open(chain_only_path, 'rb') as f:
                    intermediate_certificate = f.read().decode('utf-8')
                self.logger.debug(f"Загружено: cert.pem ({len(certificate)} байт), chain.pem ({len(intermediate_certificate)} байт)")
                files = {
                    'certificate': ('cert.pem', certificate, 'application/x-pem-file'),
                    'certificate_key': ('privkey.pem', certificate_key, 'application/x-pem-file'),
                    'intermediate_certificate': ('chain.pem', intermediate_certificate, 'application/x-pem-file'),
                }
            else:
                self.logger.info("Обновление: cert/chain не найдены, используем fullchain.pem")
                with open(cert_path, 'rb') as f:
                    certificate = f.read().decode('utf-8')
                self.logger.debug(f"Загружено: fullchain.pem ({len(certificate)} байт)")
                files = {
                    'certificate': ('fullchain.pem', certificate, 'application/x-pem-file'),
                    'certificate_key': ('privkey.pem', certificate_key, 'application/x-pem-file'),
                }
            
            # Дополнительные поля формы
            data = {
                'provider': 'other',  # other для custom сертификатов
            }
            
            self.logger.info(f"Обновление сертификата ID {cert_id} в NPM...")
            response = self.session.put(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            
            self.logger.info("Сертификат успешно обновлен в NPM")
            # Дождаться, пока NPM обновит метаданные
            try:
                parsed = self.wait_for_certificate_parse(cert_id, timeout_seconds=12, interval_seconds=1)
                if parsed:
                    self.logger.info(
                        f"Итоговые данные NPM после обновления: домены={parsed.get('domain_names', [])}, истекает={parsed.get('expires_on')}"
                    )
            except Exception as e:
                self.logger.warning(f"Не удалось дождаться обновления метаданных сертификата: {e}")
            return True
            
        except FileNotFoundError as e:
            self.logger.error(f"Файл сертификата не найден: {e}")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при обновлении сертификата в NPM: {e}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Ответ сервера: {e.response.text}")
            return False
    
    def delete_certificate(self, cert_id: int) -> bool:
        """
        Удаление сертификата из NPM
        
        Args:
            cert_id: ID сертификата в NPM
            
        Returns:
            True если успешно
        """
        url = f"{self.host}/api/nginx/certificates/{cert_id}"
        
        try:
            self.logger.info(f"Удаление сертификата ID {cert_id} из NPM...")
            response = self.session.delete(url, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"✅ Сертификат ID {cert_id} успешно удален из NPM")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при удалении сертификата: {e}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Ответ сервера: {e.response.text}")
            return False
    
    def sync_certificate(self, domain: str, cert_dir: str) -> bool:
        """
        Синхронизация сертификата с NPM (создание или обновление)
        
        Args:
            domain: Доменное имя
            cert_dir: Директория с сертификатами Let's Encrypt
            
        Returns:
            True если успешно
        """
        # Пути к файлам сертификата
        cert_path = os.path.join(cert_dir, "cert.pem")
        key_path = os.path.join(cert_dir, "privkey.pem")
        chain_path = os.path.join(cert_dir, "chain.pem")
        fullchain_path = os.path.join(cert_dir, "fullchain.pem")
        
        # Проверяем наличие файлов
        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            self.logger.error(f"Файлы сертификата не найдены в {cert_dir}")
            return False
        
        # Авторизуемся в NPM
        if not self.login():
            return False
        
        # Проверяем, существует ли уже сертификат для этого домена
        existing_cert = self.find_certificate_by_domain(domain)
        
        # Используем fullchain если доступен, иначе cert + chain
        if os.path.exists(fullchain_path):
            final_cert_path = fullchain_path
            final_chain_path = None
        else:
            final_cert_path = cert_path
            final_chain_path = chain_path if os.path.exists(chain_path) else None
        
        if existing_cert:
            # Обновляем существующий сертификат
            cert_id = existing_cert.get("id")
            self.logger.info(f"Обновление существующего сертификата (ID: {cert_id})")
            return self.update_certificate(cert_id, final_cert_path, key_path, final_chain_path)
        else:
            # Создаем новый сертификат
            self.logger.info("Создание нового сертификата в NPM")
            result = self.upload_certificate(domain, final_cert_path, key_path, final_chain_path)
            return result is not None


# ==============================================================================
# КЛАСС ДЛЯ ГЕНЕРАЦИИ ТЕСТОВЫХ СЕРТИФИКАТОВ
# ==============================================================================

class TestCertificateGenerator:
    """Класс для генерации самоподписанных тестовых SSL сертификатов"""
    
    def __init__(self, logger: logging.Logger):
        """
        Инициализация генератора тестовых сертификатов
        
        Args:
            logger: Logger объект
        """
        self.logger = logger
    
    def generate_self_signed_certificate(
        self,
        domain: str,
        wildcard: bool = False,
        output_dir: str = "/etc/letsencrypt/live",
        validity_days: int = 90
    ) -> bool:
        """
        Генерация самоподписанного SSL сертификата для тестирования
        
        Args:
            domain: Основной домен
            wildcard: Создать wildcard сертификат
            output_dir: Директория для сохранения сертификата
            validity_days: Срок действия сертификата в днях (по умолчанию 90)
            
        Returns:
            True если сертификат создан успешно, False в противном случае
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("ГЕНЕРАЦИЯ ТЕСТОВОГО САМОПОДПИСАННОГО СЕРТИФИКАТА")
            self.logger.info("=" * 80)
            self.logger.info(f"Домен: {domain}")
            self.logger.info(f"Wildcard: {wildcard}")
            self.logger.info(f"Срок действия: {validity_days} дней")
            self.logger.info("⚠️  ВНИМАНИЕ: Это тестовый сертификат, не для production!")
            
            # Создаем директорию для сертификата
            cert_dir = os.path.join(output_dir, domain)
            os.makedirs(cert_dir, exist_ok=True)
            self.logger.info(f"Директория: {cert_dir}")
            
            # Генерируем приватный ключ
            self.logger.info("Генерация приватного ключа RSA 2048 бит...")
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Сохраняем приватный ключ
            key_path = os.path.join(cert_dir, "privkey.pem")
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            os.chmod(key_path, 0o600)
            self.logger.info(f"✓ Приватный ключ сохранен: {key_path}")
            
            # Подготовка данных для сертификата
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Moscow"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Moscow"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Certificate"),
                x509.NameAttribute(NameOID.COMMON_NAME, domain),
            ])
            
            # Создаем список альтернативных имен (SAN)
            san_list = [x509.DNSName(domain)]
            if wildcard:
                san_list.append(x509.DNSName(f"*.{domain}"))
            
            # Генерируем сертификат
            self.logger.info("Генерация самоподписанного сертификата...")
            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(private_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
                .add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False,
                )
                .add_extension(
                    x509.BasicConstraints(ca=False, path_length=None),
                    critical=True,
                )
                .add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        key_encipherment=True,
                        content_commitment=False,
                        data_encipherment=False,
                        key_agreement=False,
                        key_cert_sign=False,
                        crl_sign=False,
                        encipher_only=False,
                        decipher_only=False,
                    ),
                    critical=True,
                )
                .add_extension(
                    x509.ExtendedKeyUsage([
                        x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                        x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                    ]),
                    critical=False,
                )
                .sign(private_key, hashes.SHA256(), default_backend())
            )
            
            # Сохраняем сертификат
            cert_path = os.path.join(cert_dir, "cert.pem")
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            self.logger.info(f"✓ Сертификат сохранен: {cert_path}")
            
            # Создаем fullchain (для самоподписанного это просто копия cert)
            fullchain_path = os.path.join(cert_dir, "fullchain.pem")
            with open(fullchain_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            self.logger.info(f"✓ Fullchain сохранен: {fullchain_path}")
            
            # Создаем chain.pem (пустой для самоподписанного)
            chain_path = os.path.join(cert_dir, "chain.pem")
            with open(chain_path, "w") as f:
                f.write("")
            self.logger.info(f"✓ Chain файл создан: {chain_path}")
            
            # Выводим информацию о сертификате
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("ИНФОРМАЦИЯ О СЕРТИФИКАТЕ")
            self.logger.info("=" * 80)
            self.logger.info(f"Домен: {domain}")
            if wildcard:
                self.logger.info(f"Wildcard: *.{domain}")
            self.logger.info(f"Действителен с: {cert.not_valid_before}")
            self.logger.info(f"Действителен до: {cert.not_valid_after}")
            self.logger.info(f"Серийный номер: {cert.serial_number}")
            self.logger.info("")
            self.logger.info("📁 Файлы сертификата:")
            self.logger.info(f"  • Приватный ключ: {key_path}")
            self.logger.info(f"  • Сертификат: {cert_path}")
            self.logger.info(f"  • Fullchain: {fullchain_path}")
            self.logger.info(f"  • Chain: {chain_path}")
            self.logger.info("")
            self.logger.info("⚠️  ВНИМАНИЕ:")
            self.logger.info("  Это самоподписанный тестовый сертификат!")
            self.logger.info("  Браузеры будут показывать предупреждение о безопасности.")
            self.logger.info("  Используйте ТОЛЬКО для тестирования и разработки!")
            self.logger.info("  Для production используйте настоящие Let's Encrypt сертификаты.")
            self.logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при генерации тестового сертификата: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False


# ==============================================================================
# КЛАСС ДЛЯ РАБОТЫ С CERTBOT
# ==============================================================================

class LetsEncryptManager:
    """Класс для управления сертификатами Let's Encrypt"""
    
    def __init__(self, config: Dict, api: RegRuAPI, logger: logging.Logger):
        """
        Инициализация менеджера сертификатов
        
        Args:
            config: Конфигурация
            api: API клиент reg.ru
            logger: Logger объект
        """
        self.config = config
        self.api = api
        self.logger = logger
        self.domain = config["domain"]
        self.email = config["email"]
        self.cert_dir = os.path.join(config["cert_dir"], self.domain)
    
    def check_certbot_installed(self) -> bool:
        """
        Проверка установки certbot
        
        Returns:
            True если certbot установлен
        """
        try:
            result = subprocess.run(
                ["certbot", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.debug(f"Certbot установлен: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("Certbot не установлен!")
            return False
    
    def check_certbot_running(self) -> bool:
        """
        Проверка наличия запущенных процессов certbot
        
        Returns:
            True если процесс certbot запущен
        """
        try:
            # Проверяем через ps
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            
            # Ищем процессы certbot (исключая текущий grep)
            certbot_processes = [
                line for line in result.stdout.split('\n')
                if 'certbot' in line.lower() and 'grep' not in line.lower()
                and str(os.getpid()) not in line  # Исключаем текущий процесс
            ]
            
            if certbot_processes:
                self.logger.warning("Обнаружены запущенные процессы Certbot:")
                for proc in certbot_processes:
                    self.logger.warning(f"  {proc}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Не удалось проверить запущенные процессы: {e}")
            return False
    
    def cleanup_certbot_locks(self) -> bool:
        """
        Очистка lock-файлов certbot
        
        Returns:
            True если lock-файлы были удалены или их не было
        """
        lock_files = [
            "/var/lib/letsencrypt/.certbot.lock",
            "/etc/letsencrypt/.certbot.lock",
        ]
        
        removed = False
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                    self.logger.info(f"Удалён lock-файл: {lock_file}")
                    removed = True
                except Exception as e:
                    self.logger.warning(f"Не удалось удалить lock-файл {lock_file}: {e}")
        
        if not removed:
            self.logger.debug("Lock-файлы certbot не найдены")
        
        return True
    
    def wait_for_certbot(self, timeout: int = 300) -> bool:
        """
        Ожидание завершения работы других процессов certbot
        
        Args:
            timeout: Максимальное время ожидания в секундах
            
        Returns:
            True если certbot больше не запущен
        """
        self.logger.info("Ожидание завершения других процессов Certbot...")
        
        start_time = time.time()
        check_interval = 5  # Проверяем каждые 5 секунд
        
        while time.time() - start_time < timeout:
            if not self.check_certbot_running():
                self.logger.info("Другие процессы Certbot завершены")
                return True
            
            elapsed = int(time.time() - start_time)
            self.logger.info(f"Ожидание... ({elapsed}/{timeout} секунд)")
            time.sleep(check_interval)
        
        self.logger.error(f"Превышено время ожидания ({timeout} секунд)")
        return False
    
    def is_staging_certificate(self) -> bool:
        """
        Проверка, является ли сертификат staging (тестовым)
        
        Returns:
            True если сертификат staging
        """
        cert_file = os.path.join(self.cert_dir, "cert.pem")
        
        if not os.path.exists(cert_file):
            return False
        
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            
            with open(cert_file, "rb") as f:
                cert_data = f.read()
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # Проверяем issuer (издателя сертификата)
            issuer = cert.issuer.rfc4514_string()
            
            # Staging сертификаты Let's Encrypt содержат "Fake LE" или "Staging" в issuer
            is_staging = (
                "fake" in issuer.lower() or 
                "staging" in issuer.lower() or
                "test" in issuer.lower()
            )
            
            return is_staging
            
        except Exception as e:
            self.logger.debug(f"Не удалось проверить тип сертификата: {e}")
            return False
    
    def check_certificate_expiry(self) -> Optional[int]:
        """
        Проверка срока действия сертификата
        
        Returns:
            Количество дней до истечения или None если сертификат не найден
        """
        cert_file = os.path.join(self.cert_dir, "cert.pem")
        
        if not os.path.exists(cert_file):
            self.logger.info("Сертификат не найден")
            return None
        
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            import warnings
            
            with open(cert_file, "rb") as f:
                cert_data = f.read()
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # Используем not_valid_after_utc для избежания предупреждения
            try:
                expiry_date = cert.not_valid_after_utc.replace(tzinfo=None)
            except AttributeError:
                # Для старых версий cryptography
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    expiry_date = cert.not_valid_after
            
            days_left = (expiry_date - datetime.now()).days
            
            self.logger.info(f"Сертификат истекает: {expiry_date.strftime('%d.%m.%Y %H:%M:%S')}")
            self.logger.info(f"Осталось дней: {days_left}")
            
            return days_left
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке сертификата: {e}")
            return None
    
    def dns_challenge_hook(self, validation_domain: str, validation_token: str) -> bool:
        """
        Обработчик DNS challenge - добавление TXT записи
        
        Args:
            validation_domain: Домен для валидации (например, dfv24.com или *.dfv24.com)
            validation_token: Токен валидации
            
        Returns:
            True если успешно
        """
        try:
            self.logger.info("=== DNS Challenge: Добавление TXT записи ===")
            
            # Извлекаем основной домен из validation_domain
            # Убираем wildcard если есть
            base_domain = validation_domain.replace("*.", "")
            
            # Для DNS-01 challenge всегда используем _acme-challenge
            subdomain = "_acme-challenge"
            
            self.logger.info(f"Validation Domain: {validation_domain}")
            self.logger.info(f"Base Domain: {base_domain}")
            self.logger.info(f"Subdomain: {subdomain}")
            self.logger.info(f"Token: {validation_token[:20]}...")
            
            # Добавляем TXT запись
            self.logger.info("Добавление TXT записи через API reg.ru...")
            success = self.api.add_txt_record(base_domain, subdomain, validation_token)
            
            if not success:
                self.logger.error("Не удалось добавить TXT запись")
                return False
            
            self.logger.info("✅ TXT запись успешно добавлена в API reg.ru")
            
            # Ждем распространения DNS
            wait_time = self.config.get("dns_propagation_wait", 60)
            self.logger.info("")
            self.logger.info("⏳ Ожидание распространения DNS...")
            self.logger.info(f"   Время ожидания: {wait_time} секунд")
            self.logger.info(f"   TXT запись: _acme-challenge.{base_domain}")
            self.logger.info("")
            
            # Показываем прогресс ожидания
            for i in range(wait_time):
                if i % 10 == 0:
                    elapsed_pct = int((i / wait_time) * 100)
                    self.logger.info(f"   ⏱️  Прошло: {i}/{wait_time} сек ({elapsed_pct}%)")
                time.sleep(1)
            
            self.logger.info(f"   ✅ Ожидание завершено ({wait_time} секунд)")
            self.logger.info("")
            
            # Проверяем DNS запись (используем base_domain для проверки)
            self.logger.info("🔍 Проверка распространения DNS через публичные серверы...")
            if self.verify_dns_record_external(base_domain, subdomain, validation_token):
                self.logger.info("✅ DNS запись подтверждена через публичные DNS серверы")
                self.logger.info("   Certbot сможет пройти валидацию")
                return True
            else:
                self.logger.warning("⚠️  DNS запись НЕ обнаружена через публичные DNS, но продолжаем...")
                self.logger.warning("   Возможные причины:")
                self.logger.warning("   • DNS серверы ещё не обновились (требуется больше времени)")
                self.logger.warning("   • Let's Encrypt использует свои DNS серверы")
                self.logger.warning("   • API reg.ru обновляет записи с задержкой")
                self.logger.warning("")
                self.logger.warning("   Certbot будет продолжать попытки валидации...")
                return True
                
        except Exception as e:
            self.logger.error(f"💥 Ошибка в dns_challenge_hook: {e}")
            self.logger.exception("Traceback:")
            return False
    
    def dns_cleanup_hook(self, validation_domain: str, validation_token: str) -> bool:
        """
        Обработчик очистки DNS challenge - удаление TXT записи
        
        Args:
            validation_domain: Домен валидации (например, dfv24.com или *.dfv24.com)
            validation_token: Токен валидации
            
        Returns:
            True если успешно
        """
        self.logger.info("=== DNS Challenge: Удаление TXT записи ===")
        
        # Извлекаем основной домен
        base_domain = validation_domain.replace("*.", "")
        subdomain = "_acme-challenge"
        
        self.logger.info(f"Домен: {base_domain}, Поддомен: {subdomain}")
        
        return self.api.remove_txt_record(base_domain, subdomain, validation_token)
    
    def verify_dns_record_external(self, domain: str, subdomain: str, expected_value: str) -> bool:
        """
        Проверка наличия DNS записи через внешний DNS
        
        Args:
            domain: Основной домен
            subdomain: Поддомен
            expected_value: Ожидаемое значение TXT записи
            
        Returns:
            True если запись найдена
        """
        import time
        
        full_domain = f"{subdomain}.{domain}"
        attempts = self.config.get("dns_check_attempts", 10)
        interval = self.config.get("dns_check_interval", 10)
        
        self.logger.info(f"   Проверяем: {full_domain}")
        self.logger.info(f"   Ожидаемое значение: {expected_value[:30]}...")
        self.logger.info(f"   Попыток: {attempts}, интервал: {interval} сек")
        self.logger.info("")
        
        for attempt in range(attempts):
            try:
                # Используем nslookup или dig через subprocess
                result = subprocess.run(
                    ["nslookup", "-type=TXT", full_domain],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if expected_value in result.stdout:
                    self.logger.info(f"   ✅ Попытка {attempt + 1}/{attempts}: DNS запись НАЙДЕНА!")
                    # Показываем найденную запись
                    for line in result.stdout.split('\n'):
                        if 'text =' in line.lower() or expected_value[:20] in line:
                            self.logger.info(f"      {line.strip()}")
                    return True
                else:
                    self.logger.info(f"   ⏳ Попытка {attempt + 1}/{attempts}: DNS запись не найдена, ждём...")
                    
            except Exception as e:
                self.logger.info(f"   ⚠️  Попытка {attempt + 1}/{attempts}: Ошибка nslookup - {e}")
            
            if attempt < attempts - 1:
                time.sleep(interval)
        
        self.logger.warning(f"   ❌ DNS запись не найдена после {attempts} попыток")
        return False
    
    def verify_dns_record(self, subdomain: str, expected_value: str) -> bool:
        """
        Проверка наличия DNS записи (использует self.domain)
        
        Args:
            subdomain: Поддомен
            expected_value: Ожидаемое значение TXT записи
            
        Returns:
            True если запись найдена
        """
        return self.verify_dns_record_external(self.domain, subdomain, expected_value)
    
    def obtain_certificate(self, staging: bool = False) -> bool:
        """
        Получение нового сертификата
        
        Args:
            staging: Использовать staging окружение Let's Encrypt (для тестирования)
        
        Returns:
            True если успешно
        """
        if staging:
            self.logger.info("=== Запрос ТЕСТОВОГО SSL сертификата (Let's Encrypt Staging) ===")
            self.logger.warning("⚠️  ВНИМАНИЕ: Это тестовый сертификат из staging окружения!")
            self.logger.warning("⚠️  Браузеры не будут доверять этому сертификату")
            self.logger.warning("⚠️  Используйте для тестирования DNS и автоматизации")
            self.logger.warning("⚠️  Staging НЕ имеет лимитов запросов (в отличие от production)")
        else:
            self.logger.info("=== Запрос нового SSL сертификата ===")
        
        # Проверяем, не запущен ли уже certbot
        if self.check_certbot_running():
            self.logger.warning("Обнаружен запущенный процесс Certbot")
            self.logger.info("Варианты решения:")
            self.logger.info("  1. Дождитесь завершения текущего процесса")
            self.logger.info("  2. Остановите процесс вручную: sudo pkill certbot")
            self.logger.info("  3. Используйте --force-cleanup для очистки lock-файлов")
            
            # Пытаемся подождать
            if not self.wait_for_certbot(timeout=60):
                self.logger.error("Не удалось дождаться завершения Certbot")
                self.logger.info("Попытка очистки lock-файлов...")
                self.cleanup_certbot_locks()
                
                # Проверяем снова
                if self.check_certbot_running():
                    self.logger.error("Certbot всё ещё запущен. Требуется ручное вмешательство.")
                    self.logger.error("Выполните: sudo pkill -9 certbot")
                    return False
        
        # Формируем список доменов
        domains = [self.domain]
        if self.config.get("wildcard", False):
            domains.append(f"*.{self.domain}")
        
        domain_args = []
        for d in domains:
            domain_args.extend(["-d", d])
        
        # Создаём временные wrapper скрипты для hooks
        import tempfile
        
        # Получаем путь к конфигурации из аргументов командной строки
        config_path = None
        for i, arg in enumerate(sys.argv):
            if arg in ['-c', '--config'] and i + 1 < len(sys.argv):
                config_path = os.path.abspath(sys.argv[i + 1])
                break
        
        if not config_path:
            self.logger.error("Не указан путь к конфигурации. Используйте --config /path/to/config.json")
            return False
        
        # Auth hook wrapper
        auth_hook_script = tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False)
        auth_hook_script.write('#!/bin/bash\n')
        auth_hook_script.write(f'{sys.executable} {os.path.abspath(__file__)} --config {config_path} --auth-hook\n')
        auth_hook_script.close()
        os.chmod(auth_hook_script.name, 0o755)
        
        # Cleanup hook wrapper
        cleanup_hook_script = tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False)
        cleanup_hook_script.write('#!/bin/bash\n')
        cleanup_hook_script.write(f'{sys.executable} {os.path.abspath(__file__)} --config {config_path} --cleanup-hook\n')
        cleanup_hook_script.close()
        os.chmod(cleanup_hook_script.name, 0o755)
        
        # Команда certbot
        cmd = [
            "certbot", "certonly",
            "--manual",
            "--preferred-challenges", "dns",
            "--manual-auth-hook", auth_hook_script.name,
            "--manual-cleanup-hook", cleanup_hook_script.name,
            "--email", self.email,
            "--agree-tos",
            "--non-interactive",
            "--expand",
        ]
        
        # Добавляем --staging для тестового окружения
        if staging:
            cmd.append("--staging")
            cmd.append("--break-my-certs")  # Разрешает перезапись production сертификатов staging версиями
        
        cmd.extend(domain_args)
        
        self.logger.info("=" * 80)
        if staging:
            self.logger.info("ЗАПУСК CERTBOT (STAGING MODE)")
        else:
            self.logger.info("ЗАПУСК CERTBOT")
        self.logger.info("=" * 80)
        self.logger.info(f"Режим: {'STAGING (тестовый)' if staging else 'PRODUCTION (боевой)'}")
        self.logger.info(f"Команда: {' '.join(cmd)}")
        self.logger.info(f"Python: {sys.executable}")
        self.logger.info(f"Скрипт: {os.path.abspath(__file__)}")
        self.logger.info(f"Конфигурация: {config_path}")
        self.logger.info(f"Auth hook: {sys.executable} {os.path.abspath(__file__)} --config {config_path} --auth-hook")
        self.logger.info(f"Cleanup hook: {sys.executable} {os.path.abspath(__file__)} --config {config_path} --cleanup-hook")
        self.logger.info("=" * 80)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info("=" * 80)
            self.logger.info("✅ СЕРТИФИКАТ УСПЕШНО ПОЛУЧЕН!")
            self.logger.info("=" * 80)
            
            # Выводим stdout certbot (может содержать полезную информацию)
            if result.stdout:
                self.logger.info("Вывод Certbot:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.logger.info(f"  {line}")
            
            # Информация о местоположении сертификата
            if staging:
                self.logger.info("")
                self.logger.info("⚠️  Это STAGING сертификат - не используйте на production!")
                self.logger.info("   Для получения production сертификата используйте: letsencrypt-regru --obtain")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error("=" * 80)
            self.logger.error("❌ ОШИБКА ПРИ ПОЛУЧЕНИИ СЕРТИФИКАТА")
            self.logger.error("=" * 80)
            self.logger.error(f"Код возврата: {e.returncode}")
            
            # Выводим stderr (основные ошибки)
            if e.stderr:
                self.logger.error("")
                self.logger.error("Сообщения об ошибках:")
                for line in e.stderr.split('\n'):
                    if line.strip():
                        self.logger.error(f"  {line}")
            
            # Выводим stdout (может содержать дополнительную информацию)
            if e.stdout:
                self.logger.error("")
                self.logger.error("Дополнительная информация:")
                for line in e.stdout.split('\n'):
                    if line.strip():
                        self.logger.error(f"  {line}")
            
            # Рекомендации по устранению проблем
            self.logger.error("")
            self.logger.error("=" * 80)
            self.logger.error("РЕКОМЕНДАЦИИ ПО УСТРАНЕНИЮ ПРОБЛЕМ:")
            self.logger.error("=" * 80)
            self.logger.error("1. Проверьте детальный лог Certbot:")
            self.logger.error("   tail -100 /var/log/letsencrypt/letsencrypt.log")
            self.logger.error("")
            self.logger.error("2. Проверьте логи скрипта:")
            self.logger.error("   tail -100 /var/log/letsencrypt-regru/letsencrypt_regru.log")
            self.logger.error("")
            self.logger.error("3. Убедитесь, что DNS записи создаются:")
            self.logger.error("   letsencrypt-regru --test-dns")
            self.logger.error("")
            self.logger.error("4. Проверьте доступ к API reg.ru:")
            self.logger.error("   letsencrypt-regru --test-api")
            self.logger.error("")
            self.logger.error("5. Запустите с подробным выводом:")
            self.logger.error("   letsencrypt-regru --staging -v")
            self.logger.error("")
            self.logger.error("6. Убедитесь что ваш IP в белом списке API reg.ru:")
            self.logger.error("   https://www.reg.ru/user/account/#/settings/api/")
            self.logger.error("")
            self.logger.error("7. Проверьте DNS записи вручную:")
            self.logger.error("   nslookup -type=TXT _acme-challenge.{domain}")
            self.logger.error("   dig TXT _acme-challenge.{domain}")
            self.logger.error("=" * 80)
            
            return False
        finally:
            # Удаляем временные wrapper скрипты
            try:
                os.unlink(auth_hook_script.name)
                os.unlink(cleanup_hook_script.name)
            except:
                pass
    
    def renew_certificate(self) -> bool:
        """
        Обновление существующего сертификата
        
        Returns:
            True если успешно
        """
        self.logger.info("=== Обновление SSL сертификата ===")
        
        cmd = [
            "certbot", "renew",
            "--manual",
            "--manual-auth-hook", f"{sys.executable} {os.path.abspath(__file__)} --auth-hook",
            "--manual-cleanup-hook", f"{sys.executable} {os.path.abspath(__file__)} --cleanup-hook",
            "--non-interactive",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info("Проверка обновления завершена")
            self.logger.debug(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Ошибка при обновлении: {e}")
            self.logger.error(e.stderr)
            return False
    
    def display_certificate_info(self):
        """Вывод информации о сертификате"""
        cert_file = os.path.join(self.cert_dir, "cert.pem")
        
        if not os.path.exists(cert_file):
            self.logger.warning("Сертификат не найден")
            return
        
        self.logger.info("=" * 60)
        self.logger.info("ИНФОРМАЦИЯ О СЕРТИФИКАТЕ")
        self.logger.info("=" * 60)
        
        try:
            result = subprocess.run(
                ["openssl", "x509", "-in", cert_file, "-text", "-noout"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Проверяем, является ли сертификат staging
            is_staging = "fake" in result.stdout.lower() or "staging" in result.stdout.lower()
            
            if is_staging:
                self.logger.warning("⚠️  ЭТО STAGING (ТЕСТОВЫЙ) СЕРТИФИКАТ!")
                self.logger.warning("   Браузеры не будут доверять этому сертификату")
                self.logger.warning("   Не используйте на production сайтах")
                self.logger.warning("")
            
            # Выводим только основную информацию
            for line in result.stdout.split("\n"):
                if any(keyword in line for keyword in ["Subject:", "Issuer:", "Not Before", "Not After", "DNS:"]):
                    self.logger.info(line.strip())
            
            self.logger.info("=" * 60)
            self.logger.info("ПУТИ К ФАЙЛАМ СЕРТИФИКАТА:")
            self.logger.info(f"  Сертификат: {self.cert_dir}/cert.pem")
            self.logger.info(f"  Приватный ключ: {self.cert_dir}/privkey.pem")
            self.logger.info(f"  Цепочка: {self.cert_dir}/chain.pem")
            self.logger.info(f"  Полная цепочка: {self.cert_dir}/fullchain.pem")
            
            if is_staging:
                self.logger.info("")
                self.logger.info("🚀 Для получения PRODUCTION сертификата выполните:")
                self.logger.info("   sudo letsencrypt-regru --obtain")
            
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"Ошибка при чтении сертификата: {e}")
    
    def sync_with_npm(self, npm_api: NginxProxyManagerAPI) -> bool:
        """
        Синхронизация сертификата с Nginx Proxy Manager
        
        Args:
            npm_api: API клиент NPM
            
        Returns:
            True если успешно
        """
        self.logger.info("=== Синхронизация сертификата с Nginx Proxy Manager ===")
        
        # Проверяем наличие сертификата
        if not os.path.exists(self.cert_dir):
            self.logger.error(f"Директория сертификата не найдена: {self.cert_dir}")
            return False
        
        # Синхронизируем сертификат
        return npm_api.sync_certificate(self.domain, self.cert_dir)


# ==============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==============================================================================

def reload_webserver(logger: logging.Logger):
    """
    Перезагрузка веб-сервера
    
    Args:
        logger: Logger объект
    """
    logger.info("Перезагрузка веб-сервера...")
    
    # Проверяем какие сервисы активны
    services = ["nginx", "apache2", "httpd"]
    
    for service in services:
        try:
            # Проверяем статус
            result = subprocess.run(
                ["systemctl", "is-active", service],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip() == "active":
                # Перезагружаем
                subprocess.run(
                    ["systemctl", "reload", service],
                    check=True
                )
                logger.info(f"Сервис {service} перезагружен")
                return
                
        except Exception as e:
            logger.debug(f"Сервис {service} не активен или ошибка: {e}")
    
    logger.warning("Активный веб-сервер не найден")


def load_config(config_file: Optional[str] = None) -> Dict:
    """
    Загрузка конфигурации из файла или использование значений по умолчанию
    
    Args:
        config_file: Путь к файлу конфигурации (JSON)
        
    Returns:
        Словарь с конфигурацией
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception as e:
            print(f"ОШИБКА: Не удалось загрузить конфигурацию из {config_file}: {e}")
            sys.exit(1)
    
    return config


def create_sample_config(output_file: str):
    """
    Создание примера файла конфигурации
    
    Args:
        output_file: Путь к выходному файлу
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
    
    print(f"Пример конфигурации создан: {output_file}")
    print("Отредактируйте файл и укажите ваши учетные данные")


# ==============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==============================================================================

def main():
    """Основная функция скрипта"""
    
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(
        description="Автоматическое управление SSL сертификатами Let's Encrypt через API reg.ru",
        epilog="""
================================================================================
ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
================================================================================

Основные команды:
  letsencrypt-regru --check              Проверить срок действия (определяет staging/production)
  letsencrypt-regru --info               Показать полную информацию о сертификате
  letsencrypt-regru --obtain             Получить production сертификат
  letsencrypt-regru --renew              Обновить сертификат
  letsencrypt-regru --auto               Авто-режим (для cron/systemd)
  letsencrypt-regru --upload-npm DOMAIN  Загрузить сертификат в Nginx Proxy Manager
  letsencrypt-regru --list-npm           Показать все сертификаты в NPM (с дубликатами)
  letsencrypt-regru --delete-npm ID      Удалить сертификат из NPM по ID

Команды тестирования:
  letsencrypt-regru --staging            Тестовый Let's Encrypt (БЕЗ лимитов!)
  letsencrypt-regru --test-cert          Самоподписанный (локально)
  letsencrypt-regru --test-api           Проверить API reg.ru
  letsencrypt-regru --test-dns           Проверить DNS записи

Отладка:
  letsencrypt-regru --obtain -v          Подробный вывод
  letsencrypt-regru --force-cleanup      Очистить lock-файлы Certbot

Работа с NPM:
  letsencrypt-regru --list-npm                    Показать все сертификаты
  letsencrypt-regru --upload-npm example.com      Загрузить сертификат для example.com
  letsencrypt-regru --delete-npm 5                Удалить сертификат ID 5

================================================================================
РЕКОМЕНДУЕМЫЙ WORKFLOW
================================================================================

1. Проверка настройки:
   letsencrypt-regru --test-api          [+] API доступен?
   letsencrypt-regru --test-dns          [+] DNS работает?

2. Тестирование (неограниченно):
   letsencrypt-regru --staging           [+] Полный процесс SSL

3. Production:
   letsencrypt-regru --obtain            [+] Боевой сертификат
   letsencrypt-regru --upload-npm DOMAIN [+] Загрузить в NPM (если не автоматически)

================================================================================
СРАВНЕНИЕ РЕЖИМОВ ТЕСТИРОВАНИЯ
================================================================================

  --staging         Полный Let's Encrypt, БЕЗ лимитов, ~2-3 мин, тестирует все
  --test-cert       Самоподпись, мгновенно, БЕЗ интернета, для локальной разработки
  --test-dns        Только DNS, ~1-2 мин, не создает сертификат

================================================================================
ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ
================================================================================

Документация:  https://github.com/DFofanov/configure_nginx_manager
Поддержка:     https://github.com/DFofanov/configure_nginx_manager/issues
Лимиты LE:     5 сертификатов/неделю на домен (production only, staging БЕЗ лимитов)

        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c", "--config",
        help="Путь к файлу конфигурации (JSON)",
        default=None
    )
    parser.add_argument(
        "--create-config",
        help="Создать пример файла конфигурации",
        metavar="FILE"
    )
    # Основные команды
    main_group = parser.add_argument_group('Основные команды')
    main_group.add_argument(
        "--check",
        help="Проверить срок действия сертификата (определяет staging/production)",
        action="store_true"
    )
    main_group.add_argument(
        "--info",
        help="Показать полную информацию о сертификате",
        action="store_true"
    )
    main_group.add_argument(
        "--obtain",
        help="Получить новый production сертификат Let's Encrypt",
        action="store_true"
    )
    main_group.add_argument(
        "--renew",
        help="Обновить существующий сертификат",
        action="store_true"
    )
    main_group.add_argument(
        "--auto",
        help="Автоматический режим: проверка и обновление при необходимости (для cron/systemd)",
        action="store_true"
    )
    main_group.add_argument(
        "--upload-npm",
        help="Загрузить существующий сертификат в Nginx Proxy Manager",
        metavar="DOMAIN",
        type=str
    )
    main_group.add_argument(
        "--list-npm",
        help="Показать все сертификаты в Nginx Proxy Manager",
        action="store_true"
    )
    main_group.add_argument(
        "--delete-npm",
        help="Удалить сертификат из Nginx Proxy Manager по ID",
        metavar="CERT_ID",
        type=int
    )
    
    # Команды тестирования
    test_group = parser.add_argument_group('Команды тестирования')
    test_group.add_argument(
        "--staging",
        help="Получить тестовый сертификат Let's Encrypt (staging CA, БЕЗ лимитов)",
        action="store_true"
    )
    test_group.add_argument(
        "--test-cert",
        help="Создать самоподписанный сертификат (локальная разработка, БЕЗ интернета)",
        action="store_true"
    )
    test_group.add_argument(
        "--test-api",
        help="Проверить доступ к API reg.ru (показывает IP, баланс)",
        action="store_true"
    )
    test_group.add_argument(
        "--test-dns",
        help="Протестировать создание/удаление DNS записи (полная симуляция SSL процесса)",
        action="store_true"
    )
    
    # Служебные команды
    service_group = parser.add_argument_group('Служебные команды (внутреннее использование)')
    service_group.add_argument(
        "--auth-hook",
        help="Certbot authentication hook (создание DNS записи)",
        action="store_true"
    )
    service_group.add_argument(
        "--cleanup-hook",
        help="Certbot cleanup hook (удаление DNS записи)",
        action="store_true"
    )
    
    # Дополнительные параметры
    parser.add_argument(
        "-v", "--verbose",
        help="Подробный вывод для диагностики",
        action="store_true"
    )
    parser.add_argument(
        "--force-cleanup",
        help="Принудительная очистка lock-файлов Certbot (если процесс завис)",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Создание примера конфигурации
    if args.create_config:
        create_sample_config(args.create_config)
        return 0
    
    # Принудительная очистка lock-файлов
    if args.force_cleanup:
        print("=" * 80)
        print("ПРИНУДИТЕЛЬНАЯ ОЧИСТКА LOCK-ФАЙЛОВ CERTBOT")
        print("=" * 80)
        
        lock_files = [
            "/var/lib/letsencrypt/.certbot.lock",
            "/etc/letsencrypt/.certbot.lock",
        ]
        
        # Проверяем запущенные процессы
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            certbot_processes = [
                line for line in result.stdout.split('\n')
                if 'certbot' in line.lower() and 'grep' not in line.lower()
            ]
            
            if certbot_processes:
                print("\n⚠️  ПРЕДУПРЕЖДЕНИЕ: Обнаружены запущенные процессы Certbot:")
                for proc in certbot_processes:
                    print(f"  {proc}")
                print("\nРекомендуется сначала остановить процессы:")
                print("  sudo pkill certbot")
                print("\nПродолжить очистку lock-файлов? (y/N): ", end='')
                
                response = input().strip().lower()
                if response != 'y':
                    print("Отменено.")
                    return 0
        except Exception as e:
            print(f"Не удалось проверить процессы: {e}")
        
        # Удаляем lock-файлы
        removed_count = 0
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                    print(f"✅ Удалён: {lock_file}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Ошибка при удалении {lock_file}: {e}")
            else:
                print(f"ℹ️  Не найден: {lock_file}")
        
        print("\n" + "=" * 80)
        if removed_count > 0:
            print(f"✅ Удалено lock-файлов: {removed_count}")
            print("Теперь можно попробовать запустить Certbot снова.")
        else:
            print("ℹ️  Lock-файлы не найдены.")
        print("=" * 80)
        return 0
    
    # Загрузка конфигурации
    config = load_config(args.config)
    
    # Настройка логирования
    logger = setup_logging(config["log_file"], args.verbose)
    
    # Тестирование DNS записей (полный цикл как при создании SSL)
    if args.test_dns:
        logger.info("=" * 80)
        logger.info("ТЕСТИРОВАНИЕ СОЗДАНИЯ DNS ЗАПИСИ ДЛЯ SSL")
        logger.info("=" * 80)
        logger.info("Этот тест симулирует процесс создания SSL сертификата:")
        logger.info("1. Проверка подключения к API")
        logger.info("2. Создание TXT записи _acme-challenge")
        logger.info("3. Проверка распространения DNS")
        logger.info("4. Удаление тестовой записи")
        logger.info("=" * 80)
        logger.info("")
        
        api = RegRuAPI(config["regru_username"], config["regru_password"], logger)
        domain = config["domain"]
        test_subdomain = "_acme-challenge"
        test_value = f"test-value-{int(time.time())}"
        
        all_passed = True
        
        # Шаг 1: Проверка API
        logger.info("📋 ШАГ 1/4: Проверка подключения к API reg.ru")
        if not api.test_api_access():
            logger.error("❌ API недоступен. Тест прерван.")
            return 1
        logger.info("✅ API доступен")
        logger.info("")
        
        # Шаг 2: Создание TXT записи
        logger.info("📋 ШАГ 2/4: Создание тестовой TXT записи")
        logger.info(f"   Домен: {domain}")
        logger.info(f"   Поддомен: {test_subdomain}")
        logger.info(f"   Значение: {test_value}")
        
        if api.add_txt_record(domain, test_subdomain, test_value):
            logger.info("✅ TXT запись создана успешно")
        else:
            logger.error("❌ Не удалось создать TXT запись")
            all_passed = False
        logger.info("")
        
        if all_passed:
            # Шаг 3: Ожидание распространения DNS
            logger.info("📋 ШАГ 3/4: Ожидание распространения DNS")
            wait_time = config.get("dns_propagation_wait", 60)
            logger.info(f"   Ожидаем {wait_time} секунд...")
            
            for i in range(wait_time):
                if i % 10 == 0:
                    logger.info(f"   ⏳ Прошло {i}/{wait_time} секунд")
                time.sleep(1)
            
            logger.info("✅ Ожидание завершено")
            logger.info("")
            
            # Проверка DNS через nslookup
            logger.info("📋 ШАГ 3.5/4: Проверка DNS записи через nslookup")
            full_domain = f"{test_subdomain}.{domain}"
            try:
                result = subprocess.run(
                    ["nslookup", "-type=TXT", full_domain],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if test_value in result.stdout:
                    logger.info(f"✅ DNS запись найдена для {full_domain}")
                    logger.info("   Вывод nslookup:")
                    for line in result.stdout.split("\n"):
                        if test_value in line or "text =" in line.lower():
                            logger.info(f"   {line.strip()}")
                else:
                    logger.warning(f"⚠️  DNS запись НЕ найдена для {full_domain}")
                    logger.warning("   Это может быть нормально, если DNS ещё не распространился")
                    logger.warning("   Certbot будет ждать дольше при реальном создании сертификата")
            except Exception as e:
                logger.warning(f"⚠️  Не удалось проверить DNS: {e}")
            
            logger.info("")
        
        # Шаг 4: Удаление тестовой записи
        logger.info("📋 ШАГ 4/4: Удаление тестовой записи")
        if api.remove_txt_record(domain, test_subdomain, test_value):
            logger.info("✅ TXT запись удалена успешно")
        else:
            logger.warning("⚠️  Не удалось удалить TXT запись (возможно уже удалена)")
        
        logger.info("")
        logger.info("=" * 80)
        if all_passed:
            logger.info("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО")
            logger.info("=" * 80)
            logger.info("")
            logger.info("🎉 Система готова для создания SSL сертификата!")
            logger.info("")
            logger.info("Следующие шаги:")
            logger.info("1. Убедитесь что ваш IP добавлен в белый список API reg.ru")
            logger.info("2. Запустите: sudo letsencrypt-regru --obtain")
            logger.info("3. Или настройте автоматическое обновление:")
            logger.info("   sudo systemctl enable letsencrypt-regru.timer")
            logger.info("   sudo systemctl start letsencrypt-regru.timer")
            return 0
        else:
            logger.error("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
            logger.error("=" * 80)
            logger.error("Исправьте проблемы перед созданием SSL сертификата")
            return 1
    
    # Тестирование API
    if args.test_api:
        logger.info("=" * 80)
        logger.info("ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ К API REG.RU")
        logger.info("=" * 80)
        
        api = RegRuAPI(config["regru_username"], config["regru_password"], logger)
        
        # Тест подключения
        if api.test_api_access():
            logger.info("")
            logger.info("=" * 80)
            logger.info("🧪 ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ")
            logger.info("=" * 80)
            
            # Тест получения DNS записей
            try:
                records = api.get_zone_records(config["domain"])
                logger.info(f"✅ Получение DNS записей: успешно ({len(records)} записей)")
            except Exception as e:
                logger.error(f"❌ Получение DNS записей: ошибка - {e}")
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
            logger.info("=" * 80)
            logger.info("API reg.ru готов к использованию!")
            return 0
        else:
            logger.error("=" * 80)
            logger.error("❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
            logger.error("=" * 80)
            logger.error("Исправьте проблемы с API перед использованием скрипта")
            return 1
    
    # Генерация тестового сертификата
    if args.test_cert:
        logger.info("=" * 80)
        logger.info("РЕЖИМ: Генерация тестового самоподписанного сертификата")
        logger.info("=" * 80)
        
        test_gen = TestCertificateGenerator(logger)
        success = test_gen.generate_self_signed_certificate(
            domain=config["domain"],
            wildcard=config.get("wildcard", False),
            output_dir=config["cert_dir"],
            validity_days=90
        )
        
        if success:
            # Опционально загружаем в NPM
            if config.get("npm_enabled", False):
                logger.info("")
                logger.info("=" * 80)
                logger.info("ЗАГРУЗКА ТЕСТОВОГО СЕРТИФИКАТА В NGINX PROXY MANAGER")
                logger.info("=" * 80)
                
                npm_api = NginxProxyManagerAPI(
                    config["npm_host"],
                    config["npm_email"],
                    config["npm_password"],
                    logger
                )
                
                if npm_api.login():
                    cert_dir = os.path.join(config["cert_dir"], config["domain"])
                    cert_path = os.path.join(cert_dir, "fullchain.pem")
                    key_path = os.path.join(cert_dir, "privkey.pem")
                    
                    # Проверяем существующий сертификат
                    existing = npm_api.find_certificate_by_domain(config["domain"])
                    
                    if existing:
                        # Обновляем существующий
                        cert_id = existing.get("id")
                        logger.info(f"Обновление существующего сертификата в NPM (ID: {cert_id})")
                        if npm_api.update_certificate(cert_id, cert_path, key_path):
                            logger.info("✅ Тестовый сертификат успешно обновлен в NPM")
                        else:
                            logger.warning("⚠️  Не удалось обновить сертификат в NPM")
                    else:
                        # Создаем новый
                        logger.info("Загрузка нового тестового сертификата в NPM")
                        if npm_api.upload_certificate(config["domain"], cert_path, key_path):
                            logger.info("✅ Тестовый сертификат успешно загружен в NPM")
                        else:
                            logger.warning("⚠️  Не удалось загрузить сертификат в NPM")
                else:
                    logger.error("Не удалось подключиться к Nginx Proxy Manager")
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ ТЕСТОВЫЙ СЕРТИФИКАТ УСПЕШНО СОЗДАН")
            logger.info("=" * 80)
            return 0
        else:
            logger.error("❌ Не удалось создать тестовый сертификат")
            return 1
    
    # Обработка хуков для certbot
    if args.auth_hook:
        try:
            logger.info("=" * 80)
            logger.info("🔑 AUTH HOOK ВЫЗВАН")
            logger.info("=" * 80)
            
            # Certbot передает домен и токен через переменные окружения
            domain = os.environ.get("CERTBOT_DOMAIN")
            token = os.environ.get("CERTBOT_VALIDATION")
            
            logger.info(f"CERTBOT_DOMAIN: {domain}")
            logger.info(f"CERTBOT_VALIDATION: {token[:20]}..." if token else "CERTBOT_VALIDATION: None")
            
            if not domain or not token:
                logger.error("CERTBOT_DOMAIN или CERTBOT_VALIDATION не установлены")
                logger.error("Переменные окружения:")
                for key in os.environ:
                    if key.startswith("CERTBOT_"):
                        logger.error(f"  {key}: {os.environ[key]}")
                return 1
            
            api = RegRuAPI(config["regru_username"], config["regru_password"], logger)
            manager = LetsEncryptManager(config, api, logger)
            success = manager.dns_challenge_hook(domain, token)
            
            if success:
                logger.info("✅ AUTH HOOK ЗАВЕРШЕН УСПЕШНО")
                return 0
            else:
                logger.error("❌ AUTH HOOK ЗАВЕРШИЛСЯ С ОШИБКОЙ")
                return 1
                
        except Exception as e:
            logger.error(f"💥 КРИТИЧЕСКАЯ ОШИБКА В AUTH HOOK: {e}")
            logger.exception("Traceback:")
            return 1
    
    if args.cleanup_hook:
        try:
            logger.info("=" * 80)
            logger.info("🧹 CLEANUP HOOK ВЫЗВАН")
            logger.info("=" * 80)
            
            domain = os.environ.get("CERTBOT_DOMAIN")
            token = os.environ.get("CERTBOT_VALIDATION")
            
            logger.info(f"CERTBOT_DOMAIN: {domain}")
            logger.info(f"CERTBOT_VALIDATION: {token[:20]}..." if token else "CERTBOT_VALIDATION: None")
            
            if not domain or not token:
                logger.error("CERTBOT_DOMAIN или CERTBOT_VALIDATION не установлены")
                logger.error("Переменные окружения:")
                for key in os.environ:
                    if key.startswith("CERTBOT_"):
                        logger.error(f"  {key}: {os.environ[key]}")
                return 1
            
            api = RegRuAPI(config["regru_username"], config["regru_password"], logger)
            manager = LetsEncryptManager(config, api, logger)
            success = manager.dns_cleanup_hook(domain, token)
            
            if success:
                logger.info("✅ CLEANUP HOOK ЗАВЕРШЕН УСПЕШНО")
                return 0
            else:
                logger.warning("⚠️ CLEANUP HOOK ЗАВЕРШИЛСЯ С ПРЕДУПРЕЖДЕНИЕМ (не критично)")
                return 0  # Cleanup hook не должен блокировать получение сертификата
                
        except Exception as e:
            logger.error(f"💥 ОШИБКА В CLEANUP HOOK: {e}")
            logger.exception("Traceback:")
            return 0  # Cleanup hook не должен блокировать получение сертификата
    
    # Проверка прав root
    if os.geteuid() != 0:
        logger.error("Скрипт должен быть запущен от имени root (sudo)")
        return 1
    
    # Инициализация API и менеджера
    api = RegRuAPI(config["regru_username"], config["regru_password"], logger)
    manager = LetsEncryptManager(config, api, logger)
    
    # Проверка certbot
    if not manager.check_certbot_installed():
        logger.error("Установите certbot: apt-get install certbot")
        return 1
    
    logger.info("=" * 60)
    logger.info("СКРИПТ УПРАВЛЕНИЯ SSL СЕРТИФИКАТАМИ LET'S ENCRYPT")
    logger.info("=" * 60)
    
    # Получаем текущий IP
    try:
        ip_response = requests.get("https://api.ipify.org", timeout=5)
        current_ip = ip_response.text
        logger.info(f"Текущий IP адрес: {current_ip}")
    except:
        logger.warning("Не удалось определить IP адрес")
    
    # Проверка доступности API reg.ru (кроме режимов только проверки)
    if not args.check:
        logger.info("Проверка доступности API reg.ru...")
        if not api.test_api_access():
            logger.error("=" * 80)
            logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: API reg.ru недоступен")
            logger.error("=" * 80)
            logger.error("Скрипт не может продолжить работу без доступа к API")
            logger.error("")
            logger.error("Возможные причины:")
            logger.error("  1. Неверные учётные данные reg.ru")
            logger.error("  2. IP адрес не добавлен в белый список API")
            logger.error("  3. Проблемы с интернет-соединением")
            logger.error("")
            logger.error("Проверьте настройки и запустите скрипт заново")
            logger.error("Для диагностики используйте: letsencrypt-regru --test-api -v")
            return 1
        logger.info("")
    
    # Выполнение действий
    if args.info:
        # Показать полную информацию о сертификате
        days_left = manager.check_certificate_expiry()
        
        if days_left is None:
            logger.error("Сертификат не найден")
            return 1
        
        # Проверяем тип сертификата
        is_staging = manager.is_staging_certificate()
        
        logger.info("")
        logger.info("=" * 80)
        if is_staging:
            logger.warning("ТИП СЕРТИФИКАТА: STAGING (ТЕСТОВЫЙ)")
            logger.warning("=" * 80)
            logger.warning("⚠️  Это тестовый сертификат Let's Encrypt")
            logger.warning("   • Издатель: Fake LE Intermediate X1 (staging)")
            logger.warning("   • Браузеры НЕ доверяют")
            logger.warning("   • НЕ загружен в Nginx Proxy Manager")
            logger.warning("   • БЕЗ лимитов на получение")
        else:
            logger.info("ТИП СЕРТИФИКАТА: PRODUCTION (БОЕВОЙ)")
            logger.info("=" * 80)
            logger.info("✅ Это настоящий сертификат Let's Encrypt")
            logger.info("   • Издатель: Let's Encrypt Authority")
            logger.info("   • Браузеры доверяют")
            logger.info("   • Загружен в Nginx Proxy Manager")
            logger.info("   • Лимит: 5 сертификатов/неделю")
        
        logger.info("")
        manager.display_certificate_info()
        
        if is_staging:
            logger.info("")
            logger.info("=" * 80)
            logger.info("🚀 Для получения PRODUCTION сертификата:")
            logger.info("   sudo letsencrypt-regru --obtain")
            logger.info("=" * 80)
        
        return 0
    
    elif args.check:
        # Только проверка срока действия
        days_left = manager.check_certificate_expiry()
        
        # Проверяем, является ли сертификат staging
        is_staging = manager.is_staging_certificate()
        
        if days_left is None:
            logger.info("Сертификат не найден. Требуется создание нового.")
            logger.info("")
            logger.info("Для получения production сертификата выполните:")
            logger.info("  sudo letsencrypt-regru --obtain")
            return 2
        elif is_staging:
            logger.warning("")
            logger.warning("=" * 80)
            logger.warning("⚠️  УСТАНОВЛЕН STAGING (ТЕСТОВЫЙ) СЕРТИФИКАТ!")
            logger.warning("=" * 80)
            logger.warning("Это тестовый сертификат Let's Encrypt из staging окружения")
            logger.warning("Браузеры НЕ будут доверять этому сертификату")
            logger.warning("Сертификат НЕ загружен в Nginx Proxy Manager")
            logger.warning("")
            logger.warning("🚀 Для получения PRODUCTION сертификата выполните:")
            logger.warning("   sudo letsencrypt-regru --obtain")
            logger.warning("=" * 80)
            return 3
        elif days_left < 30:
            logger.warning(f"Сертификат истекает через {days_left} дней. Требуется обновление!")
            logger.info("")
            logger.info("Для обновления сертификата выполните:")
            logger.info("  sudo letsencrypt-regru --renew")
            return 1
        else:
            logger.info(f"✅ Сертификат действителен ({days_left} дней)")
            logger.info("")
            logger.info("Сертификат в норме. Следующая проверка через:")
            logger.info(f"  {days_left - 30} дней (за 30 дней до истечения)")
            return 0
    
    elif args.staging:
        # Получение ТЕСТОВОГО сертификата из staging окружения
        logger.info("")
        logger.info("🧪" * 40)
        logger.info("РЕЖИМ STAGING: Тестовый сертификат Let's Encrypt")
        logger.info("🧪" * 40)
        logger.info("")
        logger.info("📋 ИНФОРМАЦИЯ О STAGING РЕЖИМЕ:")
        logger.info("  • Сертификат будет выдан staging CA (не доверенный)")
        logger.info("  • Браузеры покажут предупреждение о безопасности")
        logger.info("  • НЕТ лимитов на количество запросов (в отличие от production)")
        logger.info("  • Идеально для тестирования автоматизации и DNS")
        logger.info("  • Полностью идентичный процесс с production")
        logger.info("")
        logger.info("⚠️  НЕ используйте staging сертификаты на production сайтах!")
        logger.info("")
        
        success = manager.obtain_certificate(staging=True)
        
        if success:
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ ТЕСТОВЫЙ СЕРТИФИКАТ УСПЕШНО ПОЛУЧЕН")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📂 Расположение: /etc/letsencrypt/live/%s/" % config['domain'])
            logger.info("")
            logger.info("🔄 Следующие шаги:")
            logger.info("  1. ✅ Проверьте что процесс прошел успешно")
            logger.info("  2. ✅ Убедитесь что DNS записи создаются корректно")
            logger.info("  3. ✅ Проверьте автоматизацию")
            logger.info("  4. 🚀 Когда всё готово - получите production сертификат:")
            logger.info("     sudo letsencrypt-regru --obtain")
            logger.info("")
            logger.info("💡 ВАЖНО: Staging сертификаты хранятся в той же директории,")
            logger.info("           что и production. Для получения production сертификата")
            logger.info("           просто запустите команду --obtain")
            logger.info("")
            
            # Синхронизация с NPM (если включено)
            if config.get("npm_enabled", False):
                logger.warning("⚠️  Staging сертификат НЕ загружается в Nginx Proxy Manager")
                logger.warning("   (staging сертификаты не предназначены для production)")
        
        return 0 if success else 1
    
    elif args.obtain:
        # Принудительное получение нового сертификата
        success = manager.obtain_certificate(staging=False)
        if success:
            manager.display_certificate_info()
            reload_webserver(logger)
            
            # Синхронизация с Nginx Proxy Manager
            if config.get("npm_enabled", False):
                npm_api = NginxProxyManagerAPI(
                    config["npm_host"],
                    config["npm_email"],
                    config["npm_password"],
                    logger
                )
                if manager.sync_with_npm(npm_api):
                    logger.info("Сертификат успешно добавлен в Nginx Proxy Manager")
                else:
                    logger.warning("Не удалось синхронизировать сертификат с NPM")
            
            logger.info("Новый сертификат успешно создан")
            return 0
        else:
            logger.error("Не удалось получить сертификат")
            return 1
    
    elif args.renew:
        # Обновление существующего сертификата
        success = manager.renew_certificate()
        if success:
            manager.display_certificate_info()
            reload_webserver(logger)
            
            # Синхронизация с Nginx Proxy Manager
            if config.get("npm_enabled", False):
                npm_api = NginxProxyManagerAPI(
                    config["npm_host"],
                    config["npm_email"],
                    config["npm_password"],
                    logger
                )
                if manager.sync_with_npm(npm_api):
                    logger.info("Сертификат успешно обновлен в Nginx Proxy Manager")
                else:
                    logger.warning("Не удалось синхронизировать сертификат с NPM")
            
            logger.info("Сертификат успешно обновлен")
            return 0
        else:
            logger.error("Не удалось обновить сертификат")
            return 1
    
    elif args.list_npm:
        # Показать все сертификаты в NPM
        logger.info("=" * 80)
        logger.info("СПИСОК СЕРТИФИКАТОВ В NGINX PROXY MANAGER")
        logger.info("=" * 80)
        
        if not config.get("npm_enabled", False):
            logger.error("NPM не настроен в конфигурации!")
            return 1
        
        npm_api = NginxProxyManagerAPI(
            config["npm_host"],
            config["npm_email"],
            config["npm_password"],
            logger
        )
        
        if not npm_api.login():
            logger.error("Не удалось подключиться к NPM")
            return 1
        
        certificates = npm_api.get_certificates()
        
        if not certificates:
            logger.info("В NPM нет сертификатов")
            return 0
        
        logger.info(f"Всего сертификатов: {len(certificates)}")
        logger.info("")
        
        # Группируем дубликаты по domain_names
        from collections import defaultdict
        duplicates = defaultdict(list)
        
        for cert in certificates:
            domains_key = tuple(sorted(cert.get("domain_names", [])))
            duplicates[domains_key].append(cert)
        
        # Выводим список
        for domains_key, certs in sorted(duplicates.items()):
            domains_str = ", ".join(domains_key)
            
            if len(certs) > 1:
                logger.warning(f"⚠️  ДУБЛИКАТЫ для {domains_str}:")
                for cert in certs:
                    cert_id = cert.get("id")
                    created = cert.get("created_on", "Unknown")
                    expires = cert.get("expires_on", "Unknown")
                    provider = cert.get("provider", "Unknown")
                    logger.warning(f"   ID {cert_id}: создан {created}, истекает {expires}, тип {provider}")
            else:
                cert = certs[0]
                cert_id = cert.get("id")
                created = cert.get("created_on", "Unknown")
                expires = cert.get("expires_on", "Unknown")
                provider = cert.get("provider", "Unknown")
                logger.info(f"ID {cert_id}: {domains_str}")
                logger.info(f"         Создан: {created}, Истекает: {expires}, Тип: {provider}")
            logger.info("")
        
        # Показываем рекомендации по удалению дубликатов
        has_duplicates = any(len(certs) > 1 for certs in duplicates.values())
        if has_duplicates:
            logger.warning("=" * 80)
            logger.warning("Обнаружены дубликаты сертификатов!")
            logger.warning("Для удаления дубликата используйте:")
            logger.warning("  letsencrypt-regru --delete-npm CERT_ID")
            logger.warning("=" * 80)
        
        return 0
    
    elif args.delete_npm:
        # Удалить сертификат из NPM
        cert_id = args.delete_npm
        
        logger.info("=" * 80)
        logger.info(f"УДАЛЕНИЕ СЕРТИФИКАТА ID {cert_id} ИЗ NPM")
        logger.info("=" * 80)
        
        if not config.get("npm_enabled", False):
            logger.error("NPM не настроен в конфигурации!")
            return 1
        
        npm_api = NginxProxyManagerAPI(
            config["npm_host"],
            config["npm_email"],
            config["npm_password"],
            logger
        )
        
        if not npm_api.login():
            logger.error("Не удалось подключиться к NPM")
            return 1
        
        # Получаем информацию о сертификате
        certificates = npm_api.get_certificates()
        cert_to_delete = None
        
        for cert in certificates:
            if cert.get("id") == cert_id:
                cert_to_delete = cert
                break
        
        if not cert_to_delete:
            logger.error(f"Сертификат с ID {cert_id} не найден")
            logger.info("")
            logger.info("Доступные сертификаты:")
            for cert in certificates:
                logger.info(f"  ID {cert.get('id')}: {', '.join(cert.get('domain_names', []))}")
            return 1
        
        # Показываем информацию о сертификате
        domains = cert_to_delete.get("domain_names", [])
        logger.info(f"Сертификат: {', '.join(domains)}")
        logger.info(f"Создан: {cert_to_delete.get('created_on', 'Unknown')}")
        logger.info("")
        logger.warning("⚠️  ВНИМАНИЕ: Удаление сертификата нельзя отменить!")
        logger.warning("Продолжить удаление? (y/N): ")
        
        try:
            response = input().strip().lower()
            if response != 'y':
                logger.info("Отменено.")
                return 0
        except:
            logger.error("Требуется интерактивное подтверждение")
            return 1
        
        if npm_api.delete_certificate(cert_id):
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ СЕРТИФИКАТ УСПЕШНО УДАЛЕН")
            logger.info("=" * 80)
            return 0
        else:
            logger.error("Не удалось удалить сертификат")
            return 1
    
    elif args.upload_npm:
        # Загрузка существующего сертификата в NPM
        domain = args.upload_npm
        
        logger.info("=" * 80)
        logger.info(f"ЗАГРУЗКА СЕРТИФИКАТА В NGINX PROXY MANAGER")
        logger.info("=" * 80)
        logger.info(f"Домен: {domain}")
        logger.info("")
        
        # Проверяем настройки NPM
        if not config.get("npm_enabled", False):
            logger.error("NPM не настроен в конфигурации!")
            logger.error("Проверьте параметры npm_enabled, npm_host, npm_email, npm_password")
            return 1
        
        # Определяем пути к сертификату
        cert_dir = os.path.join(config["cert_dir"], domain)
        cert_path = os.path.join(cert_dir, "fullchain.pem")
        key_path = os.path.join(cert_dir, "privkey.pem")
        
        # Проверяем существование файлов
        if not os.path.exists(cert_path):
            logger.error(f"Сертификат не найден: {cert_path}")
            logger.error("")
            logger.error("Доступные домены в /etc/letsencrypt/live/:")
            try:
                live_dir = config["cert_dir"]
                if os.path.exists(live_dir):
                    for item in os.listdir(live_dir):
                        item_path = os.path.join(live_dir, item)
                        if os.path.isdir(item_path):
                            logger.error(f"  - {item}")
            except:
                pass
            return 1
        
        if not os.path.exists(key_path):
            logger.error(f"Приватный ключ не найден: {key_path}")
            return 1
        
        logger.info(f"✅ Найден сертификат: {cert_path}")
        logger.info(f"✅ Найден приватный ключ: {key_path}")
        
        # Анализируем содержимое сертификата
        try:
            with open(cert_path, 'r') as f:
                cert_content = f.read()
            cert_count = cert_content.count('-----BEGIN CERTIFICATE-----')
            logger.info(f"   Сертификатов в файле: {cert_count}")
            if cert_count > 1:
                logger.info(f"   (1 конечный + {cert_count - 1} промежуточных)")
        except:
            pass
        
        logger.info("")
        
        # Проверяем тип сертификата
        try:
            result = subprocess.run(
                ["openssl", "x509", "-in", cert_path, "-text", "-noout"],
                capture_output=True,
                text=True
            )
            is_staging = "fake" in result.stdout.lower() or "staging" in result.stdout.lower()
            
            # Показываем дату истечения
            for line in result.stdout.split('\n'):
                if 'Not After' in line:
                    logger.info(f"   Истекает: {line.strip()}")
                    break
            
            if is_staging:
                logger.warning("⚠️  ВНИМАНИЕ: Это STAGING (тестовый) сертификат!")
                logger.warning("   Браузеры не будут доверять этому сертификату")
                logger.warning("")
                logger.warning("Продолжить загрузку в NPM? (y/N): ")
                
                try:
                    response = input().strip().lower()
                    if response != 'y':
                        logger.info("Отменено.")
                        return 0
                except:
                    logger.warning("Пропускаем подтверждение (неинтерактивный режим)")
        except:
            pass
        
        # Подключаемся к NPM
        logger.info("Подключение к Nginx Proxy Manager...")
        npm_api = NginxProxyManagerAPI(
            config["npm_host"],
            config["npm_email"],
            config["npm_password"],
            logger
        )
        
        if not npm_api.login():
            logger.error("Не удалось подключиться к NPM")
            logger.error("Проверьте настройки npm_host, npm_email, npm_password в конфигурации")
            return 1
        
        logger.info("✅ Подключение к NPM успешно")
        logger.info("")
        
        # Получаем список всех сертификатов для диагностики
        all_certs = npm_api.get_certificates()
        logger.info(f"Всего сертификатов в NPM: {len(all_certs)}")
        
        if args.verbose and all_certs:
            logger.info("")
            logger.info("Список всех сертификатов в NPM:")
            for cert in all_certs:
                cert_id = cert.get("id")
                cert_name = cert.get("nice_name", "Unknown")
                domains = cert.get("domain_names", [])
                logger.info(f"  ID {cert_id}: '{cert_name}' -> {', '.join(domains)}")
            logger.info("")
        
        # Проверяем существующий сертификат
        logger.info(f"Поиск сертификата для домена '{domain}'...")
        existing = npm_api.find_certificate_by_domain(domain)
        
        if existing:
            cert_id = existing.get("id")
            logger.info(f"Найден существующий сертификат (ID: {cert_id})")
            logger.info("Обновление сертификата...")
            
            if npm_api.update_certificate(cert_id, cert_path, key_path):
                logger.info("")
                logger.info("=" * 80)
                logger.info("✅ СЕРТИФИКАТ УСПЕШНО ОБНОВЛЕН В NPM")
                logger.info("=" * 80)
                logger.info(f"ID сертификата: {cert_id}")
                logger.info(f"Домен: {domain}")
                logger.info("")
                
                # Проверяем результат
                updated_certs = npm_api.get_certificates()
                for cert in updated_certs:
                    if cert.get("id") == cert_id:
                        expires = cert.get("expires_on", "Unknown")
                        logger.info(f"Статус в NPM: {cert.get('provider', 'Unknown')}")
                        logger.info(f"Истекает: {expires}")
                        break
                
                return 0
            else:
                logger.error("Не удалось обновить сертификат в NPM")
                return 1
        else:
            logger.info("Существующий сертификат не найден")
            logger.info("Создание нового сертификата в NPM...")
            
            result = npm_api.upload_certificate(domain, cert_path, key_path)
            if result:
                cert_id = result.get("id")
                logger.info("")
                logger.info("=" * 80)
                logger.info("✅ СЕРТИФИКАТ УСПЕШНО ЗАГРУЖЕН В NPM")
                logger.info("=" * 80)
                logger.info(f"ID сертификата: {cert_id}")
                logger.info(f"Домен: {domain}")
                logger.info("")
                
                # Проверяем результат (повторно получаем из NPM, если возможно)
                try:
                    final = npm_api.get_certificate_by_id(cert_id)
                    if final:
                        provider = final.get('provider', result.get('provider', 'Unknown'))
                        expires = final.get('expires_on', result.get('expires_on', 'Unknown'))
                        domains = final.get('domain_names', [])
                        logger.info(f"Статус в NPM: {provider}")
                        logger.info(f"Домены: {', '.join(domains) if domains else '[пока не распознаны]'}")
                        logger.info(f"Истекает: {expires}")
                    else:
                        logger.info(f"Статус в NPM: {result.get('provider', 'Unknown')}")
                        logger.info(f"Истекает: {result.get('expires_on', 'Unknown')}")
                except Exception:
                    logger.info(f"Статус в NPM: {result.get('provider', 'Unknown')}")
                    logger.info(f"Истекает: {result.get('expires_on', 'Unknown')}")
                logger.info("")
                logger.info("Теперь вы можете использовать этот сертификат в Proxy Hosts")
                return 0
            else:
                logger.error("Не удалось загрузить сертификат в NPM")
                return 1
    
    else:
        # Автоматический режим: проверка и обновление при необходимости
        logger.info("=" * 60)
        logger.info("АВТОМАТИЧЕСКАЯ ПРОВЕРКА И ОБНОВЛЕНИЕ СЕРТИФИКАТА")
        logger.info("=" * 60)
        
        # Получаем порог для обновления из конфигурации
        renewal_days = config.get("renewal_days", 30)
        logger.info(f"Порог обновления: {renewal_days} дней до истечения")
        
        # Проверяем срок действия сертификата
        days_left = manager.check_certificate_expiry()
        
        if days_left is None:
            # Сертификат не существует - создаем новый
            logger.info("=" * 60)
            logger.info("СТАТУС: Сертификат не найден")
            logger.info("ДЕЙСТВИЕ: Создание нового сертификата")
            logger.info("=" * 60)
            success = manager.obtain_certificate()
            action = "создан"
        elif days_left < renewal_days:
            # Сертификат скоро истекает - обновляем
            logger.info("=" * 60)
            logger.info(f"СТАТУС: Сертификат истекает через {days_left} дней")
            logger.info(f"ДЕЙСТВИЕ: Обновление сертификата (порог: {renewal_days} дней)")
            logger.info("=" * 60)
            success = manager.renew_certificate()
            action = "обновлен"
        else:
            # Сертификат действителен - ничего не делаем
            logger.info("=" * 60)
            logger.info(f"СТАТУС: Сертификат действителен ({days_left} дней)")
            logger.info("ДЕЙСТВИЕ: Обновление не требуется")
            logger.info("=" * 60)
            manager.display_certificate_info()
            
            # Проверяем синхронизацию с NPM даже если сертификат действителен
            if config.get("npm_enabled", False):
                logger.info("Проверка синхронизации с Nginx Proxy Manager...")
                npm_api = NginxProxyManagerAPI(
                    config["npm_host"],
                    config["npm_email"],
                    config["npm_password"],
                    logger
                )
                existing_cert = npm_api.login() and npm_api.find_certificate_by_domain(manager.domain)
                if existing_cert:
                    logger.info(f"Сертификат найден в NPM (ID: {existing_cert.get('id')})")
                else:
                    logger.info("Сертификат не найден в NPM. Синхронизация...")
                    if manager.sync_with_npm(npm_api):
                        logger.info("Сертификат успешно синхронизирован с NPM")
            
            return 0
        
        # Если был создан или обновлен сертификат
        if success:
            logger.info("=" * 60)
            logger.info(f"РЕЗУЛЬТАТ: Сертификат успешно {action}")
            logger.info("=" * 60)
            
            manager.display_certificate_info()
            reload_webserver(logger)
            
            # Синхронизация с Nginx Proxy Manager
            if config.get("npm_enabled", False):
                logger.info("=" * 60)
                logger.info("СИНХРОНИЗАЦИЯ С NGINX PROXY MANAGER")
                logger.info("=" * 60)
                
                npm_api = NginxProxyManagerAPI(
                    config["npm_host"],
                    config["npm_email"],
                    config["npm_password"],
                    logger
                )
                if manager.sync_with_npm(npm_api):
                    logger.info(f"✅ Сертификат успешно {action} в Nginx Proxy Manager")
                else:
                    logger.warning("⚠️  Не удалось синхронизировать сертификат с NPM")
            
            logger.info("=" * 60)
            logger.info("ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
            logger.info("=" * 60)
            return 0
        else:
            logger.error("Операция завершилась с ошибкой")
            return 1


if __name__ == "__main__":
    sys.exit(main())
