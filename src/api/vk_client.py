"""
Модуль для работы с VK API

Предоставляет клиент для взаимодействия с ВКонтакте API,
получения сообщений, управления контактами, поиска и т.д.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

logger = logging.getLogger(__name__)


class VKClient:
    """
    Основной клиент для работы с VK API.
    
    Предоставляет методы для:
    - Получения сообщений
    - Отправки сообщений
    - Управления друзьями
    - Получения информации профиля
    - Поиска пользователей и групп
    - Работы с аудиозаписями
    """
    
    # Версия API
    API_VERSION = '5.131'
    
    def __init__(self, token: str):
        """
        Инициализация VK API клиента.
        
        Args:
            token: токен доступа ВКонтакте
        """
        self.token = token
        self.session = vk_api.VkApi(token=token)
        self.api = self.session.get_api()
        self.longpoll = VkLongPoll(self.session)
        
        logger.info("VK API клиент инициализирован")
    
    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о пользователе.
        
        Args:
            user_id: ID пользователя ВКонтакте
        
        Returns:
            Словарь с информацией о пользователе или None при ошибке
        """
        try:
            user_info = self.api.users.get(
                user_ids=user_id,
                fields='photo_50,status,online,last_seen'
            )
            
            if user_info:
                logger.info(f"Получена информация о пользователе {user_id}")
                return user_info[0]
            
            return None
        
        except Exception as e:
            logger.error(f"Ошибка при получении информации о пользователе: {e}")
            return None
    
    def get_messages(self, count: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Получить последние сообщения.
        
        Args:
            count: количество сообщений для получения
        
        Returns:
            Список сообщений или None при ошибке
        """
        try:
            messages = self.api.messages.getConversations(
                count=count,
                fields='photo_50,status'
            )
            
            logger.info(f"Получено {len(messages.get('items', []))} разговоров")
            return messages.get('items', [])
        
        except Exception as e:
            logger.error(f"Ошибка при получении сообщений: {e}")
            return None
    
    def send_message(self, peer_id: int, message: str, attachment: Optional[str] = None) -> Optional[int]:
        """
        Отправить сообщение пользователю или в группу.
        
        Args:
            peer_id: ID получателя (пользователя или группы)
            message: текст сообщения
            attachment: путь к файлу для отправки (опционально)
        
        Returns:
            ID отправленного сообщения или None при ошибке
        """
        try:
            result = self.api.messages.send(
                peer_id=peer_id,
                message=message,
                random_id=0  # VK API сам генерирует random_id
            )
            
            logger.info(f"Сообщение отправлено пользователю {peer_id}")
            return result
        
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            return None
    
    def get_friends(self, user_id: int, count: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Получить список друзей пользователя.
        
        Args:
            user_id: ID пользователя
            count: количество друзей для получения
        
        Returns:
            Список друзей или None при ошибке
        """
        try:
            friends = self.api.friends.get(
                user_id=user_id,
                count=count,
                fields='photo_50,status,online'
            )
            
            logger.info(f"Получен список из {len(friends.get('items', []))} друзей")
            return friends.get('items', [])
        
        except Exception as e:
            logger.error(f"Ошибка при получении списка друзей: {e}")
            return None
    
    def search_users(self, query: str, count: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Поиск пользователей по запросу.
        
        Args:
            query: поисковый запрос
            count: количество результатов
        
        Returns:
            Список найденных пользователей или None при ошибке
        """
        try:
            results = self.api.users.search(
                q=query,
                count=count,
                fields='photo_50,status,online'
            )
            
            logger.info(f"Найдено {len(results.get('items', []))} пользователей по запросу '{query}'")
            return results.get('items', [])
        
        except Exception as e:
            logger.error(f"Ошибка при поиске пользователей: {e}")
            return None
    
    def get_audio(self, owner_id: int, count: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Получить аудиозаписи пользователя.
        
        Args:
            owner_id: ID владельца аудиозаписей
            count: количество аудиозаписей
        
        Returns:
            Список аудиозаписей или None при ошибке
        """
        try:
            audios = self.api.audio.get(
                owner_id=owner_id,
                count=count
            )
            
            logger.info(f"Получено {len(audios.get('items', []))} аудиозаписей")
            return audios.get('items', [])
        
        except Exception as e:
            logger.error(f"Ошибка при получении аудиозаписей: {e}")
            return None
    
    def get_dialogs(self, count: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Получить диалоги с информацией о последних сообщениях.
        
        Args:
            count: количество диалогов
        
        Returns:
            Список диалогов или None при ошибке
        """
        try:
            dialogs = self.api.messages.getConversations(
                count=count,
                fields='photo_50,status,online'
            )
            
            logger.info(f"Получено {len(dialogs.get('items', []))} диалогов")
            return dialogs.get('items', [])
        
        except Exception as e:
            logger.error(f"Ошибка при получении диалогов: {e}")
            return None
    
    def add_friend(self, user_id: int) -> bool:
        """
        Отправить заявку в друзья.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            True если успешно, False при ошибке
        """
        try:
            self.api.friends.add(user_id=user_id)
            logger.info(f"Заявка в друзья отправлена пользователю {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при отправке заявки: {e}")
            return False
    
    def remove_friend(self, user_id: int) -> bool:
        """
        Удалить пользователя из друзей.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            True если успешно, False при ошибке
        """
        try:
            self.api.friends.delete(user_id=user_id)
            logger.info(f"Пользователь {user_id} удалён из друзей")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при удалении из друзей: {e}")
            return False
