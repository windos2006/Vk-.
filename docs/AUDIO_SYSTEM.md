# Документация по системе звуковых событий VK Desktop

## Описание

Система звуковых событий предоставляет полнофункциональную поддержку уведомлений звуком для всех действий в приложении VK Desktop. Это критически важная функция для пользователей со скрин-ридерами (NVDA, JAWS), которым необходимо слышать все события, происходящие в приложении.

## Архитектура системы

### Основные компоненты

```
┌─────────────────────────────────────────────────────┐
│         Приложение (Главный поток)                 │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         SoundManager (Менеджер звуков)              │
│  - Управление звуками                              │
│  - Очередь событий                                 │
│  - Расчет громкости                                │
│  - Кэширование звуков                              │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│      Поток воспроизведения (Асинхронный)           │
│  - Очередь событий с приоритетами                  │
│  - Воспроизведение звуков через VLC                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            VLC Media Player                        │
│  - Воспроизведение аудио файлов                    │
│  - Контроль громкости                              │
│  - Управление плейлистом                           │
└─────────────────────────────────────────────────────┘
```

## Типы событий

### Категория: Сообщения и чаты

| Событие | Описание | Файл звука | Громкость |
|---------|---------|------------|----------|
| `MESSAGE_RECEIVED` | Получено новое сообщение | `message_received.wav` | 100% |
| `MESSAGE_SENT` | Сообщение отправлено | `message_sent.wav` | 80% |
| `USER_TYPING` | Пользователь начал печатать | `user_typing.wav` | 60% |
| `USER_STOPPED_TYPING` | Пользователь перестал печатать | `user_stopped_typing.wav` | 60% |
| `GROUP_TYPING` | Кто-то печатает в группе/беседе | `group_typing.wav` | 70% |

### Категория: Уведомления

| Событие | Описание | Файл звука | Громкость |
|---------|---------|------------|----------|
| `FRIEND_REQUEST` | Получена заявка в друзья | `friend_request.wav` | 100% |
| `FRIEND_ACCEPTED` | Заявка в друзья принята | `friend_accepted.wav` | 90% |
| `FRIEND_REMOVED` | Друг удален | `friend_removed.wav` | 80% |
| `LIKE_RECEIVED` | Получен лайк | `like_received.wav` | 85% |
| `WALL_POST_COMMENT` | Комментарий к посту на стене | `wall_post_comment.wav` | 90% |
| `MENTION` | Упоминание пользователя | `mention.wav` | 100% |

### Категория: Действия и системные события

| Событие | Описание | Файл звука | Громкость |
|---------|---------|------------|----------|
| `BUTTON_CLICK` | Нажатие кнопки | `button_click.wav` | 50% |
| `MENU_OPEN` | Открытие меню | `menu_open.wav` | 60% |
| `MENU_CLOSE` | Закрытие меню | `menu_close.wav` | 60% |
| `NOTIFICATION_ALERT` | Общее оповещение | `notification_alert.wav` | 100% |
| `LOADING` | Начало загрузки данных | `loading.wav` | 70% |
| `LOADED` | Завершение загрузки данных | `loaded.wav` | 80% |

### Категория: Музыка и медиа

| Событие | Описание | Файл звука | Громкость |
|---------|---------|------------|----------|
| `AUDIO_PLAY` | Начало воспроизведения | `audio_play.wav` | 70% |
| `AUDIO_PAUSE` | Пауза | `audio_pause.wav` | 70% |
| `AUDIO_STOP` | Остановка | `audio_stop.wav` | 70% |
| `AUDIO_NEXT` | Переход к следующему треку | `audio_next.wav` | 75% |
| `AUDIO_PREVIOUS` | Переход к предыдущему треку | `audio_previous.wav` | 75% |

### Категория: Профиль и статус

| Событие | Описание | Файл звука | Громкость |
|---------|---------|------------|----------|
| `PROFILE_UPDATED` | Профиль обновлен | `profile_updated.wav` | 85% |
| `STATUS_CHANGED` | Статус изменен | `status_changed.wav` | 80% |
| `ONLINE` | Пользователь онлайн | `online.wav` | 75% |
| `OFFLINE` | Пользователь офлайн | `offline.wav` | 75% |

### Категория: Ошибки и предупреждения

| Событие | Описание | Файл звука | Громкость |
|---------|---------|------------|----------|
| `ERROR` | Ошибка в приложении | `error.wav` | 100% |
| `WARNING` | Предупреждение | `warning.wav` | 95% |
| `SUCCESS` | Успешное выполнение операции | `success.wav` | 90% |

## Использование

### Базовое использование

