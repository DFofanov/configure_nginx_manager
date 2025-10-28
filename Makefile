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

.PHONY: help install uninstall status check-root setup-dirs install-script install-service install-cron clean build build-linux build-windows build-all package-linux package-windows release

# Переменные для сборки
PYINSTALLER = pyinstaller
APP_NAME = letsencrypt-regru
DIST_DIR = dist
BUILD_DIR_PY = build
SPEC_FILE = $(APP_NAME).spec

# ==============================================================================
# Помощь
# ==============================================================================

help:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Makefile для управления Let's Encrypt SSL сертификатами      ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Команды для установки:$(NC)"
	@echo ""
	@echo "  $(YELLOW)make install$(NC)      - Установить скрипт и настроить автоматизацию"
	@echo "  $(YELLOW)make uninstall$(NC)    - Удалить скрипт и очистить систему"
	@echo "  $(YELLOW)make status$(NC)       - Проверить статус установки"
	@echo "  $(YELLOW)make check-config$(NC) - Проверить конфигурацию"
	@echo "  $(YELLOW)make test-run$(NC)     - Тестовый запуск скрипта"
	@echo "  $(YELLOW)make test-cert$(NC)    - Создать тестовый самоподписанный сертификат"
	@echo "  $(YELLOW)make logs$(NC)         - Показать логи"
	@echo ""
	@echo "$(GREEN)Команды для сборки (PyInstaller):$(NC)"
	@echo ""
	@echo "  $(YELLOW)make build$(NC)         - Собрать исполняемый файл для текущей ОС"
	@echo "  $(YELLOW)make build-linux$(NC)   - Собрать исполняемый файл для Linux"
	@echo "  $(YELLOW)make build-windows$(NC) - Собрать исполняемый файл для Windows"
	@echo "  $(YELLOW)make build-all$(NC)     - Собрать для всех платформ"
	@echo "  $(YELLOW)make package-linux$(NC) - Создать tar.gz пакет для Linux"
	@echo "  $(YELLOW)make package-windows$(NC) - Создать zip пакет для Windows"
	@echo "  $(YELLOW)make release$(NC)       - Полный цикл релиза (build + package)"
	@echo "  $(YELLOW)make clean-build$(NC)   - Очистить артефакты сборки"
	@echo ""
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
	@if command -v pip3 >/dev/null 2>&1; then \
		pip3 install -q requests cryptography 2>/dev/null || pip3 install requests cryptography; \
	elif command -v pip >/dev/null 2>&1; then \
		pip install -q requests cryptography 2>/dev/null || pip install requests cryptography; \
	elif command -v python3 >/dev/null 2>&1; then \
		if python3 -m pip --version >/dev/null 2>&1; then \
			python3 -m pip install -q requests cryptography 2>/dev/null || python3 -m pip install requests cryptography; \
		else \
			echo "$(RED)✗ pip не установлен. Выполните:$(NC)"; \
			echo "  $(CYAN)sudo apt-get update && sudo apt-get install -y python3-pip$(NC)"; \
			echo "  или"; \
			echo "  $(CYAN)curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py$(NC)"; \
			exit 1; \
		fi; \
	elif command -v python >/dev/null 2>&1; then \
		if python -m pip --version >/dev/null 2>&1; then \
			python -m pip install -q requests cryptography 2>/dev/null || python -m pip install requests cryptography; \
		else \
			echo "$(RED)✗ pip не установлен. Выполните:$(NC)"; \
			echo "  $(CYAN)sudo apt-get update && sudo apt-get install -y python3-pip$(NC)"; \
			exit 1; \
		fi; \
	else \
		echo "$(RED)✗ Python не найден. Установите Python 3:$(NC)"; \
		echo "  $(CYAN)sudo apt-get update && sudo apt-get install -y python3 python3-pip$(NC)"; \
		exit 1; \
	fi
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
	@printf "Вы уверены? Это удалит все файлы и настройки [y/N]: "; \
	read REPLY; \
	case "$$REPLY" in \
		[Yy]* ) \
			$(MAKE) remove-service; \
			$(MAKE) remove-cron; \
			$(MAKE) remove-files; \
			echo ""; \
			echo "$(GREEN)✓ Удаление завершено$(NC)"; \
			;; \
		* ) \
			echo "$(YELLOW)Удаление отменено$(NC)"; \
			;; \
	esac

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
	@printf "Удалить конфигурацию $(CONFIG_FILE)? [y/N]: "; \
	read REPLY; \
	case "$$REPLY" in \
		[Yy]* ) \
			rm -f $(CONFIG_FILE); \
			echo "$(GREEN)✓ Конфигурация удалена$(NC)"; \
			;; \
		* ) \
			echo "$(YELLOW)Конфигурация сохранена$(NC)"; \
			;; \
	esac
	@echo ""
	@printf "Удалить логи? [y/N]: "; \
	read REPLY; \
	case "$$REPLY" in \
		[Yy]* ) \
			rm -f $(LOG_FILE) $(CRON_LOG); \
			echo "$(GREEN)✓ Логи удалены$(NC)"; \
			;; \
		* ) \
			echo "$(YELLOW)Логи сохранены$(NC)"; \
			;; \
	esac

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
		echo "$(YELLOW)Совет: Скопируйте config.json.example в $(CONFIG_FILE)$(NC)"; \
		echo "  $(CYAN)sudo cp config.json.example $(CONFIG_FILE)$(NC)"; \
		echo "  $(CYAN)sudo chmod 644 $(CONFIG_FILE)$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Конфигурация найдена$(NC)"
	@if [ ! -r "$(CONFIG_FILE)" ]; then \
		echo "$(RED)✗ Нет прав для чтения: $(CONFIG_FILE)$(NC)"; \
		echo "$(YELLOW)Решение: Запустите команду с sudo:$(NC)"; \
		echo "  $(CYAN)sudo make check-config$(NC)"; \
		exit 1; \
	fi
	@echo ""
	@$(PYTHON) -c "import json; print(json.dumps(json.load(open('$(CONFIG_FILE)')), indent=2, ensure_ascii=False))" 2>&1 || \
		(echo "$(RED)✗ Ошибка: Неверный формат JSON$(NC)"; \
		 echo "$(YELLOW)Подробности:$(NC)"; \
		 $(PYTHON) -c "import json; json.load(open('$(CONFIG_FILE)'))" 2>&1 | head -5; \
		 exit 1)
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

