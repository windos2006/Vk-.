"""
Модуль для работы с ботами ВКонтакте

Предоставляет функциональность для:
- Управления ботами
- Отправки команд ботам
- Обработки ответов от ботов
- Интеграции с диалогами
"""

import logging
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class BotStatus(Enum):
    """
    Статусы ботов.
    
    AVAILABLE: бот доступен
    OFFLINE: бот офлайн
    UNAVAILABLE: бот недоступен
    """
    AVAILABLE = "available"
    OFFLINE = "offline"
    UNAVAILABLE = "unavailable"


@dataclass
class BotInfo:
    """
    Информация о боте.
    
    Атрибуты:
        bot_id: ID бота
        name: имя бота
        description: описание бота
        status: статус бота
        avatar_url: URL аватара бота
        commands: список доступных команд
    """
    bot_id: int
    name: str
    description: str
    status: BotStatus
    avatar_url: Optional[str] = None
    commands: List[str] = None


class BotManager:
    """
    Менеджер для работы с ботами ВКонтакте.
    
    Управляет ботами, отправкой команд и обработкой ответов.
    """
    
    def __init__(self, api_client):
        """
        Инициализация менеджера ботов.
        
        Args:
            api_client: клиент VK API
        """
        self.api_client = api_client
        self.bots: Dict[int, BotInfo] = {}
        self.message_callbacks = []
    
    def register_bot(self, bot_id: int, name: str, description: str, commands: List[str]) -> bool:
        """
        Зарегистрировать бота в системе.
        
        Args:
            bot_id: ID бота
            name: имя бота
            description: описание функциональности
            commands: список доступных команд
        
        Returns:
            True если успешно, False при ошибке
        """
        try:
            self.bots[bot_id] = BotInfo(
                bot_id=bot_id,
                name=name,
                description=description,
                status=BotStatus.AVAILABLE,
                commands=commands
            )
            
            logger.info(f"Бот {name} (ID: {bot_id}) зарегистрирован")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при регистрации бота: {e}")
            return False
    
    def send_command(self, bot_id: int, command: str, args: Optional[str] = None) -> bool:
        """
        Отправить команду боту.
        
        Args:
            bot_id: ID бота
            command: команда для отправки
            args: аргументы команды (опционально)
        
        Returns:
            True если успешно, False при ошибке
        """
        try:
            if bot_id not in self.bots:
                logger.warning(f"Бот {bot_id} не найден")
                return False
            
            bot = self.bots[bot_id]
            
            if bot.status != BotStatus.AVAILABLE:
                logger.warning(f"Бот {bot.name} недоступен")
                return False
            
            # Формируем сообщение команды
            message = f"/{command}"
            if args:
                message += f" {args}"
            
            # Отправляем команду боту
            result = self.api_client.send_message(bot_id, message)
            
            if result:
                logger.info(f"Команда '{command}' отправлена боту {bot.name}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Ошибка при отправке команды: {e}")
            return False
    
    def get_bot_info(self, bot_id: int) -> Optional[BotInfo]:
        """
        Получить информацию о боте.
        
        Args:
            bot_id: ID бота
        
        Returns:
            Информация о боте или None если не найден
        """
        return self.bots.get(bot_id)
    
    def get_available_bots(self) -> List[BotInfo]:
        """
        Получить список всех доступных ботов.
        
        Returns:
            Список доступных ботов
        """
        available = [
            bot for bot in self.bots.values()
            if bot.status == BotStatus.AVAILABLE
        ]
        return available
    
    def register_callback(self, callback: Callable) -> None:
        """
        Зарегистрировать callback для сообщений от ботов.
        
        Args:
            callback: функция для вызова при получении сообщения от бота
        """
        self.message_callbacks.append(callback)
        logger.info("Callback для сообщений ботов зарегистрирован")
    
    def handle_bot_message(self, bot_id: int, message: str) -> None:
        """
        Обработать сообщение от бота.
        
        Args:
            bot_id: ID бота
            message: сообщение от бота
        """
        try:
            if bot_id in self.bots:
                bot = self.bots[bot_id]
                
                # Вызываем все зарегистрированные callbacks
                for callback in self.message_callbacks:
                    try:
                        callback(bot, message)
                    except Exception as e:
                        logger.error(f"Ошибка в callback бота: {e}")
                
                logger.info(f"Сообщение от {bot.name} обработано")
        
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения бота: {e}")
    
    def update_bot_status(self, bot_id: int, status: BotStatus) -> bool:
        """
        Обновить статус бота.
        
        Args:
            bot_id: ID бота
            status: новый статус
        
        Returns:
            True если успешно, False при ошибке
        """
        try:
            if bot_id not in self.bots:
                return False
            
            self.bots[bot_id].status = status
            logger.info(f"Статус бота {bot_id} обновлён на {status.value}")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса бота: {e}")
            return False
