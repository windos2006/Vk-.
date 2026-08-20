"""
Модуль аутентификации и управления токенами для VK API

Этот модуль отвечает за:
- Получение и управление токенами доступа
- Сохранение токенов в защищённом виде
- Проверку срока действия токена
- Обновление токена при необходимости
- Управление сессиями пользователя
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class TokenStorage:
    """
    Класс для безопасного хранения и управления токенами.
    
    Токены шифруются перед сохранением на диск для защиты от несанкционированного доступа.
    """
    
    def __init__(self, storage_path: str = "config/tokens.encrypted"):
        """
        Инициализация хранилища токенов.
        
        Args:
            storage_path: путь к файлу хранилища токенов
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Генерируем или загружаем ключ шифрования
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """
        Получить или создать ключ шифрования.
        
        Returns:
            Ключ шифрования
        """
        key_path = Path("config/.key")
        
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(key_path, 'wb') as f:
                f.write(key)
            # Устанавливаем права доступа (только для владельца)
            os.chmod(key_path, 0o600)
            logger.info(f"Создан новый ключ шифрования в {key_path}")
            return key
    
    def save_token(self, user_id: int, token: str, expires_in: int = 86400) -> None:
        """
        Сохранить токен доступа.
        
        Args:
            user_id: ID пользователя ВКонтакте
            token: токен доступа
            expires_in: время жизни токена в секундах (по умолчанию 24 часа)
        """
        # Создаём структуру данных токена
        token_data = {
            'user_id': user_id,
            'token': token,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        }
        
        # Шифруем и сохраняем
        json_data = json.dumps(token_data).encode()
        encrypted_data = self.cipher.encrypt(json_data)
        
        with open(self.storage_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Устанавливаем права доступа
        os.chmod(self.storage_path, 0o600)
        logger.info(f"Токен сохранён для пользователя {user_id}")
    
    def load_token(self) -> Optional[dict]:
        """
        Загрузить сохранённый токен.
        
        Returns:
            Словарь с данными токена или None если токена нет
        """
        if not self.storage_path.exists():
            return None
        
        try:
            with open(self.storage_path, 'rb') as f:
                encrypted_data = f.read()
            
            json_data = self.cipher.decrypt(encrypted_data)
            token_data = json.loads(json_data.decode())
            
            logger.info(f"Токен загружен для пользователя {token_data['user_id']}")
            return token_data
        
        except Exception as e:
            logger.error(f"Ошибка при загрузке токена: {e}")
            return None
    
    def is_token_valid(self, token_data: dict) -> bool:
        """
        Проверить, действителен ли токен.
        
        Args:
            token_data: словарь с данными токена
        
        Returns:
            True если токен ещё действителен, False если истёк
        """
        if not token_data:
            return False
        
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        is_valid = datetime.now() < expires_at
        
        if not is_valid:
            logger.warning(f"Токен истёк для пользователя {token_data['user_id']}")
        
        return is_valid
    
    def delete_token(self) -> None:
        """
        Удалить сохранённый токен.
        """
        if self.storage_path.exists():
            self.storage_path.unlink()
            logger.info("Токен удалён")


class AuthManager:
    """
    Менеджер аутентификации для работы с VK API.
    
    Обрабатывает процесс получения токена, его сохранение и проверку актуальности.
    """
    
    def __init__(self, app_id: int):
        """
        Инициализация менеджера аутентификации.
        
        Args:
            app_id: ID приложения ВКонтакте
        """
        self.app_id = app_id
        self.token_storage = TokenStorage()
        self.current_token: Optional[str] = None
        self.current_user_id: Optional[int] = None
    
    def get_token(self) -> Optional[str]:
        """
        Получить действительный токен доступа.
        
        Сначала пытается загрузить сохранённый токен,
        если его нет или он истёк, требует повторную аутентификацию.
        
        Returns:
            Токен доступа или None если не удалось получить
        """
        # Если уже есть токен в памяти, используем его
        if self.current_token:
            return self.current_token
        
        # Пытаемся загрузить сохранённый токен
        token_data = self.token_storage.load_token()
        
        if token_data and self.token_storage.is_token_valid(token_data):
            self.current_token = token_data['token']
            self.current_user_id = token_data['user_id']
            logger.info(f"Использован сохранённый токен для пользователя {self.current_user_id}")
            return self.current_token
        
        logger.warning("Токен не найден или истёк, требуется аутентификация")
        return None
    
    def save_token(self, user_id: int, token: str, expires_in: int = 86400) -> None:
        """
        Сохранить токен доступа.
        
        Args:
            user_id: ID пользователя ВКонтакте
            token: полученный токен
            expires_in: время жизни токена в секундах
        """
        self.token_storage.save_token(user_id, token, expires_in)
        self.current_token = token
        self.current_user_id = user_id
    
    def clear_token(self) -> None:
        """
        Удалить сохранённый токен и выйти из аккаунта.
        """
        self.token_storage.delete_token()
        self.current_token = None
        self.current_user_id = None
        logger.info("Пользователь вышел из системы")
