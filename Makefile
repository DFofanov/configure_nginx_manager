# ==============================================================================
# Makefile для установки и удаления скрипта управления SSL сертификатами
# Let's Encrypt с DNS-валидацией через API reg.ru
# ==============================================================================

# Переменные
INSTALL_DIR = /opt/letsencrypt-regru
SCRIPT_NAME = letsencrypt_regru_api.py
CONFIG_EXAMPLE = config.json.example
SERVICE_NAME = letsencrypt-regru
SERVICE_FILE = $(SERVICE_NAME).service
TIMER_FILE = $(SERVICE_NAME).timer
CONFIG_DIR = /etc/letsencrypt
CONFIG_FILE = $(CONFIG_DIR)/regru_config.json
LOG_DIR = /var/log
LOG_FILE = $(LOG_DIR)/letsencrypt_regru.log
CRON_LOG = $(LOG_DIR)/letsencrypt_cron.log
SYSTEMD_DIR = /etc/systemd/system
PYTHON = python3

# Цвета для вывода
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help install uninstall status check-root setup-dirs install-script install-service install-cron clean

# ==============================================================================
# Помощь
# ==============================================================================

help:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Makefile для управления Let's Encrypt SSL сертификатами      ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Доступные команды:$(NC)"
	@echo ""
	@echo "  $(YELLOW)make install$(NC)      - Установить скрипт и настроить автоматизацию"
	@echo "  $(YELLOW)make uninstall$(NC)    - Удалить скрипт и очистить систему"
	@echo "  $(YELLOW)make status$(NC)       - Проверить статус установки"
	@echo "  $(YELLOW)make check-config$(NC) - Проверить конфигурацию"
	@echo "  $(YELLOW)make test-run$(NC)     - Тестовый запуск скрипта"
	@echo "  $(YELLOW)make test-cert$(NC)    - Создать тестовый самоподписанный сертификат"
	@echo "  $(YELLOW)make logs$(NC)         - Показать логи"
	@echo "  $(YELLOW)make help$(NC)         - Показать эту справку"
	@echo ""

# ==============================================================================
# Проверка прав root
# ==============================================================================

check-root:
	@if [ "$$(id -u)" != "0" ]; then \
		echo "$(RED)✗ Ошибка: Требуются права root$(NC)"; \
		echo "$(YELLOW)Запустите: sudo make install$(NC)"; \
		exit 1; \
	fi

# ==============================================================================
# Установка
# ==============================================================================

install: check-root
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Установка Let's Encrypt SSL Manager                          ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@$(MAKE) setup-dirs
	@$(MAKE) install-dependencies
	@$(MAKE) install-script
	@$(MAKE) install-service
	@$(MAKE) install-cron
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  ✓ Установка завершена успешно!                               ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Следующие шаги:$(NC)"
	@echo "  1. Отредактируйте конфигурацию:"
	@echo "     $(BLUE)sudo nano $(CONFIG_FILE)$(NC)"
	@echo ""
	@echo "  2. Проверьте конфигурацию:"
	@echo "     $(BLUE)make check-config$(NC)"
	@echo ""
	@echo "  3. Запустите тестовую проверку:"
	@echo "     $(BLUE)make test-run$(NC)"
	@echo ""
	@echo "  4. Проверьте статус службы:"
	@echo "     $(BLUE)make status$(NC)"
	@echo ""

# Создание директорий
setup-dirs:
	@echo "$(YELLOW)→ Создание директорий...$(NC)"
	@mkdir -p $(INSTALL_DIR)
	@mkdir -p $(CONFIG_DIR)
	@mkdir -p $(LOG_DIR)
	@echo "$(GREEN)✓ Директории созданы$(NC)"

# Установка зависимостей
install-dependencies:
	@echo "$(YELLOW)→ Установка зависимостей Python...$(NC)"
	@if ! command -v pip3 >/dev/null 2>&1; then \
		echo "$(RED)✗ pip3 не найден. Установите python3-pip$(NC)"; \
		exit 1; \
	fi
	@pip3 install -q requests cryptography 2>/dev/null || pip3 install requests cryptography
	@echo "$(GREEN)✓ Зависимости установлены$(NC)"