# ==============================================================================
# Сборка исполняемых файлов с PyInstaller
# ==============================================================================

# Установка PyInstaller
install-pyinstaller:
	@echo "$(YELLOW)→ Установка PyInstaller...$(NC)"
	@if command -v pip3 >/dev/null 2>&1; then \
		pip3 install --upgrade pyinstaller; \
	elif command -v pip >/dev/null 2>&1; then \
		pip install --upgrade pyinstaller; \
	else \
		echo "$(RED)✗ pip не найден. Установите pip сначала.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ PyInstaller установлен$(NC)"

# Сборка для текущей ОС
build:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Сборка исполняемого файла для текущей ОС                     ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@if ! command -v $(PYINSTALLER) >/dev/null 2>&1; then \
		echo "$(YELLOW)PyInstaller не найден. Установка...$(NC)"; \
		$(MAKE) install-pyinstaller; \
	fi
	@echo "$(YELLOW)→ Компиляция $(SCRIPT_NAME) в исполняемый файл...$(NC)"
	@$(PYINSTALLER) --onefile \
		--name $(APP_NAME) \
		--add-data "README.md:." \
		--hidden-import requests \
		--hidden-import certbot \
		--hidden-import cryptography \
		--collect-all certbot \
		--noconfirm \
		$(SCRIPT_NAME)
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  ✓ Сборка завершена успешно!                                   ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Исполняемый файл:$(NC)"
	@ls -lh $(DIST_DIR)/$(APP_NAME) 2>/dev/null || dir $(DIST_DIR)\$(APP_NAME).exe 2>/dev/null || echo "  $(DIST_DIR)/$(APP_NAME)"
	@echo ""
	@echo "$(YELLOW)Размер файла:$(NC)"
	@du -h $(DIST_DIR)/$(APP_NAME) 2>/dev/null || echo "  ~40-60 MB (включая Python runtime и все библиотеки)"
	@echo ""
	@echo "$(YELLOW)Примечание:$(NC)"
	@echo "  • Исполняемый файл содержит весь Python runtime"
	@echo "  • Certbot все равно должен быть установлен в системе"
	@echo "  • Запускайте с sudo для работы с сертификатами"

