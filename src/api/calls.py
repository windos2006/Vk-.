"""
Модуль для работы с голосовыми вызовами через VK API

Предоставляет функциональность для:
- Инициализации голосовых вызовов
- Управления состоянием вызова
- Обработки входящих вызовов
- Завершения вызовов
"""

import logging
from typing import Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


class CallState(Enum):
    """
    Состояния голосовых вызовов.
    
    IDLE: приложение готово к вызовам
    CALLING: исходящий вызов в процессе подключения
    INCOMING: входящий вызов ожидает ответа
    CONNECTED: активный вызов
    DISCONNECTING: вызов завершается
    ENDED: вызов завершён
    """
    IDLE = "idle"
    CALLING = "calling"
    INCOMING = "incoming"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ENDED = "ended"


@dataclass
class CallInfo:
    """
    Информация о голосовом вызове.
    
    Атрибуты:
        call_id: уникальный идентификатор вызова
        initiator_id: ID инициатора вызова
        recipient_id: ID получателя вызова
        state: текущее состояние вызова
        started_at: время начала вызова
        duration: длительность вызова в секундах (0 если не завершён)
    """
    call_id: str
    initiator_id: int
    recipient_id: int
    state: CallState
    started_at: datetime
    duration: int = 0


class CallManager:
    """
    Менеджер голосовых вызовов для работы с VK API.
    
    Обрабатывает инициализацию, управление и завершение вызовов.
    """
    
    def __init__(self, api_client):
        """
        Инициализация менеджера вызовов.
        
        Args:
            api_client: клиент VK API для выполнения операций
        """
        self.api_client = api_client
        self.current_call: Optional[CallInfo] = None
        self.call_callbacks = []
    
    def register_callback(self, callback: Callable) -> None:
        """
        Зарегистрировать callback для событий вызовов.
        
        Args:
            callback: функция для вызова при изменении состояния
        """
        self.call_callbacks.append(callback)
        logger.info("Callback для вызовов зарегистрирован")
    
    def initiate_call(self, user_id: int) -> bool:
        """
        Инициировать исходящий вызов.
        
        Args:
            user_id: ID пользователя для вызова
        
        Returns:
            True если вызов успешно инициирован, False при ошибке
        """
        try:
            # Проверяем, нет ли уже активного вызова
            if self.current_call and self.current_call.state != CallState.ENDED:
                logger.warning("Уже есть активный вызов")
                return False
            
            # Создаём новый вызов
            self.current_call = CallInfo(
                call_id=f"call_{int(datetime.now().timestamp())}",
                initiator_id=self.api_client.current_user_id,
                recipient_id=user_id,
                state=CallState.CALLING,
                started_at=datetime.now()
            )
            
            logger.info(f"Инициирован вызов пользователю {user_id}")
            self._notify_callbacks(self.current_call)
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при инициировании вызова: {e}")
            return False
    
    def answer_call(self) -> bool:
        """
        Ответить на входящий вызов.
        
        Returns:
            True если успешно, False при ошибке
        """
        try:
            if not self.current_call or self.current_call.state != CallState.INCOMING:
                logger.warning("Нет входящего вызова для ответа")
                return False
            
            self.current_call.state = CallState.CONNECTED
            logger.info(f"Вызов от {self.current_call.initiator_id} принят")
            self._notify_callbacks(self.current_call)
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при ответе на вызов: {e}")
            return False
    
    def reject_call(self) -> bool:
        """
        Отклонить входящий вызов.
        
        Returns:
            True если успешно, False при ошибке
        """
        try:
            if not self.current_call:
                logger.warning("Нет вызова для отклонения")
                return False
            
            self.current_call.state = CallState.ENDED
            logger.info(f"Вызов отклонен")
            self._notify_callbacks(self.current_call)
            self.current_call = None
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при отклонении вызова: {e}")
            return False
    
    def end_call(self) -> bool:
        """
        Завершить текущий вызов.
        
        Returns:
            True если успешно, False при ошибке
        """
        try:
            if not self.current_call:
                logger.warning("Нет активного вызова для завершения")
                return False
            
            # Рассчитываем длительность
            duration = int((datetime.now() - self.current_call.started_at).total_seconds())
            self.current_call.duration = duration
            self.current_call.state = CallState.ENDED
            
            logger.info(f"Вызов завершён. Длительность: {duration} сек")
            self._notify_callbacks(self.current_call)
            self.current_call = None
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при завершении вызова: {e}")
            return False
    
    def get_call_info(self) -> Optional[CallInfo]:
        """
        Получить информацию о текущем вызове.
        
        Returns:
            Информация о вызове или None если вызова нет
        """
        return self.current_call
    
    def is_in_call(self) -> bool:
        """
        Проверить, находится ли пользователь в активном вызове.
        
        Returns:
            True если в вызове, False если нет
        """
        return self.current_call is not None and self.current_call.state == CallState.CONNECTED
    
    def _notify_callbacks(self, call_info: CallInfo) -> None:
        """
        Уведомить всех зарегистрированных слушателей о событии вызова.
        
        Args:
            call_info: информация о вызове
        """
        for callback in self.call_callbacks:
            try:
                callback(call_info)
            except Exception as e:
                logger.error(f"Ошибка в callback вызова: {e}")