# Копирование скрипта
install-script:
	@echo "$(YELLOW)→ Установка скрипта...$(NC)"
	@if [ ! -f "$(SCRIPT_NAME)" ]; then \
		echo "$(RED)✗ Файл $(SCRIPT_NAME) не найден!$(NC)"; \
		exit 1; \
	fi
	@cp $(SCRIPT_NAME) $(INSTALL_DIR)/
	@chmod +x $(INSTALL_DIR)/$(SCRIPT_NAME)
	@echo "$(GREEN)✓ Скрипт установлен в $(INSTALL_DIR)/$(NC)"
	@echo ""
	@echo "$(YELLOW)→ Создание конфигурации...$(NC)"
	@if [ ! -f "$(CONFIG_FILE)" ]; then \
		if [ -f "$(CONFIG_EXAMPLE)" ]; then \
			cp $(CONFIG_EXAMPLE) $(CONFIG_FILE); \
			chmod 600 $(CONFIG_FILE); \
			echo "$(GREEN)✓ Создан файл конфигурации: $(CONFIG_FILE)$(NC)"; \
			echo "$(YELLOW)⚠ ВНИМАНИЕ: Отредактируйте конфигурацию перед использованием!$(NC)"; \
		else \
			echo "$(YELLOW)⚠ Файл config.json.example не найден$(NC)"; \
			$(PYTHON) $(INSTALL_DIR)/$(SCRIPT_NAME) --create-config $(CONFIG_FILE); \
			chmod 600 $(CONFIG_FILE); \
			echo "$(GREEN)✓ Создана конфигурация по умолчанию$(NC)"; \
		fi \
	else \
		echo "$(GREEN)✓ Конфигурация уже существует: $(CONFIG_FILE)$(NC)"; \
	fi

# Установка systemd service и timer
install-service:
	@echo "$(YELLOW)→ Создание systemd service...$(NC)"
	@echo "[Unit]" > $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "Description=Let's Encrypt Certificate Manager with reg.ru DNS" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "After=network.target" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "[Service]" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "Type=oneshot" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "ExecStart=$(PYTHON) $(INSTALL_DIR)/$(SCRIPT_NAME) -c $(CONFIG_FILE)" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "StandardOutput=journal" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "StandardError=journal" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "User=root" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "[Install]" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "WantedBy=multi-user.target" >> $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "$(GREEN)✓ Service файл создан$(NC)"
	@echo ""
	@echo "$(YELLOW)→ Создание systemd timer...$(NC)"
	@echo "[Unit]" > $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "Description=Daily Let's Encrypt Certificate Check and Renewal" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "Requires=$(SERVICE_FILE)" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "[Timer]" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "OnCalendar=daily" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "Persistent=true" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "RandomizedDelaySec=1h" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "[Install]" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "WantedBy=timers.target" >> $(SYSTEMD_DIR)/$(TIMER_FILE)
	@echo "$(GREEN)✓ Timer файл создан$(NC)"
	@echo ""
	@echo "$(YELLOW)→ Активация systemd службы...$(NC)"
	@systemctl daemon-reload
	@systemctl enable $(SERVICE_FILE) 2>/dev/null || true
	@systemctl enable $(TIMER_FILE) 2>/dev/null || true
	@systemctl start $(TIMER_FILE) 2>/dev/null || true
	@echo "$(GREEN)✓ Systemd служба активирована$(NC)"

# Установка cron задачи
install-cron:
	@echo "$(YELLOW)→ Настройка cron задачи...$(NC)"
	@CRON_CMD="0 3 * * * $(PYTHON) $(INSTALL_DIR)/$(SCRIPT_NAME) -c $(CONFIG_FILE) >> $(CRON_LOG) 2>&1"; \
	(crontab -l 2>/dev/null | grep -v "$(SCRIPT_NAME)" ; echo "$$CRON_CMD") | crontab -
	@echo "$(GREEN)✓ Cron задача добавлена (ежедневно в 3:00 AM)$(NC)"

# ==============================================================================
# Удаление
# ==============================================================================

uninstall: check-root
	@echo "$(RED)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(RED)║  Удаление Let's Encrypt SSL Manager                           ║$(NC)"
	@echo "$(RED)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@read -p "Вы уверены? Это удалит все файлы и настройки [y/N]: " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(MAKE) remove-service; \
		$(MAKE) remove-cron; \
		$(MAKE) remove-files; \
		echo ""; \
		echo "$(GREEN)✓ Удаление завершено$(NC)"; \
	else \
		echo "$(YELLOW)Удаление отменено$(NC)"; \
	fi

# Удаление systemd service
remove-service:
	@echo "$(YELLOW)→ Остановка и удаление systemd служб...$(NC)"
	@systemctl stop $(TIMER_FILE) 2>/dev/null || true
	@systemctl stop $(SERVICE_FILE) 2>/dev/null || true
	@systemctl disable $(TIMER_FILE) 2>/dev/null || true
	@systemctl disable $(SERVICE_FILE) 2>/dev/null || true
	@rm -f $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@rm -f $(SYSTEMD_DIR)/$(TIMER_FILE)
	@systemctl daemon-reload
	@echo "$(GREEN)✓ Systemd службы удалены$(NC)"

