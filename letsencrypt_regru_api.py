#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для создания и обновления SSL сертификата Let's Encrypt
с использованием DNS-валидации через API reg.ru

Автор: GitHub Copilot
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

# ==============================================================================
# КОНФИГУРАЦИЯ
# ==============================================================================

# Настройки по умолчанию
DEFAULT_CONFIG = {
    # Учетные данные API reg.ru
    "regru_username": "your_username",
    "regru_password": "your_password",
    
    # Параметры домена
    "domain": "dfv24.com",
    "wildcard": True,  # Создавать wildcard сертификат (*.domain.com)
    
    # Email для уведомлений Let's Encrypt
    "email": "admin@dfv24.com",
    
    # Директории
    "cert_dir": "/etc/letsencrypt/live",
    "log_file": "/var/log/letsencrypt_regru.log",
    
    # Параметры DNS
    "dns_propagation_wait": 60,  # Время ожидания распространения DNS (секунды)
    "dns_check_attempts": 10,     # Количество попыток проверки DNS
    "dns_check_interval": 10,     # Интервал между проверками DNS (секунды)
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
        datefmt='%Y-%m-%d %H:%M:%S'
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
            response = self.session.post(url, data=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("result") == "success":
                self.logger.debug(f"Запрос {method} выполнен успешно")
                return result
            else:
                error_msg = result.get("error_text", "Неизвестная ошибка")
                self.logger.error(f"Ошибка API: {error_msg}")
                raise Exception(f"API Error: {error_msg}")
                
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
        
        params = {
            "domain": domain,
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
        
        params = {
            "domain": domain,
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
            return False
        
        params = {
            "domain": domain,
            "record_id": record_id
        }
        
        try:
            self._make_request("zone/remove_record", params)
            self.logger.info("TXT запись успешно удалена")
            return True
        except Exception as e:
            self.logger.error(f"Не удалось удалить TXT запись: {e}")
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
            
            with open(cert_file, "rb") as f:
                cert_data = f.read()
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            expiry_date = cert.not_valid_after
            days_left = (expiry_date - datetime.now()).days
            
            self.logger.info(f"Сертификат истекает: {expiry_date.strftime('%Y-%m-%d')}")
            self.logger.info(f"Осталось дней: {days_left}")
            
            return days_left
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке сертификата: {e}")
            return None
    
    def dns_challenge_hook(self, validation_domain: str, validation_token: str) -> bool:
        """
        Обработчик DNS challenge - добавление TXT записи
        
        Args:
            validation_domain: Домен для валидации (_acme-challenge.domain.com)
            validation_token: Токен валидации
            
        Returns:
            True если успешно
        """
        self.logger.info("=== DNS Challenge: Добавление TXT записи ===")
        
        # Извлекаем поддомен из validation_domain
        # Формат: _acme-challenge.domain.com или _acme-challenge
        parts = validation_domain.replace(f".{self.domain}", "").split(".")
        subdomain = parts[0] if parts else "_acme-challenge"
        
        # Добавляем TXT запись
        success = self.api.add_txt_record(self.domain, subdomain, validation_token)
        
        if success:
            # Ждем распространения DNS
            wait_time = self.config.get("dns_propagation_wait", 60)
            self.logger.info(f"Ожидание распространения DNS ({wait_time} секунд)...")
            time.sleep(wait_time)
            
            # Проверяем DNS запись
            if self.verify_dns_record(subdomain, validation_token):
                self.logger.info("DNS валидация готова")
                return True
            else:
                self.logger.warning("DNS запись не распространилась вовремя, но продолжаем...")
                return True
        
        return False
    
    def dns_cleanup_hook(self, validation_domain: str, validation_token: str) -> bool:
        """
        Обработчик очистки DNS challenge - удаление TXT записи
        
        Args:
            validation_domain: Домен валидации
            validation_token: Токен валидации
            
        Returns:
            True если успешно
        """
        self.logger.info("=== DNS Challenge: Удаление TXT записи ===")
        
        parts = validation_domain.replace(f".{self.domain}", "").split(".")
        subdomain = parts[0] if parts else "_acme-challenge"
        
        return self.api.remove_txt_record(self.domain, subdomain, validation_token)
    
    def verify_dns_record(self, subdomain: str, expected_value: str) -> bool:
        """
        Проверка наличия DNS записи
        
        Args:
            subdomain: Поддомен
            expected_value: Ожидаемое значение TXT записи
            
        Returns:
            True если запись найдена
        """
        import socket
        
        full_domain = f"{subdomain}.{self.domain}"
        attempts = self.config.get("dns_check_attempts", 10)
        interval = self.config.get("dns_check_interval", 10)
        
        self.logger.info(f"Проверка DNS записи для {full_domain}")
        
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
                    self.logger.info(f"DNS запись найдена (попытка {attempt + 1})")
                    return True
                    
            except Exception as e:
                self.logger.debug(f"Попытка {attempt + 1}: DNS запись не найдена - {e}")
            
            if attempt < attempts - 1:
                time.sleep(interval)
        
        self.logger.warning("DNS запись не найдена после всех попыток")
        return False
    
    def obtain_certificate(self) -> bool:
        """
        Получение нового сертификата
        
        Returns:
            True если успешно
        """
        self.logger.info("=== Запрос нового SSL сертификата ===")
        
        # Формируем список доменов
        domains = [self.domain]
        if self.config.get("wildcard", False):
            domains.append(f"*.{self.domain}")
        
        domain_args = []
        for d in domains:
            domain_args.extend(["-d", d])
        
        # Команда certbot
        cmd = [
            "certbot", "certonly",
            "--manual",
            "--preferred-challenges", "dns",
            "--manual-auth-hook", f"{sys.executable} {os.path.abspath(__file__)} --auth-hook",
            "--manual-cleanup-hook", f"{sys.executable} {os.path.abspath(__file__)} --cleanup-hook",
            "--email", self.email,
            "--agree-tos",
            "--non-interactive",
            "--expand",
        ] + domain_args
        
        self.logger.info(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info("Сертификат успешно получен!")
            self.logger.debug(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Ошибка при получении сертификата: {e}")
            self.logger.error(e.stderr)
            return False
    
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
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"Ошибка при чтении сертификата: {e}")


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
        description="Автоматическое управление SSL сертификатами Let's Encrypt через API reg.ru"
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
    parser.add_argument(
        "--obtain",
        help="Получить новый сертификат",
        action="store_true"
    )
    parser.add_argument(
        "--renew",
        help="Обновить существующий сертификат",
        action="store_true"
    )
    parser.add_argument(
        "--check",
        help="Проверить срок действия сертификата",
        action="store_true"
    )
    parser.add_argument(
        "--auth-hook",
        help="Внутренний хук для DNS аутентификации (используется certbot)",
        action="store_true"
    )
    parser.add_argument(
        "--cleanup-hook",
        help="Внутренний хук для очистки DNS (используется certbot)",
        action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Подробный вывод",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Создание примера конфигурации
    if args.create_config:
        create_sample_config(args.create_config)
        return 0
    
    # Загрузка конфигурации
    config = load_config(args.config)
    
    # Настройка логирования
    logger = setup_logging(config["log_file"], args.verbose)
    
    # Обработка хуков для certbot
    if args.auth_hook:
        # Certbot передает домен и токен через переменные окружения
        domain = os.environ.get("CERTBOT_DOMAIN")
        token = os.environ.get("CERTBOT_VALIDATION")
        
        if domain and token:
            api = RegRuAPI(config["regru_username"], config["regru_password"], logger)
            manager = LetsEncryptManager(config, api, logger)
            success = manager.dns_challenge_hook(domain, token)
            return 0 if success else 1
        else:
            logger.error("CERTBOT_DOMAIN или CERTBOT_VALIDATION не установлены")
            return 1
    
    if args.cleanup_hook:
        domain = os.environ.get("CERTBOT_DOMAIN")
        token = os.environ.get("CERTBOT_VALIDATION")
        
        if domain and token:
            api = RegRuAPI(config["regru_username"], config["regru_password"], logger)
            manager = LetsEncryptManager(config, api, logger)
            success = manager.dns_cleanup_hook(domain, token)
            return 0 if success else 1
        else:
            logger.error("CERTBOT_DOMAIN или CERTBOT_VALIDATION не установлены")
            return 1
    
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
    
    # Выполнение действий
    if args.check:
        # Только проверка срока действия
        days_left = manager.check_certificate_expiry()
        if days_left is None:
            logger.info("Сертификат не найден. Требуется создание нового.")
            return 2
        elif days_left < 30:
            logger.warning(f"Сертификат истекает через {days_left} дней. Требуется обновление!")
            return 1
        else:
            logger.info(f"Сертификат действителен ({days_left} дней)")
            return 0
    
    elif args.obtain:
        # Принудительное получение нового сертификата
        success = manager.obtain_certificate()
        if success:
            manager.display_certificate_info()
            reload_webserver(logger)
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
            logger.info("Сертификат успешно обновлен")
            return 0
        else:
            logger.error("Не удалось обновить сертификат")
            return 1
    
    else:
        # Автоматический режим: проверка и обновление при необходимости
        days_left = manager.check_certificate_expiry()
        
        if days_left is None:
            # Сертификат не существует
            logger.info("Сертификат не найден. Создание нового...")
            success = manager.obtain_certificate()
        elif days_left < 30:
            # Сертификат скоро истекает
            logger.info(f"Сертификат истекает через {days_left} дней. Обновление...")
            success = manager.renew_certificate()
        else:
            # Сертификат действителен
            logger.info(f"Сертификат действителен ({days_left} дней). Обновление не требуется.")
            manager.display_certificate_info()
            return 0
        
        if success:
            manager.display_certificate_info()
            reload_webserver(logger)
            logger.info("Операция завершена успешно")
            return 0
        else:
            logger.error("Операция завершилась с ошибкой")
            return 1


if __name__ == "__main__":
    sys.exit(main())