```python
from src.audio.sound_manager import SoundManager
from src.audio.sound_events import AudioEvent

# Инициализация менеджера звуков
manager = SoundManager()

# Воспроизведение простого события
manager.play_event(AudioEvent.MESSAGE_RECEIVED)

# Воспроизведение события с дополнительной информацией
manager.play_event(
    AudioEvent.MESSAGE_RECEIVED,
    user_name="Иван",
    volume=100,
    priority=5
)

# Завершение работы
manager.shutdown()
```

### Управление громкостью

```python
from src.audio.sound_manager import SoundManager
from src.audio.sound_events import SoundEventCategory

manager = SoundManager()

# Установка общей громкости
manager.set_master_volume(80)

# Установка громкости для категории сообщений
manager.set_category_volume(SoundEventCategory.MESSAGES, 100)

# Установка громкости для категории уведомлений
manager.set_category_volume(SoundEventCategory.NOTIFICATIONS, 90)
```

### Управление категориями событий

```python
from src.audio.sound_manager import SoundManager
from src.audio.sound_events import SoundEventCategory

manager = SoundManager()

# Отключение звуков для категории (например, отключить музыку)
manager.disable_category(SoundEventCategory.MEDIA)

# Включение звуков для категории
manager.enable_category(SoundEventCategory.MEDIA)

# Отключение всех уведомлений
manager.disable_category(SoundEventCategory.NOTIFICATIONS)
```

### Очистка очереди

```python
manager = SoundManager()

# Отменить все ожидающие звуки
manager.clear_queue()
```

## Расчет громкости

Финальная громкость рассчитывается по следующей формуле:

```
Финальная громкость = (Громкость события × Громкость категории × Обща громкость) / 1000000 × 100
```

**Пример:**
- Громкость события: 100
- Громкость категории: 100
- Обща громкость: 80
- **Результат:** (100 × 100 × 80) / 1000000 × 100 = 80%

## Структура файлов

```
src/audio/
├── __init__.py              # Инициализация пакета
├── sound_events.py          # Определение типов событий
├── sound_manager.py         # Менеджер звуков и воспроизведения
├── sound_config.py          # Управление конфигурацией
└── README.md               # Документация (этот файл)

sounds/                     # Папка со звуковыми файлами
├── message_received.wav
├── message_sent.wav
├── user_typing.wav
├── user_stopped_typing.wav
├── group_typing.wav
├── friend_request.wav
├── friend_accepted.wav
├── friend_removed.wav
├── like_received.wav
├── wall_post_comment.wav
├── mention.wav
├── button_click.wav
├── menu_open.wav
├── menu_close.wav
├── notification_alert.wav
├── loading.wav
├── loaded.wav
├── audio_play.wav
├── audio_pause.wav
├── audio_stop.wav
├── audio_next.wav
├── audio_previous.wav
├── profile_updated.wav
├── status_changed.wav
├── online.wav
├── offline.wav
├── error.wav
├── warning.wav
└── success.wav

config/
└── sound_config.json        # Конфигурация пользователя
```

## Интеграция с wxPython GUI

### Пример использования в главном окне приложения

```python
import wx
from src.audio.sound_manager import SoundManager
from src.audio.sound_events import AudioEvent

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="VK Desktop")
        
        # Инициализация менеджера звуков
        self.sound_manager = SoundManager()
        
        # Создание UI
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Кнопка для тестирования звука
        test_btn = wx.Button(panel, label="Тест звука")
        test_btn.Bind(wx.EVT_BUTTON, self.on_test_sound)
        sizer.Add(test_btn, 0, wx.ALL, 5)
        
        panel.SetSizer(sizer)
    
    def on_test_sound(self, event):
        """Обработчик для кнопки тестирования звука."""
        self.sound_manager.play_event(
            AudioEvent.MESSAGE_RECEIVED,
            user_name="Тестовый пользователь"
        )
    
    def on_message_received(self, user_name: str, message: str):
        """Обработчик получения сообщения."""
        # Воспроизведение звука события
        self.sound_manager.play_event(
            AudioEvent.MESSAGE_RECEIVED,
            user_name=user_name,
            message_preview=message[:50],  # Первые 50 символов
            priority=5  # Высокий приоритет
        )
    
    def on_close(self, event):
        """Завершение работы приложения."""
        # Корректное завершение работы менеджера звуков
        self.sound_manager.shutdown()
        self.Destroy()
```

## Конфигурационный файл

Пример файла `config/sound_config.json`:

```json
{
    "master_volume": 100,
    "category_volumes": {
        "messages": 100,
        "notifications": 100,
        "actions": 70,
        "media": 80,
        "profile": 75,
        "errors": 100
    },
    "enabled_categories": {
        "messages": true,
        "notifications": true,
        "actions": true,
        "media": true,
        "profile": true,
        "errors": true
    }
}
```