# Сборка для Linux
build-linux:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Сборка исполняемого файла для Linux                          ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@UNAME=$$(uname -s 2>/dev/null || echo "Unknown"); \
	if [ "$$UNAME" != "Linux" ]; then \
		echo "$(RED)ВНИМАНИЕ: Сборка на $$UNAME, но целевая ОС - Linux$(NC)"; \
		echo "$(YELLOW)Рекомендуется собирать на Linux для лучшей совместимости$(NC)"; \
		echo ""; \
	fi
	@if ! command -v $(PYINSTALLER) >/dev/null 2>&1; then \
		echo "$(YELLOW)PyInstaller не найден. Установка...$(NC)"; \
		$(MAKE) install-pyinstaller; \
	fi
	@echo "$(YELLOW)→ Компиляция для Linux (x86_64)...$(NC)"
	@$(PYINSTALLER) --onefile \
		--name $(APP_NAME) \
		--add-data "README.md:." \
		--hidden-import requests \
		--hidden-import certbot \
		--hidden-import cryptography \
		--collect-all certbot \
		--target-arch x86_64 \
		--noconfirm \
		$(SCRIPT_NAME)
	@echo ""
	@echo "$(GREEN)✓ Сборка для Linux завершена!$(NC)"
	@echo ""
	@echo "$(YELLOW)Исполняемый файл:$(NC) $(DIST_DIR)/$(APP_NAME)"
	@file $(DIST_DIR)/$(APP_NAME) 2>/dev/null || echo "  ELF 64-bit executable"
	@ls -lh $(DIST_DIR)/$(APP_NAME) 2>/dev/null || echo ""

# Сборка для Windows
build-windows:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Сборка исполняемого файла для Windows                        ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@UNAME=$$(uname -s 2>/dev/null || echo "Windows"); \
	SEPARATOR=";"; \
	if [ "$$UNAME" = "Linux" ] || [ "$$UNAME" = "Darwin" ]; then \
		echo "$(RED)ВНИМАНИЕ: Кросс-компиляция для Windows из $$UNAME$(NC)"; \
		echo "$(YELLOW)Используем разделитель ':' вместо ';' для PyInstaller$(NC)"; \
		echo "$(YELLOW)Рекомендуется: собирайте на нативной Windows для лучших результатов$(NC)"; \
		echo ""; \
		SEPARATOR=":"; \
	fi; \
	if ! command -v $(PYINSTALLER) >/dev/null 2>&1; then \
		echo "$(YELLOW)PyInstaller не найден. Установка...$(NC)"; \
		$(MAKE) install-pyinstaller; \
	fi; \
	echo "$(YELLOW)→ Компиляция для Windows (x86_64) с разделителем $$SEPARATOR...$(NC)"; \
	$(PYINSTALLER) --onefile \
		--name $(APP_NAME) \
		--add-data "README.md$${SEPARATOR}." \
		--hidden-import requests \
		--hidden-import certbot \
		--hidden-import cryptography \
		--collect-all certbot \
		--icon NONE \
		--noconfirm \
		$(SCRIPT_NAME)
	@echo ""
	@echo "$(GREEN)✓ Сборка для Windows завершена!$(NC)"
	@echo ""
	@echo "$(YELLOW)Исполняемый файл:$(NC) $(DIST_DIR)/$(APP_NAME).exe"
	@ls -lh $(DIST_DIR)/$(APP_NAME).exe 2>/dev/null || dir $(DIST_DIR)\$(APP_NAME).exe 2>/dev/null || echo ""

