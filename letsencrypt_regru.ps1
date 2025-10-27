# ============================================================================
# Скрипт для создания и обновления SSL сертификата Let's Encrypt
# с использованием DNS-валидации через API reg.ru (PowerShell версия)
#
# Автор: Фофанов Дмитрий
# Дата: 27.10.2025
# Описание: PowerShell версия скрипта для Windows окружения
# ============================================================================

<#
.SYNOPSIS
    Автоматизация получения SSL сертификатов Let's Encrypt через DNS-валидацию reg.ru

.DESCRIPTION
    Скрипт позволяет автоматически получать и обновлять SSL сертификаты Let's Encrypt
    для доменов на reg.ru используя DNS-01 challenge через API

.PARAMETER Domain
    Основной домен (например, dfv24.com)

.PARAMETER Email
    Email для уведомлений Let's Encrypt

.PARAMETER RegRuUsername
    Имя пользователя reg.ru

.PARAMETER RegRuPassword
    Пароль reg.ru

.PARAMETER Wildcard
    Создать wildcard сертификат (*.domain.com)

.PARAMETER ConfigFile
    Путь к файлу конфигурации JSON

.EXAMPLE
    .\letsencrypt_regru.ps1 -Domain "dfv24.com" -Email "admin@dfv24.com" -Wildcard
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain = "dfv24.com",
    
    [Parameter(Mandatory=$false)]
    [string]$Email = "admin@dfv24.com",
    
    [Parameter(Mandatory=$false)]
    [string]$RegRuUsername = "",
    
    [Parameter(Mandatory=$false)]
    [string]$RegRuPassword = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Wildcard = $true,
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigFile = ".\config.json",
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false
)

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

$Script:Config = @{
    RegRuApiUrl = "https://api.reg.ru/api/regru2"
    CertbotPath = "certbot"
    LogFile = ".\letsencrypt_regru.log"
    DnsPropagationWait = 60
    DnsCheckAttempts = 10
    DnsCheckInterval = 10
}

# ============================================================================
# ФУНКЦИИ ЛОГИРОВАНИЯ
# ============================================================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "dd.MM.yyyy HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    # Вывод в консоль
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
        "WARNING" { Write-Host $LogMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor Green }
        default { Write-Host $LogMessage }
    }
    
    # Запись в файл
    Add-Content -Path $Script:Config.LogFile -Value $LogMessage
}

# ============================================================================
# ФУНКЦИИ РАБОТЫ С КОНФИГУРАЦИЕЙ
# ============================================================================

function Load-Configuration {
    param([string]$ConfigPath)
    
    Write-Log "Загрузка конфигурации из: $ConfigPath"
    
    if (Test-Path $ConfigPath) {
        try {
            $config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
            
            # Обновляем параметры скрипта из конфигурации
            if ($config.domain) { $Script:Domain = $config.domain }
            if ($config.email) { $Script:Email = $config.email }
            if ($config.regru_username) { $Script:RegRuUsername = $config.regru_username }
            if ($config.regru_password) { $Script:RegRuPassword = $config.regru_password }
            if ($null -ne $config.wildcard) { $Script:Wildcard = $config.wildcard }
            
            Write-Log "Конфигурация успешно загружена" "SUCCESS"
            return $true
        }
        catch {
            Write-Log "Ошибка при загрузке конфигурации: $_" "ERROR"
            return $false
        }
    }
    else {
        Write-Log "Файл конфигурации не найден: $ConfigPath" "WARNING"
        return $false
    }
}

function Create-SampleConfig {
    param([string]$OutputPath = ".\config.json")
    
    $sampleConfig = @{
        regru_username = "your_username"
        regru_password = "your_password"
        domain = "dfv24.com"
        wildcard = $true
        email = "admin@dfv24.com"
        dns_propagation_wait = 60
        dns_check_attempts = 10
        dns_check_interval = 10
    }
    
    $sampleConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath
    Write-Log "Пример конфигурации создан: $OutputPath" "SUCCESS"
}