# Удаление cron задачи
remove-cron:
	@echo "$(YELLOW)→ Удаление cron задачи...$(NC)"
	@crontab -l 2>/dev/null | grep -v "$(SCRIPT_NAME)" | crontab - 2>/dev/null || true
	@echo "$(GREEN)✓ Cron задача удалена$(NC)"

# Удаление файлов
remove-files:
	@echo "$(YELLOW)→ Удаление файлов...$(NC)"
	@rm -rf $(INSTALL_DIR)
	@echo "$(GREEN)✓ Директория $(INSTALL_DIR) удалена$(NC)"
	@echo ""
	@read -p "Удалить конфигурацию $(CONFIG_FILE)? [y/N]: " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f $(CONFIG_FILE); \
		echo "$(GREEN)✓ Конфигурация удалена$(NC)"; \
	else \
		echo "$(YELLOW)Конфигурация сохранена$(NC)"; \
	fi
	@echo ""
	@read -p "Удалить логи? [y/N]: " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f $(LOG_FILE) $(CRON_LOG); \
		echo "$(GREEN)✓ Логи удалены$(NC)"; \
	else \
		echo "$(YELLOW)Логи сохранены$(NC)"; \
	fi

# ==============================================================================
# Утилиты
# ==============================================================================

# Проверка статуса
status:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Статус Let's Encrypt SSL Manager                             ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)→ Установка:$(NC)"
	@if [ -d "$(INSTALL_DIR)" ]; then \
		echo "  $(GREEN)✓ Директория: $(INSTALL_DIR)$(NC)"; \
	else \
		echo "  $(RED)✗ Директория не найдена$(NC)"; \
	fi
	@if [ -f "$(INSTALL_DIR)/$(SCRIPT_NAME)" ]; then \
		echo "  $(GREEN)✓ Скрипт установлен$(NC)"; \
	else \
		echo "  $(RED)✗ Скрипт не найден$(NC)"; \
	fi
	@if [ -f "$(CONFIG_FILE)" ]; then \
		echo "  $(GREEN)✓ Конфигурация: $(CONFIG_FILE)$(NC)"; \
	else \
		echo "  $(YELLOW)⚠ Конфигурация не найдена$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)→ Systemd служба:$(NC)"
	@systemctl is-enabled $(SERVICE_FILE) 2>/dev/null && echo "  $(GREEN)✓ Service включен$(NC)" || echo "  $(RED)✗ Service отключен$(NC)"
	@systemctl is-active $(SERVICE_FILE) 2>/dev/null && echo "  $(GREEN)✓ Service активен$(NC)" || echo "  $(YELLOW)⚠ Service неактивен (oneshot)$(NC)"
	@echo ""
	@echo "$(YELLOW)→ Systemd timer:$(NC)"
	@systemctl is-enabled $(TIMER_FILE) 2>/dev/null && echo "  $(GREEN)✓ Timer включен$(NC)" || echo "  $(RED)✗ Timer отключен$(NC)"
	@systemctl is-active $(TIMER_FILE) 2>/dev/null && echo "  $(GREEN)✓ Timer активен$(NC)" || echo "  $(RED)✗ Timer неактивен$(NC)"
	@echo ""
	@echo "$(YELLOW)→ Следующий запуск:$(NC)"
	@systemctl list-timers $(TIMER_FILE) --no-pager 2>/dev/null || echo "  $(RED)✗ Timer не найден$(NC)"
	@echo ""
	@echo "$(YELLOW)→ Cron задача:$(NC)"
	@if crontab -l 2>/dev/null | grep -q "$(SCRIPT_NAME)"; then \
		echo "  $(GREEN)✓ Cron задача настроена$(NC)"; \
		crontab -l 2>/dev/null | grep "$(SCRIPT_NAME)"; \
	else \
		echo "  $(RED)✗ Cron задача не найдена$(NC)"; \
	fi

