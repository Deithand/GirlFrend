#!/bin/bash

# Telegram Girlfriend Bot - Start Script
# Красивый запуск бота с проверками

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция для вывода цветных сообщений
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Заголовок
clear
print_color "$MAGENTA" "╔══════════════════════════════════════════════════════════════╗"
print_color "$MAGENTA" "║         Telegram Girlfriend Bot - Launcher v1.0              ║"
print_color "$MAGENTA" "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Проверка наличия Python
print_color "$CYAN" "→ Проверка Python..."
if ! command -v python3 &> /dev/null; then
    print_color "$RED" "✗ Python 3 не найден! Установите Python 3.8 или выше."
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_color "$GREEN" "✓ Python $PYTHON_VERSION найден"
echo ""

# Проверка наличия .env файла
print_color "$CYAN" "→ Проверка конфигурации..."
if [ ! -f .env ]; then
    print_color "$YELLOW" "⚠ Файл .env не найден!"
    print_color "$YELLOW" "  Создайте .env на основе .env.example и заполните переменные"
    echo ""
    print_color "$CYAN" "  Создать .env сейчас? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cp .env.example .env
        print_color "$GREEN" "✓ Файл .env создан"
        print_color "$YELLOW" "  Отредактируйте .env и добавьте ваши API ключи, затем запустите скрипт снова"
        exit 0
    else
        print_color "$RED" "✗ Невозможно продолжить без .env файла"
        exit 1
    fi
fi
print_color "$GREEN" "✓ Файл .env найден"
echo ""

# Проверка виртуального окружения
print_color "$CYAN" "→ Проверка виртуального окружения..."
if [ ! -d "venv" ]; then
    print_color "$YELLOW" "⚠ Виртуальное окружение не найдено"
    print_color "$CYAN" "  Создать виртуальное окружение? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_color "$CYAN" "  Создание виртуального окружения..."
        python3 -m venv venv
        print_color "$GREEN" "✓ Виртуальное окружение создано"
    else
        print_color "$YELLOW" "  Продолжаем без виртуального окружения..."
    fi
else
    print_color "$GREEN" "✓ Виртуальное окружение найдено"
fi
echo ""

# Активация виртуального окружения
if [ -d "venv" ]; then
    print_color "$CYAN" "→ Активация виртуального окружения..."
    source venv/bin/activate
    print_color "$GREEN" "✓ Виртуальное окружение активировано"
    echo ""
fi

# Установка зависимостей
print_color "$CYAN" "→ Проверка зависимостей..."
if [ ! -f "venv/lib/python*/site-packages/telethon/__init__.py" ]; then
    print_color "$YELLOW" "⚠ Зависимости не установлены"
    print_color "$CYAN" "  Установить зависимости? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_color "$CYAN" "  Установка зависимостей..."
        pip install -r requirements.txt
        print_color "$GREEN" "✓ Зависимости установлены"
    else
        print_color "$RED" "✗ Невозможно продолжить без зависимостей"
        exit 1
    fi
else
    print_color "$GREEN" "✓ Зависимости установлены"
fi
echo ""

# Запуск бота
print_color "$GREEN" "╔══════════════════════════════════════════════════════════════╗"
print_color "$GREEN" "║                  Запуск бота...                              ║"
print_color "$GREEN" "╚══════════════════════════════════════════════════════════════╝"
echo ""

python3 bot.py