# Сборка для всех платформ
build-all:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Сборка для всех платформ                                      ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(RED)⚠️  ВНИМАНИЕ: Кросс-компиляция Windows из Linux НЕ РАБОТАЕТ!$(NC)"
	@echo "$(YELLOW)→ PyInstaller не может создать .exe файл на Linux/macOS$(NC)"
	@echo "$(YELLOW)→ Для Windows сборки используйте нативную Windows систему$(NC)"
	@echo ""
	@echo "$(YELLOW)Рекомендации:$(NC)"
	@echo "  • Собирать Linux версию на Linux (работает ✓)"
	@echo "  • Собирать Windows версию на Windows (обязательно!)"
	@echo "  • Использовать GitHub Actions для автоматической сборки"
	@echo ""
	@$(MAKE) build-linux
	@echo ""
	@UNAME=$$(uname -s 2>/dev/null || echo "Windows"); \
	if [ "$$UNAME" != "Windows" ] && [ "$$UNAME" != "MINGW"* ] && [ "$$UNAME" != "MSYS"* ]; then \
		echo "$(YELLOW)Пропускаем Windows сборку (текущая ОС: $$UNAME)$(NC)"; \
		echo "$(YELLOW)Используйте Windows для создания .exe файла$(NC)"; \
	else \
		$(MAKE) build-windows; \
	fi
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  ✓ Сборка завершена!                                           ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Файлы в директории $(DIST_DIR)/:$(NC)"
	@ls -lh $(DIST_DIR)/ 2>/dev/null || dir $(DIST_DIR) 2>/dev/null || echo "  Проверьте $(DIST_DIR)/"

# Создание пакета для Linux (tar.gz)
package-linux: build-linux
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Создание пакета для Linux                                     ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)→ Подготовка файлов...$(NC)"
	@mkdir -p $(DIST_DIR)/package
	@cp $(DIST_DIR)/$(APP_NAME) $(DIST_DIR)/package/
	@cp README.md $(DIST_DIR)/package/ 2>/dev/null || true
	@cp -r systemd $(DIST_DIR)/package/ 2>/dev/null || true
	@if [ -f "config.json.example" ]; then \
		cp config.json.example $(DIST_DIR)/package/; \
	fi
	@echo "$(YELLOW)→ Создание архива...$(NC)"
	@cd $(DIST_DIR)/package && tar -czf ../$(APP_NAME)-linux-x86_64.tar.gz *
	@rm -rf $(DIST_DIR)/package
	@echo ""
	@echo "$(GREEN)✓ Пакет создан:$(NC) $(DIST_DIR)/$(APP_NAME)-linux-x86_64.tar.gz"
	@ls -lh $(DIST_DIR)/$(APP_NAME)-linux-x86_64.tar.gz
	@echo ""
	@echo "$(YELLOW)Содержимое пакета:$(NC)"
	@tar -tzf $(DIST_DIR)/$(APP_NAME)-linux-x86_64.tar.gz | head -10

# Создание пакета для Windows (zip)
package-windows: build-windows
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Создание пакета для Windows                                   ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@if [ ! -f "$(DIST_DIR)/$(APP_NAME).exe" ]; then \
		echo "$(RED)✗ Ошибка: Файл $(APP_NAME).exe не найден$(NC)"; \
		echo "$(YELLOW)⚠️  Кросс-компиляция для Windows из Linux/macOS не создает .exe файл!$(NC)"; \
		echo "$(YELLOW)→ Используйте нативную Windows систему для сборки Windows версии$(NC)"; \
		echo ""; \
		exit 1; \
	fi
	@echo "$(YELLOW)→ Подготовка файлов...$(NC)"
	@mkdir -p $(DIST_DIR)/package
	@cp $(DIST_DIR)/$(APP_NAME).exe $(DIST_DIR)/package/
	@cp README.md $(DIST_DIR)/package/ 2>/dev/null || true
	@if [ -f "config.json.example" ]; then cp config.json.example $(DIST_DIR)/package/; fi
	@echo "$(YELLOW)→ Создание архива (tar.gz)...$(NC)"
	@cd $(DIST_DIR)/package && tar -czf ../$(APP_NAME)-windows-x86_64.tar.gz *
	@rm -rf $(DIST_DIR)/package
	@echo ""
	@echo "$(GREEN)✓ Пакет создан:$(NC) $(DIST_DIR)/$(APP_NAME)-windows-x86_64.tar.gz"
	@ls -lh $(DIST_DIR)/$(APP_NAME)-windows-x86_64.tar.gz
	@echo ""
	@echo "$(YELLOW)Содержимое пакета:$(NC)"
	@tar -tzf $(DIST_DIR)/$(APP_NAME)-windows-x86_64.tar.gz | head -10