## Создание звуковых файлов

Для создания звуковых файлов используйте следующие инструменты:

### Рекомендуемые параметры:
- **Формат:** WAV (без сжатия)
- **Битрейт:** 16-bit PCM
- **Частота дискретизации:** 44100 Hz
- **Каналы:** Моно (1 канал)
- **Длительность:** 0.3-1.0 секунды

### Инструменты для создания:
1. **Audacity** - бесплатный и простой редактор
2. **FFmpeg** - командная строка для конвертации
3. **Adobe Audition** - профессиональный инструмент

### Пример с Audacity:
1. Создайте или импортируйте аудиофайл
2. Нормализируйте громкость (Effect → Normalize)
3. Обрежьте в нужной длительности
4. Экспортируйте как WAV файл (File → Export → Export as WAV)
5. Выберите параметры:
   - Format: WAV (Microsoft) signed 16-bit PCM
6. Сохраните в папку `sounds/` с соответствующим именем

## Поддержка скрин-ридеров

### NVDA (NonVisual Desktop Access)
Система звуковых событий полностью совместима с NVDA. Рекомендуется:
- Включить "речь через приложение" в настройках NVDA
- Установить громкость звуков на 80-100%
- Включить все категории уведомлений

### JAWS (Job Access With Speech)
Полная поддержка JAWS. Рекомендации:
- Использовать встроенную звуковую систему JAWS наряду с этой системой
- Настроить приоритеты звуков для избежания конфликтов

### Windows Narrator
Поддерживается, но рекомендуется использовать NVDA или JAWS для лучшего опыта.

## Оптимизация производительности

### Кэширование звуков
Систе кэширует загруженные звуки для быстрого воспроизведения:
```python
# При первом воспроизведении звук загружается и кэшируется
manager.play_event(AudioEvent.MESSAGE_RECEIVED)  # Загружается
manager.play_event(AudioEvent.MESSAGE_RECEIVED)  # Из кэша
```

### Асинхронное воспроизведение
Все звуки воспроизводятся в отдельном потоке, что не блокирует UI:
```python
# UI остается отзывчивым
for i in range(10):
    manager.play_event(AudioEvent.BUTTON_CLICK)
```

### Приоритизация событий
Соревания с высоким приоритетом обрабатываются раньше:
```python
# Это событие будет обработано первым
manager.play_event(AudioEvent.ERROR, priority=5)

# Это событие будет обработано после
manager.play_event(AudioEvent.BUTTON_CLICK, priority=1)
```

## Решение проблем

### Звуки не воспроизводятся
1. Проверьте наличие файлов звуков в папке `sounds/`
2. Проверьте, установлен ли VLC
3. Проверьте громкость системы Windows
4. Проверьте логи для деталей ошибки

### Звуки воспроизводятся с задержкой
1. Убедитесь, что система не перегружена
2. Уменьшите громкость категорий с меньшим приоритетом
3. Очистите очередь событий

### Конфликты с NVDA/JAWS
1. Проверьте настройки громкости
2. Попробуйте использовать разные звуки для разных событий
3. Отключите категорию действий (actions) при необходимости

## API Reference

### SoundManager класс

#### Методы:

**`__init__(sounds_directory: Optional[str] = None)`**
- Инициализирует менеджер звуков
- Параметры: путь к папке со звуками (опционально)

**`play_event(event: AudioEvent, **kwargs) -> None`**
- Воспроизводит звук для события
- Параметры:
  - `event`: тип события (AudioEvent)
  - `user_name`: имя пользователя (опционально)
  - `group_name`: название группы (опционально)
  - `message_preview`: предпросмотр сообщения (опционально)
  - `volume`: громкость (опционально, 0-100)
  - `priority`: приоритет (опционально, 1-5)

**`set_master_volume(volume: int) -> None`**
- Устанавливает общую громкость приложения
- Параметры: громкость (0-100)

**`set_category_volume(category: SoundEventCategory, volume: int) -> None`**
- Устанавливает громкость для категории
- Параметры:
  - `category`: категория события
  - `volume`: громкость (0-100)

**`enable_category(category: SoundEventCategory) -> None`**
- Включает звуки для категории
- Параметры: категория события

**`disable_category(category: SoundEventCategory) -> None`**
- Отключает звуки для категории
- Параметры: категория события

**`clear_queue() -> None`**
- Очищает очередь ожидающих звуков

**`shutdown() -> None`**
- Завершает работу менеджера и освобождает ресурсы

## Примеры кода

См. раздел "Использование" выше для подробных примеров.

## Лицензия

MIT License - см. файл LICENSE в корне проекта.

## Автор

[windos2006](https://github.com/windos2006)
