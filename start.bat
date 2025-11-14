@echo off
REM Telegram Girlfriend Bot - Start Script for Windows
REM Красивый запуск бота с проверками

chcp 65001 >nul
title Telegram Girlfriend Bot Launcher

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         Telegram Girlfriend Bot - Launcher v1.0              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Проверка наличия Python
echo → Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python не найден! Установите Python 3.8 или выше.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% найден
echo.

REM Проверка наличия .env файла
echo → Проверка конфигурации...
if not exist .env (
    echo ⚠ Файл .env не найден!
    echo   Создайте .env на основе .env.example и заполните переменные
    echo.
    set /p response="  Создать .env сейчас? (y/n): "
    if /i "%response%"=="y" (
        copy .env.example .env
        echo ✓ Файл .env создан
        echo   Отредактируйте .env и добавьте ваши API ключи, затем запустите скрипт снова
        pause
        exit /b 0
    ) else (
        echo ✗ Невозможно продолжить без .env файла
        pause
        exit /b 1
    )
)
echo ✓ Файл .env найден
echo.

REM Проверка виртуального окружения
echo → Проверка виртуального окружения...
if not exist venv (
    echo ⚠ Виртуальное окружение не найдено
    set /p response="  Создать виртуальное окружение? (y/n): "
    if /i "%response%"=="y" (
        echo   Создание виртуального окружения...
        python -m venv venv
        echo ✓ Виртуальное окружение создано
    ) else (
        echo   Продолжаем без виртуального окружения...
    )
) else (
    echo ✓ Виртуальное окружение найдено
)
echo.

REM Активация виртуального окружения
if exist venv (
    echo → Активация виртуального окружения...
    call venv\Scripts\activate.bat
    echo ✓ Виртуальное окружение активировано
    echo.
)

REM Установка зависимостей
echo → Проверка зависимостей...
python -c "import telethon" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ Зависимости не установлены
    set /p response="  Установить зависимости? (y/n): "
    if /i "%response%"=="y" (
        echo   Установка зависимостей...
        pip install -r requirements.txt
        echo ✓ Зависимости установлены
    ) else (
        echo ✗ Невозможно продолжить без зависимостей
        pause
        exit /b 1
    )
) else (
    echo ✓ Зависимости установлены
)
echo.

REM Запуск бота
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  Запуск бота...                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

python bot.py

pause