# Полный цикл релиза
release:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  ПОЛНЫЙ ЦИКЛ РЕЛИЗА                                            ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@$(MAKE) clean-build
	@$(MAKE) install-pyinstaller
	@$(MAKE) build-all
	@$(MAKE) package-linux
	@$(MAKE) package-windows
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  ✓ РЕЛИЗ ГОТОВ!                                                ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Артефакты релиза:$(NC)"
	@ls -lh $(DIST_DIR)/*.tar.gz $(DIST_DIR)/*.zip 2>/dev/null || dir $(DIST_DIR)\*.zip 2>/dev/null || echo "  Проверьте $(DIST_DIR)/"
	@echo ""
	@echo "$(YELLOW)Контрольные суммы SHA256:$(NC)"
	@cd $(DIST_DIR) && sha256sum *.tar.gz *.zip 2>/dev/null || \
		cd $(DIST_DIR) && certutil -hashfile $(APP_NAME)-windows-x86_64.zip SHA256 2>/dev/null || \
		echo "  Используйте sha256sum или certutil для проверки контрольных сумм"
	@echo ""
	@echo "$(YELLOW)Следующие шаги:$(NC)"
	@echo "  1. Протестируйте исполняемые файлы"
	@echo "  2. Создайте GitHub Release"
	@echo "  3. Загрузите пакеты как Assets"

# Тестирование собранного файла
test-build:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Тестирование собранного файла                                 ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@if [ -f "$(DIST_DIR)/$(APP_NAME)" ]; then \
		echo "$(YELLOW)→ Тестирование Linux версии...$(NC)"; \
		chmod +x $(DIST_DIR)/$(APP_NAME); \
		$(DIST_DIR)/$(APP_NAME) --help; \
		echo ""; \
		echo "$(GREEN)✓ Linux версия работает$(NC)"; \
	elif [ -f "$(DIST_DIR)/$(APP_NAME).exe" ]; then \
		echo "$(YELLOW)→ Тестирование Windows версии...$(NC)"; \
		$(DIST_DIR)/$(APP_NAME).exe --help; \
		echo ""; \
		echo "$(GREEN)✓ Windows версия работает$(NC)"; \
	else \
		echo "$(RED)✗ Исполняемый файл не найден$(NC)"; \
		echo "$(YELLOW)Запустите 'make build' сначала$(NC)"; \
		exit 1; \
	fi

# Очистка артефактов сборки
clean-build:
	@echo "$(YELLOW)→ Очистка артефактов сборки...$(NC)"
	@rm -rf $(BUILD_DIR_PY) $(DIST_DIR) $(SPEC_FILE) __pycache__ *.pyc
	@echo "$(GREEN)✓ Артефакты сборки удалены$(NC)"

# Информация о среде сборки
build-info:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Информация о среде сборки                                     ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Система:$(NC)"
	@echo "  ОС: $$(uname -s 2>/dev/null || echo 'Windows')"
	@echo "  Архитектура: $$(uname -m 2>/dev/null || echo 'x86_64')"
	@echo "  Ядро: $$(uname -r 2>/dev/null || echo 'N/A')"
	@echo ""
	@echo "$(YELLOW)Python:$(NC)"
	@echo "  Версия: $$($(PYTHON) --version 2>&1)"
	@echo "  Путь: $$(which $(PYTHON) 2>/dev/null || where $(PYTHON) 2>/dev/null || echo 'N/A')"
	@echo ""
	@echo "$(YELLOW)PyInstaller:$(NC)"
	@if command -v $(PYINSTALLER) >/dev/null 2>&1; then \
		echo "  Версия: $$($(PYINSTALLER) --version 2>&1)"; \
		echo "  Путь: $$(which $(PYINSTALLER) 2>/dev/null || where $(PYINSTALLER) 2>/dev/null)"; \
		echo "  $(GREEN)✓ Установлен$(NC)"; \
	else \
		echo "  $(RED)✗ Не установлен$(NC)"; \
		echo "  Установите: make install-pyinstaller"; \
	fi
	@echo ""
	@echo "$(YELLOW)Конфигурация сборки:$(NC)"
	@echo "  Исходный файл: $(SCRIPT_NAME)"
	@echo "  Название приложения: $(APP_NAME)"
	@echo "  Директория сборки: $(DIST_DIR)/"
	@echo ""

# По умолчанию показываем помощь
.DEFAULT_GOAL := help
