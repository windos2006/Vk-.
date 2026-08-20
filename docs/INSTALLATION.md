# Установка и настройка VK Desktop

## Быстрый старт

### Системные требования

- **ОС:** Windows 7, 8, 10, 11
- **Python:** 3.8 или выше
- **VLC:** Портабельная или установленная версия
- **Экранный диктор:** NVDA, JAWS или встроенный Narrator

### Шаг 1: Установка Python

1. Скачайте Python с [python.org](https://www.python.org/)
2. Запустите установщик
3. **Важно:** Установите флажок "Add Python to PATH"
4. Нажмите "Install Now"

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/windos2006/Vk-.git
cd Vk-.
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Установка VLC

#### Вариант 1: Портабельная версия (Рекомендуется)

1. Скачайте портабельную версию VLC с [официального сайта](https://www.videolan.org/)
2. Распакуйте архив в папку `vlc/` в корне проекта
3. Структура должна быть:
   ```
   Vk-./
   ├── vlc/
   │   ├── vlc.exe
   │   ├── libvlc.dll
   │   └── ...
   ```

#### Вариант 2: Установленная версия

Если VLC установлен системно, приложение найдет его автоматически.

### Шаг 5: Запуск приложения

```bash
python main.py
```

## Конфигурация

### Файл конфигурации

Создайте файл `config/config.ini` со следующим содержимым:

```ini
[VK]
# Токен доступа VK API (будет запрашиваться при первом запуске)
token =
user_id =

[AUDIO]
# Основная громкость (0-100)
master_volume = 100

# Громкость категорий
messages_volume = 100
notifications_volume = 100
actions_volume = 70
media_volume = 80
profile_volume = 75
errors_volume = 100

# Включенные категории
enable_messages = true
enable_notifications = true
enable_actions = true
enable_media = true
enable_profile = true
enable_errors = true

[UI]
# Тема интерфейса (light, dark)
theme = dark

# Язык (ru, en)
language = ru

# Размер шрифта (9, 10, 11, 12)
font_size = 11
```

### Переменные окружения

Создайте файл `.env` (опционально):

```
VK_API_VERSION=5.131
DEBUG=False
LOG_LEVEL=INFO
```

## Аутентификация

### Получение токена VK API

1. Перейдите на [vk.com/dev](https://vk.com/dev)
2. Нажмите "Мои приложения"
3. Создайте новое приложение (Standalone)
4. Скопируйте ID приложения
5. При первом запуске приложение попросит вас авторизоваться
6. Следуйте инструкциям на э��ране

## Структура папок

```
Vk-./
├── main.py                 # Точка входа приложения
├── requirements.txt        # Зависимости
├── LICENSE                 # Лицензия MIT
├── README.md              # Основная документация
├── .gitignore             # Файлы для игнорирования git
├── .env                   # Переменные окружения (не коммитить)
│
├── config/
│   ├── config.ini         # Основная конфигурация
│   └── sound_config.json  # Конфигурация звуков
│
├── src/                   # Исходный код
│   ├── __init__.py
│   ├── api/               # VK API
│   │   ├── __init__.py
│   │   ├── vk_client.py   # VK API клиент
│   │   └── methods.py     # Методы API
│   │
│   ├── ui/                # wxPython интерфейс
│   │   ├── __init__.py
│   │   ├── main_frame.py  # Главное окно
│   │   ├── widgets.py     # Виджеты
│   │   └── dialogs.py     # Диалоги
│   │
│   ├── audio/             # Звуковая система
│   │   ├── __init__.py
│   │   ├── sound_events.py
│   │   ├── sound_manager.py
│   │   └── sound_config.py
│   │
│   ├── media/             # Работа с медиа
│   │   ├── __init__.py
│   │   ├── vlc_player.py  # VLC плеер
│   │   └── playlist.py    # Плейлист
│   │
│   ├── auth/              # Аутентификация
│   │   ├── __init__.py
│   │   ├── auth_manager.py
│   │   └── token_storage.py
│   │
│   └── utils/             # Вспомогательные функции
│       ├── __init__.py
│       ├── logger.py      # Логирование
│       ├── config.py      # Работа с конфигом
│       └── helpers.py     # Помощники
│
├── sounds/                # Звуковые файлы
│   ├── message_received.wav
│   ├── message_sent.wav
│   └── ... (остальные звуки)
│
├── docs/                  # Документация
│   ├── README.md         # Установка и быстрый старт
│   ├── AUDIO_SYSTEM.md   # Документация звуковой системы
│   ├── API.md            # Документация VK API
│   ├── ARCHITECTURE.md   # Архитектура приложения
│   └── DEVELOPER_GUIDE.md # Руководство разработчика
│
├── tests/                 # Тесты
│   ├── __init__.py
│   ├── test_audio.py      # Тесты звуковой системы
│   ├── test_api.py        # Тесты API
│   └── test_ui.py         # Тесты UI
│
└── vlc/                   # Портабельная версия VLC (опционально)
    ├── vlc.exe
    ├── libvlc.dll
    └── ... (остальные файлы VLC)
```

## Проверка установки

### Проверка Python

```bash
python --version
```

Должно вывести: `Python 3.x.x`

### Проверка зависимостей

```bash
pip list
```

Должны быть установлены все пакеты из `requirements.txt`

### Проверка VLC

```bash
# Портабельная версия
./vlc/vlc.exe --version

# Или системная версия
vlc --version
```

### Проверка NVDA/JAWS

1. Запустите NVDA или JAWS
2. Запустите приложение VK Desktop
3. Вы должны услышать голос скрин-ридера

## Решение проблем при установке

### Проблема: Python не найден

**Решение:**
1. Переустановите Python
2. Убедитесь, что выбрана опция "Add Python to PATH"
3. Перезагру��ите компьютер

### Проблема: Не удается установить зависимости

**Решение:**
```bash
# Обновите pip
python -m pip install --upgrade pip

# Повторите установку
pip install -r requirements.txt
```

### Проблема: VLC не найден

**Решение:**
1. Скачайте портабельную версию VLC
2. Распакуйте в папку `vlc/`
3. Убедитесь, что путь правильный

### Проблема: Приложение не запускается

**Решение:**
```bash
# Запустите с подробным логированием
python main.py --debug

# Проверьте логи в папке logs/
```

## Обновление приложения

### Обновление исходного кода

```bash
git pull origin develop
```

### Обновление зависимостей

```bash
pip install -r requirements.txt --upgrade
```

## Удаление приложения

```bash
# Удалите зависимости Python (опционально)
pip uninstall -r requirements.txt -y

# Удалите папку проекта
rmdir /s /q Vk-.
```

## Получение помощи

- 📖 Документация: https://github.com/windos2006/Vk-./docs
- 🐛 Баги: https://github.com/windos2006/Vk-./issues
- 💬 Обсуждения: https://github.com/windos2006/Vk-./discussions