# ============================================================================
# ФУНКЦИИ РАБОТЫ С REG.RU API
# ============================================================================

function Invoke-RegRuApi {
    param(
        [string]$Method,
        [hashtable]$Params
    )
    
    $url = "$($Script:Config.RegRuApiUrl)/$Method"
    
    # Добавляем учетные данные
    $Params["username"] = $Script:RegRuUsername
    $Params["password"] = $Script:RegRuPassword
    $Params["output_format"] = "json"
    
    Write-Log "Отправка запроса к API: $Method" "DEBUG"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Body $Params -ContentType "application/x-www-form-urlencoded"
        
        if ($response.result -eq "success") {
            Write-Log "Запрос $Method выполнен успешно" "DEBUG"
            return $response
        }
        else {
            $errorMsg = if ($response.error_text) { $response.error_text } else { "Неизвестная ошибка" }
            Write-Log "Ошибка API: $errorMsg" "ERROR"
            throw "API Error: $errorMsg"
        }
    }
    catch {
        Write-Log "Ошибка HTTP запроса: $_" "ERROR"
        throw
    }
}

function Get-DnsRecords {
    param([string]$Domain)
    
    Write-Log "Получение DNS записей для домена: $Domain"
    
    $params = @{
        domain = $Domain
    }
    
    $response = Invoke-RegRuApi -Method "zone/get_resource_records" -Params $params
    
    if ($response.answer -and $response.answer.records) {
        $records = $response.answer.records
        Write-Log "Получено $($records.Count) DNS записей"
        return $records
    }
    else {
        Write-Log "DNS записи не найдены" "WARNING"
        return @()
    }
}

function Add-TxtRecord {
    param(
        [string]$Domain,
        [string]$Subdomain,
        [string]$TxtValue
    )
    
    Write-Log "Добавление TXT записи: $Subdomain.$Domain = $TxtValue"
    
    $params = @{
        domain = $Domain
        subdomain = $Subdomain
        text = $TxtValue
        output_content_type = "plain"
    }
    
    try {
        $null = Invoke-RegRuApi -Method "zone/add_txt" -Params $params
        Write-Log "TXT запись успешно добавлена" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Не удалось добавить TXT запись: $_" "ERROR"
        return $false
    }
}

function Remove-TxtRecord {
    param(
        [string]$Domain,
        [string]$Subdomain,
        [string]$TxtValue
    )
    
    Write-Log "Удаление TXT записи: $Subdomain.$Domain"
    
    # Получаем список записей
    $records = Get-DnsRecords -Domain $Domain
    
    # Ищем нужную TXT запись
    $record = $records | Where-Object {
        $_.rectype -eq "TXT" -and
        $_.subdomain -eq $Subdomain -and
        $_.text -eq $TxtValue
    } | Select-Object -First 1
    
    if (-not $record) {
        Write-Log "TXT запись для удаления не найдена" "WARNING"
        return $false
    }
    
    $params = @{
        domain = $Domain
        record_id = $record.id
    }
    
    try {
        $null = Invoke-RegRuApi -Method "zone/remove_record" -Params $params
        Write-Log "TXT запись успешно удалена" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Не удалось удалить TXT запись: $_" "ERROR"
        return $false
    }
}

# ============================================================================
# ФУНКЦИИ РАБОТЫ С CERTBOT
# ============================================================================

function Test-CertbotInstalled {
    try {
        $version = & certbot --version 2>&1
        Write-Log "Certbot установлен: $version"
        return $true
    }
    catch {
        Write-Log "Certbot не установлен!" "ERROR"
        Write-Log "Установите Certbot: https://certbot.eff.org/instructions" "ERROR"
        return $false
    }
}

