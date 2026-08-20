"""
Конфигурация и настройки звуковой системы

Этот модуль отвечает за сохранение и загрузку пользовательских настроек
звуков из файла конфигурации. Позволяет пользователю настраивать громкость
для каждой категории, включать/отключать события и управлять прочими
параметрами звуковой системы.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
from dataclasses import asdict, dataclass

from .sound_events import SoundEventCategory

logger = logging.getLogger(__name__)


@dataclass
class SoundSettings:
    """
    Конфигурация звуковых настроек пользователя.
    
    Атрибуты:
        master_volume: общая громкость (0-100)
        category_volumes: громкость для каждой категории
        enabled_categories: включенные/отключенные категории
    """
    master_volume: int = 100
    category_volumes: Dict[str, int] = None
    enabled_categories: Dict[str, bool] = None
    
    def __post_init__(self):
        """Инициализация значений по умолчанию."""
        if self.category_volumes is None:
            self.category_volumes = {
                category.value: 100 for category in SoundEventCategory
            }
        
        if self.enabled_categories is None:
            self.enabled_categories = {
                category.value: True for category in SoundEventCategory
            }


class SoundConfigManager:
    """
    Менеджер для управления конфигурацией звуков.
    
    Сохраняет и загружает пользовательские настройки звуков из JSON файла.
    """
    
    DEFAULT_CONFIG_PATH = Path("config") / "sound_config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Инициализация менеджера конфигурации.
        
        Args:
            config_path: путь к файлу конфигурации (если None, используется DEFAULT_CONFIG_PATH)
        """
        self.config_path = Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.settings = self.load_settings()
    
    def load_settings(self) -> SoundSettings:
        """
        Загрузить настройки из файла конфигурации.
        
        Returns:
            Объект SoundSettings с загруженными настройками
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    settings = SoundSettings(
                        master_volume=data.get('master_volume', 100),
                        category_volumes=data.get('category_volumes', {}),
                        enabled_categories=data.get('enabled_categories', {})
                    )
                    logger.info(f"Настройки звуков загружены из {self.config_path}")
                    return settings
            except Exception as e:
                logger.error(f"Ошибка при загрузке конфигурации: {e}", exc_info=True)
        
        logger.info("Используются настройки по умолчанию")
        return SoundSettings()
    
    def save_settings(self, settings: SoundSettings) -> None:
        """
        Сохранить настройки в файл конфигурации.
        
        Args:
            settings: объект с настройками для сохранения
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                data = {
                    'master_volume': settings.master_volume,
                    'category_volumes': settings.category_volumes,
                    'enabled_categories': settings.enabled_categories
                }
                json.dump(data, f, indent=4, ensure_ascii=False)
                logger.info(f"Настройки сохранены в {self.config_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении конфигурации: {e}", exc_info=True)