# Проверка конфигурации
check-config:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Проверка конфигурации                                         ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@if [ ! -f "$(CONFIG_FILE)" ]; then \
		echo "$(RED)✗ Конфигурация не найдена: $(CONFIG_FILE)$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Конфигурация найдена$(NC)"
	@echo ""
	@$(PYTHON) -c "import json; print(json.dumps(json.load(open('$(CONFIG_FILE)')), indent=2, ensure_ascii=False))" 2>/dev/null || \
		(echo "$(RED)✗ Ошибка: Неверный формат JSON$(NC)"; exit 1)
	@echo ""
	@echo "$(YELLOW)→ Проверка обязательных параметров:$(NC)"
	@$(PYTHON) -c "import json; c=json.load(open('$(CONFIG_FILE)')); assert c.get('regru_username'), 'regru_username не задан'" && echo "  $(GREEN)✓ regru_username$(NC)" || echo "  $(RED)✗ regru_username$(NC)"
	@$(PYTHON) -c "import json; c=json.load(open('$(CONFIG_FILE)')); assert c.get('regru_password'), 'regru_password не задан'" && echo "  $(GREEN)✓ regru_password$(NC)" || echo "  $(RED)✗ regru_password$(NC)"
	@$(PYTHON) -c "import json; c=json.load(open('$(CONFIG_FILE)')); assert c.get('domain'), 'domain не задан'" && echo "  $(GREEN)✓ domain$(NC)" || echo "  $(RED)✗ domain$(NC)"
	@$(PYTHON) -c "import json; c=json.load(open('$(CONFIG_FILE)')); assert c.get('email'), 'email не задан'" && echo "  $(GREEN)✓ email$(NC)" || echo "  $(RED)✗ email$(NC)"

# Тестовый запуск
test-run: check-root
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Тестовый запуск скрипта                                       ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@if [ ! -f "$(CONFIG_FILE)" ]; then \
		echo "$(RED)✗ Конфигурация не найдена. Запустите: make install$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)→ Запуск проверки сертификата...$(NC)"
	@echo ""
	@$(PYTHON) $(INSTALL_DIR)/$(SCRIPT_NAME) -c $(CONFIG_FILE) --check -v

# Просмотр логов
logs:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Логи Let's Encrypt SSL Manager                               ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)→ Основной лог скрипта:$(NC)"
	@if [ -f "$(LOG_FILE)" ]; then \
		tail -n 50 $(LOG_FILE); \
	else \
		echo "$(YELLOW)Лог файл не найден$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)→ Лог cron задачи:$(NC)"
	@if [ -f "$(CRON_LOG)" ]; then \
		tail -n 50 $(CRON_LOG); \
	else \
		echo "$(YELLOW)Лог cron не найден$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)→ Логи systemd:$(NC)"
	@journalctl -u $(SERVICE_FILE) -n 50 --no-pager 2>/dev/null || echo "$(YELLOW)Логи systemd не найдены$(NC)"

# Ручной запуск обновления
run: check-root
	@echo "$(YELLOW)→ Запуск обновления сертификата...$(NC)"
	@$(PYTHON) $(INSTALL_DIR)/$(SCRIPT_NAME) -c $(CONFIG_FILE) -v

# Принудительное получение сертификата
obtain: check-root
	@echo "$(YELLOW)→ Принудительное получение нового сертификата...$(NC)"
	@$(PYTHON) $(INSTALL_DIR)/$(SCRIPT_NAME) -c $(CONFIG_FILE) --obtain -v

# Принудительное обновление сертификата
renew: check-root
	@echo "$(YELLOW)→ Принудительное обновление сертификата...$(NC)"
	@$(PYTHON) $(INSTALL_DIR)/$(SCRIPT_NAME) -c $(CONFIG_FILE) --renew -v

# Создание тестового самоподписанного сертификата
test-cert: check-root
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Создание тестового самоподписанного сертификата               ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)⚠️  ВНИМАНИЕ: Это тестовый сертификат для разработки!$(NC)"
	@echo "$(YELLOW)   Браузеры будут показывать предупреждение безопасности.$(NC)"
	@echo "$(YELLOW)   Для production используйте Let's Encrypt сертификаты.$(NC)"
	@echo ""
	@if [ ! -f "$(CONFIG_FILE)" ]; then \
		echo "$(RED)✗ Конфигурация не найдена. Запустите: make install$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)→ Генерация самоподписанного сертификата...$(NC)"
	@echo ""
	@$(PYTHON) $(INSTALL_DIR)/$(SCRIPT_NAME) -c $(CONFIG_FILE) --test-cert -v
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  ✓ Тестовый сертификат создан                                  ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Преимущества тестового сертификата:$(NC)"
	@echo "  • Нет ограничений Let's Encrypt (5 сертификатов в неделю)"
	@echo "  • Мгновенное создание без DNS-валидации"
	@echo "  • Идеально для тестирования интеграции с NPM"
	@echo "  • Можно создавать неограниченное количество раз"
	@echo ""
	@echo "$(YELLOW)Примечание:$(NC)"
	@echo "  Тестовый сертификат НЕ доверяется браузерами."
	@echo "  Используйте только для локальной разработки и тестирования."
	@echo ""

# Очистка временных файлов
clean:
	@echo "$(YELLOW)→ Очистка временных файлов...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@echo "$(GREEN)✓ Очистка завершена$(NC)"

# По умолчанию показываем помощь
.DEFAULT_GOAL := help