function Get-CertificateExpiry {
    param([string]$Domain)
    
    $certPath = Join-Path $env:ProgramData "letsencrypt\live\$Domain\cert.pem"
    
    if (-not (Test-Path $certPath)) {
        Write-Log "Сертификат не найден: $certPath"
        return $null
    }
    
    try {
        # Используем openssl для проверки сертификата
        $expiryText = & openssl x509 -enddate -noout -in $certPath 2>&1
        
        if ($expiryText -match "notAfter=(.+)") {
            $expiryDate = [DateTime]::Parse($matches[1])
            $daysLeft = ($expiryDate - (Get-Date)).Days
            
            Write-Log "Сертификат истекает: $($expiryDate.ToString('yyyy-MM-dd'))"
            Write-Log "Осталось дней: $daysLeft"
            
            return $daysLeft
        }
    }
    catch {
        Write-Log "Ошибка при проверке сертификата: $_" "ERROR"
    }
    
    return $null
}

function Invoke-DnsChallenge {
    param(
        [string]$Domain,
        [string]$ValidationToken
    )
    
    Write-Log "=== DNS Challenge: Добавление TXT записи ===" "INFO"
    
    # Извлекаем поддомен
    $subdomain = "_acme-challenge"
    
    # Добавляем TXT запись
    $success = Add-TxtRecord -Domain $Script:Domain -Subdomain $subdomain -TxtValue $ValidationToken
    
    if ($success) {
        # Ждем распространения DNS
        $waitTime = $Script:Config.DnsPropagationWait
        Write-Log "Ожидание распространения DNS ($waitTime секунд)..."
        Start-Sleep -Seconds $waitTime
        
        Write-Log "DNS валидация готова" "SUCCESS"
        return $true
    }
    
    return $false
}

function Invoke-DnsCleanup {
    param(
        [string]$Domain,
        [string]$ValidationToken
    )
    
    Write-Log "=== DNS Challenge: Удаление TXT записи ===" "INFO"
    
    $subdomain = "_acme-challenge"
    
    return Remove-TxtRecord -Domain $Script:Domain -Subdomain $subdomain -TxtValue $ValidationToken
}

# ============================================================================
# ГЛАВНЫЕ ФУНКЦИИ
# ============================================================================

function Get-Certificate {
    param([string]$Domain, [bool]$WildcardCert)
    
    Write-Log "=== Запрос нового SSL сертификата ===" "INFO"
    
    # Формируем список доменов
    $domains = @($Domain)
    if ($WildcardCert) {
        $domains += "*.$Domain"
    }
    
    $domainArgs = @()
    foreach ($d in $domains) {
        $domainArgs += "-d"
        $domainArgs += $d
    }
    
    Write-Log "Домены для сертификата: $($domains -join ', ')"
    
    # Создаем временные скрипты для хуков
    $authHookScript = Join-Path $env:TEMP "certbot_auth_hook.ps1"
    $cleanupHookScript = Join-Path $env:TEMP "certbot_cleanup_hook.ps1"
    
    # Скрипт для аутентификации
    @"
param([string]`$Domain, [string]`$Token)
# Вызов функции добавления TXT записи
# Здесь должна быть логика работы с API reg.ru
"@ | Set-Content -Path $authHookScript
    
    # Скрипт для очистки
    @"
param([string]`$Domain, [string]`$Token)
# Вызов функции удаления TXT записи
"@ | Set-Content -Path $cleanupHookScript
    
    Write-Log "Примечание: Для полной автоматизации используйте Linux версию скрипта" "WARNING"
    Write-Log "На Windows рекомендуется использовать плагин certbot-dns-регru или выполнить вручную" "WARNING"
    
    # Команда certbot (базовая, требует ручной DNS валидации)
    $certbotArgs = @(
        "certonly",
        "--manual",
        "--preferred-challenges", "dns",
        "--email", $Script:Email,
        "--agree-tos",
        "--manual-public-ip-logging-ok"
    ) + $domainArgs
    
    Write-Log "Запуск certbot..."
    Write-Log "ВАЖНО: Certbot запросит вас добавить TXT записи в DNS" "WARNING"
    Write-Log "Используйте API reg.ru или добавьте записи вручную через панель управления" "WARNING"
    
    try {
        & certbot @certbotArgs
        
        Write-Log "Процесс получения сертификата завершен" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Ошибка при получении сертификата: $_" "ERROR"
        return $false
    }
}

