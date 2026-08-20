"""
Менеджер звуков и управление воспроизведением

Этот модуль отвечает за воспроизведение всех звуковых событий в приложении.
Исользует VLC для воспроизведения и поддерживает асинхронное воспроизведение
для избежания зависаний интерфейса.

Основные функции:
- Воспроизведение звуков по типам событий
- Управление громкостью
- Загрузка звуков из файлов
- Кэширование загруженных звуков
- Асинхронное воспроизведение
- Поддержка приоритизации событий
"""

import os
import threading
import logging
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, field
import vlc

from .sound_events import AudioEvent, SoundEventData, SoundEventCategory, EVENT_CATEGORY_MAP

# Настройка логирования
logger = logging.getLogger(__name__)


@dataclass
class SoundConfig:
    """
    Конфигурация звуков для каждого события.
    
    Атрибуты:
        event: тип события
        file_name: имя файла звука (без пути)
        default_volume: громкость по умолчанию (0-100)
        allow_repeat: разрешить ли повторное воспроизведение без задержки
    """
    event: AudioEvent
    file_name: str
    default_volume: int = 100
    allow_repeat: bool = True


class SoundManager:
    """
    Основной класс для управления всеми звуковыми событиями приложения.
    
    Эта система позволяет:
    - Воспроизводить звуки для различных событий
    - Управлять громкостью по категориям и для отдельных событий
    - Кэшировать загруженные звуки для быстрого воспроизведения
    - Асинхронно воспроизводить звуки
    - Приоритизировать события с высоким приоритетом
    
    Пример использования:
        manager = SoundManager()
        manager.play_event(AudioEvent.MESSAGE_RECEIVED, user_name="Иван")
    """
    
    def __init__(self, sounds_directory: Optional[str] = None):
        """
        Инициализация менеджера звуков.
        
        Args:
            sounds_directory: путь к папке со звуками (если None, использует ./sounds/)
        """
        # Определение директории со звуками
        if sounds_directory is None:
            sounds_directory = os.path.join(os.path.dirname(__file__), '..', '..', 'sounds')
        
        self.sounds_directory = Path(sounds_directory)
        self.sounds_directory.mkdir(parents=True, exist_ok=True)
        
        # VLC инстанция для воспроизведения
        self.vlc_instance = vlc.Instance()
        self.media_list_player = self.vlc_instance.media_list_player_new()
        
        # Кэш загруженных медиа файлов
        self.media_cache: Dict[AudioEvent, vlc.Media] = {}
        
        # Конфигурация звуков для каждого события
        self.sound_configs = self._init_sound_configs()
        
        # Управление громкостью по категориям
        self.category_volumes: Dict[SoundEventCategory, int] = {
            category: 100 for category in SoundEventCategory
        }
        
        # Общая громкость приложения
        self.master_volume = 100
        
        # Включенные/отключенные категории
        self.enabled_categories: Dict[SoundEventCategory, bool] = {
            category: True for category in SoundEventCategory
        }
        
        # Очередь событий с приоритетом
        self.event_queue: List[SoundEventData] = []
        
        # Поток для асинхронного воспроизведения
        self.playback_thread: Optional[threading.Thread] = None
        self.is_playing = False
        
        logger.info(f"SoundManager инициализирован. Директория звуков: {self.sounds_directory}")
    
    def _init_sound_configs(self) -> Dict[AudioEvent, SoundConfig]:
        """
        Инициализация конфигурации звуков для всех событий.
        
        Returns:
            Словарь с конфигурациями звуков для каждого события
        """
        return {
            # Сообщения
            AudioEvent.MESSAGE_RECEIVED: SoundConfig(
                AudioEvent.MESSAGE_RECEIVED,
                "message_received.wav",
                default_volume=100,
                allow_repeat=True
            ),
            AudioEvent.MESSAGE_SENT: SoundConfig(
                AudioEvent.MESSAGE_SENT,
                "message_sent.wav",
                default_volume=80,
                allow_repeat=True
            ),
            AudioEvent.USER_TYPING: SoundConfig(
                AudioEvent.USER_TYPING,
                "user_typing.wav",
                default_volume=60,
                allow_repeat=False
            ),
            AudioEvent.USER_STOPPED_TYPING: SoundConfig(
                AudioEvent.USER_STOPPED_TYPING,
                "user_stopped_typing.wav",
                default_volume=60,
                allow_repeat=False
            ),
            AudioEvent.GROUP_TYPING: SoundConfig(
                AudioEvent.GROUP_TYPING,
                "group_typing.wav",
                default_volume=70,
                allow_repeat=False
            ),
            
            # Уведомления
            AudioEvent.FRIEND_REQUEST: SoundConfig(
                AudioEvent.FRIEND_REQUEST,
                "friend_request.wav",
                default_volume=100,
                allow_repeat=True
            ),
            AudioEvent.FRIEND_ACCEPTED: SoundConfig(
                AudioEvent.FRIEND_ACCEPTED,
                "friend_accepted.wav",
                default_volume=90,
                allow_repeat=True
            ),
            AudioEvent.FRIEND_REMOVED: SoundConfig(
                AudioEvent.FRIEND_REMOVED,
                "friend_removed.wav",
                default_volume=80,
                allow_repeat=True
            ),
            AudioEvent.LIKE_RECEIVED: SoundConfig(
                AudioEvent.LIKE_RECEIVED,
                "like_received.wav",
                default_volume=85,
                allow_repeat=True
            ),
            AudioEvent.WALL_POST_COMMENT: SoundConfig(
                AudioEvent.WALL_POST_COMMENT,
                "wall_post_comment.wav",
                default_volume=90,
                allow_repeat=True
            ),
            AudioEvent.MENTION: SoundConfig(
                AudioEvent.MENTION,
                "mention.wav",
                default_volume=100,
                allow_repeat=True
            ),
            
            # Действия
            AudioEvent.BUTTON_CLICK: SoundConfig(
                AudioEvent.BUTTON_CLICK,
                "button_click.wav",
                default_volume=50,
                allow_repeat=True
            ),
            AudioEvent.MENU_OPEN: SoundConfig(
                AudioEvent.MENU_OPEN,
                "menu_open.wav",
                default_volume=60,
                allow_repeat=True
            ),
            AudioEvent.MENU_CLOSE: SoundConfig(
                AudioEvent.MENU_CLOSE,
                "menu_close.wav",
                default_volume=60,
                allow_repeat=True
            ),
            AudioEvent.NOTIFICATION_ALERT: SoundConfig(
                AudioEvent.NOTIFICATION_ALERT,
                "notification_alert.wav",
                default_volume=100,
                allow_repeat=True
            ),
            AudioEvent.LOADING: SoundConfig(
                AudioEvent.LOADING,
                "loading.wav",
                default_volume=70,
                allow_repeat=False
            ),
            AudioEvent.LOADED: SoundConfig(
                AudioEvent.LOADED,
                "loaded.wav",
                default_volume=80,
                allow_repeat=True
            ),
            
            # Медиа
            AudioEvent.AUDIO_PLAY: SoundConfig(
                AudioEvent.AUDIO_PLAY,
                "audio_play.wav",
                default_volume=70,
                allow_repeat=True
            ),
            AudioEvent.AUDIO_PAUSE: SoundConfig(
                AudioEvent.AUDIO_PAUSE,
                "audio_pause.wav",
                default_volume=70,
                allow_repeat=True
            ),
            AudioEvent.AUDIO_STOP: SoundConfig(
                AudioEvent.AUDIO_STOP,
                "audio_stop.wav",
                default_volume=70,
                allow_repeat=True
            ),
            AudioEvent.AUDIO_NEXT: SoundConfig(
                AudioEvent.AUDIO_NEXT,
                "audio_next.wav",
                default_volume=75,
                allow_repeat=True
            ),
            AudioEvent.AUDIO_PREVIOUS: SoundConfig(
                AudioEvent.AUDIO_PREVIOUS,
                "audio_previous.wav",
                default_volume=75,
                allow_repeat=True
            ),
            
            # Профиль
            AudioEvent.PROFILE_UPDATED: SoundConfig(
                AudioEvent.PROFILE_UPDATED,
                "profile_updated.wav",
                default_volume=85,
                allow_repeat=True
            ),
            AudioEvent.STATUS_CHANGED: SoundConfig(
                AudioEvent.STATUS_CHANGED,
                "status_changed.wav",
                default_volume=80,
                allow_repeat=True
            ),
            AudioEvent.ONLINE: SoundConfig(
                AudioEvent.ONLINE,
                "online.wav",
                default_volume=75,
                allow_repeat=True
            ),
            AudioEvent.OFFLINE: SoundConfig(
                AudioEvent.OFFLINE,
                "offline.wav",
                default_volume=75,
                allow_repeat=True
            ),
            
            # Ошибки
            AudioEvent.ERROR: SoundConfig(
                AudioEvent.ERROR,
                "error.wav",
                default_volume=100,
                allow_repeat=True
            ),
            AudioEvent.WARNING: SoundConfig(
                AudioEvent.WARNING,
                "warning.wav",
                default_volume=95,
                allow_repeat=True
            ),
            AudioEvent.SUCCESS: SoundConfig(
                AudioEvent.SUCCESS,
                "success.wav",
                default_volume=90,
                allow_repeat=True
            ),
        }
    
    def play_event(self, event: AudioEvent, **kwargs) -> None:
        """
        Воспроизвести звук для события.
        
        Args:
            event: тип события для воспроизведения
            **kwargs: дополнительные пар��метры (volume, user_name, group_name, priority, message_preview)
        
        Example:
            manager.play_event(AudioEvent.MESSAGE_RECEIVED, user_name="Иван", volume=100)
        """
        # Проверка, включена ли категория события
        category = EVENT_CATEGORY_MAP.get(event)
        if category and not self.enabled_categories.get(category, True):
            logger.debug(f"Категория {category} отключена, звук не воспроизводится")
            return
        
        # Получение громкости из параметров или используя значение по умолчанию
        volume = kwargs.get('volume', None)
        if volume is None and event in self.sound_configs:
            volume = self.sound_configs[event].default_volume
        
        # Создание данных события
        event_data = SoundEventData(
            event_type=event,
            volume=volume or 100,
            user_name=kwargs.get('user_name'),
            group_name=kwargs.get('group_name'),
            message_preview=kwargs.get('message_preview'),
            priority=kwargs.get('priority', 3)
        )
        
        # Добавление события в очередь
        self._enqueue_event(event_data)
        logger.info(f"Событие {event.value} добавлено в очередь воспроизведения")
    
    def _enqueue_event(self, event_data: SoundEventData) -> None:
        """
        Добавить событие в очередь для воспроизведения.
        
        Args:
            event_data: данные события для добавления
        """
        self.event_queue.append(event_data)
        
        # Сортировка очереди по приоритету (высший приоритет первым)
        self.event_queue.sort(key=lambda x: x.priority, reverse=True)
        
        # Запуск потока воспроизведения, если он еще не запущен
        if not self.is_playing:
            self._start_playback_thread()
    
    def _start_playback_thread(self) -> None:
        """
        Запустить поток для асинхронного воспроизведения звуков.
        """
        if self.playback_thread is None or not self.playback_thread.is_alive():
            self.is_playing = True
            self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
            self.playback_thread.start()
    
    def _playback_loop(self) -> None:
        """
        Основной цикл воспроизведения звуков из очереди.
        """
        while self.is_playing and len(self.event_queue) > 0:
            event_data = self.event_queue.pop(0)
            self._play_sound(event_data)
        
        self.is_playing = False
    
    def _play_sound(self, event_data: SoundEventData) -> None:
        """
        Воспроизвести звук для конкретного события.
        
        Args:
            event_data: данные события для воспроизведения
        """
        if event_data.event_type not in self.sound_configs:
            logger.warning(f"Нет конфигурации для события {event_data.event_type.value}")
            return
        
        config = self.sound_configs[event_data.event_type]
        sound_path = self.sounds_directory / config.file_name
        
        # Проверка наличия файла звука
        if not sound_path.exists():
            logger.warning(f"Файл звука не найден: {sound_path}")
            return
        
        try:
            # Загрузка или получение из кэша
            if event_data.event_type not in self.media_cache:
                media = self.vlc_instance.media_new(str(sound_path))
                self.media_cache[event_data.event_type] = media
            else:
                media = self.media_cache[event_data.event_type]
            
            # Создание медиа плеера для воспроизведения
            media_player = self.vlc_instance.media_list_player_new()
            media_list = self.vlc_instance.media_list_new()
            media_list.add_media(media)
            media_player.set_media_list(media_list)
            
            # Установка громкости
            volume = self._calculate_volume(event_data)
            media_player.get_media_player().audio_set_volume(volume)
            
            # Воспроизведение
            media_player.play()
            
            # Ожидание завершения воспроизведения
            while media_player.is_playing():
                threading.Event().wait(0.1)
            
            logger.info(f"Звук для события {event_data.event_type.value} успешно воспроизведен")
        
        except Exception as e:
            logger.error(f"Ошибка при воспроизведении звука: {e}", exc_info=True)
    
    def _calculate_volume(self, event_data: SoundEventData) -> int:
        """
        Рассчитать итоговую громкость с учетом всех множителей.
        
        Args:
            event_data: данные события
        
        Returns:
            Финальная громкость (0-100)
        """
        # Получение категории события
        category = EVENT_CATEGORY_MAP.get(event_data.event_type)
        category_volume = self.category_volumes.get(category, 100)
        
        # Расчет: громкость события * громкость категории * общая громкость / 10000
        final_volume = int(
            (event_data.volume * category_volume * self.master_volume) / 1000000 * 100
        )
        
        return min(100, max(0, final_volume))
    
    def set_master_volume(self, volume: int) -> None:
        """
        Установить общую громкость приложения.
        
        Args:
            volume: громкость от 0 до 100
        """
        if not 0 <= volume <= 100:
            raise ValueError(f"Громкость должна быть от 0 до 100, получено: {volume}")
        
        self.master_volume = volume
        logger.info(f"Общая громкость установлена на {volume}%")
    
    def set_category_volume(self, category: SoundEventCategory, volume: int) -> None:
        """
        Установить громкость для категории событий.
        
        Args:
            category: категория для изменения
            volume: громкость от 0 до 100
        """
        if not 0 <= volume <= 100:
            raise ValueError(f"Громкость должна быть от 0 до 100, получено: {volume}")
        
        self.category_volumes[category] = volume
        logger.info(f"Громкость категории {category.value} установлена на {volume}%")
    
    def enable_category(self, category: SoundEventCategory) -> None:
        """
        Включить звуки для категории.
        
        Args:
            category: категория для включения
        """
        self.enabled_categories[category] = True
        logger.info(f"Категория {category.value} включена")
    
    def disable_category(self, category: SoundEventCategory) -> None:
        """
        Отключить звуки для категории.
        
        Args:
            category: категория для отключения
        """
        self.enabled_categories[category] = False
        logger.info(f"Категория {category.value} отключена")
    
    def clear_queue(self) -> None:
        """
        Очистить очередь воспроизведения.
        """
        self.event_queue.clear()
        logger.info("Очередь воспроизведения очищена")
    
    def shutdown(self) -> None:
        """
        Завершить работу менеджера звуков и освободить ресурсы.
        """
        self.is_playing = False
        self.clear_queue()
        
        # Очистка кэша медиа
        self.media_cache.clear()
        
        # Ожидание завершения потока воспроизведения
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=2.0)
        
        logger.info("SoundManager завершил работу")
