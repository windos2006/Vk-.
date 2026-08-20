"""
Определение типов звуковых событий приложения

Этот модуль содержит перечисление всех возможных звуковых событий,
которые происходят в приложении. Каждое событие имеет уникальный идентификатор
и связано с определённым действием пользователя или системы.

Все события разделены по категориям:
- Сообщения (получение, отправка, печать)
- Уведомления (друзья, подписки, лайки)
- Действия пользователя (клики, переходы)
- Ошибки и предупреждения
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class AudioEvent(Enum):
    """
    Перечисление всех типов звуковых событий в приложении.
    
    Сообщения и чаты:
    - MESSAGE_RECEIVED: получение нового сообщения
    - MESSAGE_SENT: отправка сообщения
    - USER_TYPING: пользователь начал печатать
    - USER_STOPPED_TYPING: пользователь перестал печатать
    - GROUP_TYPING: кто-то печатает в группе/беседе
    
    Уведомления:
    - FRIEND_REQUEST: получена заявка в друзья
    - FRIEND_ACCEPTED: заявка в друзья принята
    - FRIEND_REMOVED: друг удален
    - LIKE_RECEIVED: получен лайк
    - WALL_POST_COMMENT: комментарий к посту на стене
    - MENTION: упоминание пользователя
    
    Действия и системные события:
    - BUTTON_CLICK: нажатие кнопки
    - MENU_OPEN: открытие меню
    - MENU_CLOSE: закрытие меню
    - WINDOW_FOCUS: фокус на окно приложения
    - NOTIFICATION_ALERT: общее оповещение
    - ERROR: ошибка в приложении
    - WARNING: предупреждение
    - SUCCESS: успешное выполнение операции
    - LOADING: начало загрузки данных
    - LOADED: завершение загрузки данных
    
    Музыка и медиа:
    - AUDIO_PLAY: начало воспроизведения
    - AUDIO_PAUSE: пауза
    - AUDIO_STOP: остановка
    - AUDIO_NEXT: переход к следующему треку
    - AUDIO_PREVIOUS: переход к предыдущему треку
    
    Профиль и статус:
    - PROFILE_UPDATED: профиль обновлен
    - STATUS_CHANGED: статус изменен
    - ONLINE: пользователь онлайн
    - OFFLINE: пользователь оффлайн
    """
    # Сообщения и чаты
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    USER_TYPING = "user_typing"
    USER_STOPPED_TYPING = "user_stopped_typing"
    GROUP_TYPING = "group_typing"
    
    # Уведомления
    FRIEND_REQUEST = "friend_request"
    FRIEND_ACCEPTED = "friend_accepted"
    FRIEND_REMOVED = "friend_removed"
    LIKE_RECEIVED = "like_received"
    WALL_POST_COMMENT = "wall_post_comment"
    MENTION = "mention"
    
    # Действия и системные события
    BUTTON_CLICK = "button_click"
    MENU_OPEN = "menu_open"
    MENU_CLOSE = "menu_close"
    WINDOW_FOCUS = "window_focus"
    NOTIFICATION_ALERT = "notification_alert"
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    LOADING = "loading"
    LOADED = "loaded"
    
    # Музыка и медиа
    AUDIO_PLAY = "audio_play"
    AUDIO_PAUSE = "audio_pause"
    AUDIO_STOP = "audio_stop"
    AUDIO_NEXT = "audio_next"
    AUDIO_PREVIOUS = "audio_previous"
    
    # Профиль и статус
    PROFILE_UPDATED = "profile_updated"
    STATUS_CHANGED = "status_changed"
    ONLINE = "online"
    OFFLINE = "offline"


@dataclass
class SoundEventData:
    """
    Данные звукового события с дополнительной информацией.
    
    Атрибуты:
        event_type: тип события (AudioEvent)
        volume: громкость звука от 0 до 100 (по умолчанию 100)
        user_name: имя пользователя, связанного с событием (опционально)
        group_name: название группы/беседы, связанной с событием (опционально)
        message_preview: предпросмотр сообщения (опционально)
        priority: приоритет события (1-5, где 5 - наивысший)
    """
    event_type: AudioEvent
    volume: int = 100
    user_name: Optional[str] = None
    group_name: Optional[str] = None
    message_preview: Optional[str] = None
    priority: int = 3
    
    def __post_init__(self):
        """Валидация данных события после инициализации."""
        if not 0 <= self.volume <= 100:
            raise ValueError(f"Громкость должна быть от 0 до 100, получено: {self.volume}")
        
        if not 1 <= self.priority <= 5:
            raise ValueError(f"Приоритет должен быть от 1 до 5, получено: {self.priority}")


class SoundEventCategory(Enum):
    """
    Категории звуковых событий для группировки и управления.
    Позволяет отключать/включать целые категории событий.
    """
    MESSAGES = "messages"  # Сообщения и чаты
    NOTIFICATIONS = "notifications"  # Уведомления
    ACTIONS = "actions"  # Действия и системные события
    MEDIA = "media"  # Музыка и медиа
    PROFILE = "profile"  # Профиль и статус
    ERRORS = "errors"  # Ошибки и предупреждения


# Маппинг событий на категории
EVENT_CATEGORY_MAP = {
    # Сообщения
    AudioEvent.MESSAGE_RECEIVED: SoundEventCategory.MESSAGES,
    AudioEvent.MESSAGE_SENT: SoundEventCategory.MESSAGES,
    AudioEvent.USER_TYPING: SoundEventCategory.MESSAGES,
    AudioEvent.USER_STOPPED_TYPING: SoundEventCategory.MESSAGES,
    AudioEvent.GROUP_TYPING: SoundEventCategory.MESSAGES,
    
    # Уведомления
    AudioEvent.FRIEND_REQUEST: SoundEventCategory.NOTIFICATIONS,
    AudioEvent.FRIEND_ACCEPTED: SoundEventCategory.NOTIFICATIONS,
    AudioEvent.FRIEND_REMOVED: SoundEventCategory.NOTIFICATIONS,
    AudioEvent.LIKE_RECEIVED: SoundEventCategory.NOTIFICATIONS,
    AudioEvent.WALL_POST_COMMENT: SoundEventCategory.NOTIFICATIONS,
    AudioEvent.MENTION: SoundEventCategory.NOTIFICATIONS,
    
    # Действия
    AudioEvent.BUTTON_CLICK: SoundEventCategory.ACTIONS,
    AudioEvent.MENU_OPEN: SoundEventCategory.ACTIONS,
    AudioEvent.MENU_CLOSE: SoundEventCategory.ACTIONS,
    AudioEvent.WINDOW_FOCUS: SoundEventCategory.ACTIONS,
    AudioEvent.NOTIFICATION_ALERT: SoundEventCategory.ACTIONS,
    AudioEvent.LOADING: SoundEventCategory.ACTIONS,
    AudioEvent.LOADED: SoundEventCategory.ACTIONS,
    
    # Медиа
    AudioEvent.AUDIO_PLAY: SoundEventCategory.MEDIA,
    AudioEvent.AUDIO_PAUSE: SoundEventCategory.MEDIA,
    AudioEvent.AUDIO_STOP: SoundEventCategory.MEDIA,
    AudioEvent.AUDIO_NEXT: SoundEventCategory.MEDIA,
    AudioEvent.AUDIO_PREVIOUS: SoundEventCategory.MEDIA,
    
    # Профиль
    AudioEvent.PROFILE_UPDATED: SoundEventCategory.PROFILE,
    AudioEvent.STATUS_CHANGED: SoundEventCategory.PROFILE,
    AudioEvent.ONLINE: SoundEventCategory.PROFILE,
    AudioEvent.OFFLINE: SoundEventCategory.PROFILE,
    
    # Ошибки
    AudioEvent.ERROR: SoundEventCategory.ERRORS,
    AudioEvent.WARNING: SoundEventCategory.ERRORS,
    AudioEvent.SUCCESS: SoundEventCategory.ERRORS,
}