function Update-Certificate {
    Write-Log "=== Обновление SSL сертификата ===" "INFO"
    
    try {
        & certbot renew
        
        Write-Log "Проверка обновления завершена" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Ошибка при обновлении: $_" "ERROR"
        return $false
    }
}

function Show-CertificateInfo {
    param([string]$Domain)
    
    $certPath = Join-Path $env:ProgramData "letsencrypt\live\$Domain\cert.pem"
    
    if (-not (Test-Path $certPath)) {
        Write-Log "Сертификат не найден" "WARNING"
        return
    }
    
    Write-Log ("=" * 60)
    Write-Log "ИНФОРМАЦИЯ О СЕРТИФИКАТЕ"
    Write-Log ("=" * 60)
    
    try {
        $certInfo = & openssl x509 -in $certPath -text -noout
        
        # Выводим основную информацию
        $certInfo -split "`n" | Where-Object {
            $_ -match "Subject:|Issuer:|Not Before|Not After|DNS:"
        } | ForEach-Object {
            Write-Log $_.Trim()
        }
        
        Write-Log ("=" * 60)
        Write-Log "ПУТИ К ФАЙЛАМ СЕРТИФИКАТА:"
        Write-Log "  Сертификат: $certPath"
        Write-Log "  Приватный ключ: $(Join-Path $env:ProgramData "letsencrypt\live\$Domain\privkey.pem")"
        Write-Log "  Цепочка: $(Join-Path $env:ProgramData "letsencrypt\live\$Domain\chain.pem")"
        Write-Log "  Полная цепочка: $(Join-Path $env:ProgramData "letsencrypt\live\$Domain\fullchain.pem")"
        Write-Log ("=" * 60)
    }
    catch {
        Write-Log "Ошибка при чтении сертификата: $_" "ERROR"
    }
}

# ============================================================================
# ОСНОВНАЯ ЛОГИКА
# ============================================================================

function Main {
    Write-Log ("=" * 60)
    Write-Log "СКРИПТ УПРАВЛЕНИЯ SSL СЕРТИФИКАТАМИ LET'S ENCRYPT"
    Write-Log ("=" * 60)
    
    # Проверка прав администратора
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Log "ПРЕДУПРЕЖДЕНИЕ: Скрипт запущен без прав администратора" "WARNING"
        Write-Log "Некоторые операции могут потребовать повышенных прав" "WARNING"
    }
    
    # Загрузка конфигурации
    if ($ConfigFile -and (Test-Path $ConfigFile)) {
        Load-Configuration -ConfigPath $ConfigFile
    }
    
    # Проверка обязательных параметров
    if (-not $Script:RegRuUsername -or -not $Script:RegRuPassword) {
        Write-Log "ОШИБКА: Не указаны учетные данные reg.ru" "ERROR"
        Write-Log "Укажите RegRuUsername и RegRuPassword или создайте файл конфигурации" "ERROR"
        return
    }
    
    # Проверка Certbot
    if (-not (Test-CertbotInstalled)) {
        Write-Log "Установите Certbot и повторите попытку" "ERROR"
        return
    }
    
    # Проверка срока действия сертификата
    $daysLeft = Get-CertificateExpiry -Domain $Script:Domain
    
    if ($null -eq $daysLeft) {
        Write-Log "Сертификат не найден. Требуется создание нового." "INFO"
        $success = Get-Certificate -Domain $Script:Domain -WildcardCert $Script:Wildcard
    }
    elseif ($daysLeft -lt 30) {
        Write-Log "Сертификат истекает через $daysLeft дней. Требуется обновление!" "WARNING"
        $success = Update-Certificate
    }
    else {
        Write-Log "Сертификат действителен ($daysLeft дней)" "SUCCESS"
        $success = $true
    }
    
    if ($success) {
        Show-CertificateInfo -Domain $Script:Domain
    }
    
    Write-Log ("=" * 60)
    Write-Log "Скрипт завершен"
    Write-Log ("=" * 60)
}

# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

# Запуск основной функции
Main
