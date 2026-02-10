"""
Config Manager - Gestor de configuración del framework

Maneja la configuración del framework desde archivos JSON
y variables de entorno.

Autor: DAM2526
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Gestor de configuración que carga y valida la configuración
    del framework desde múltiples fuentes.
    """

    DEFAULT_CONFIG = {
        "database": {
            "format": "sqlite",
            "backup_enabled": True,
            "migration_on_startup": False
        },
        "api": {
            "enabled": True,
            "host": "localhost",
            "port": 5000,
            "cors_enabled": True,
            "jwt_secret": "default_secret_change_in_production"
        },
        "ui": {
            "enabled": True,
            "theme": "corporate",
            "language": "es",
            "auto_refresh": True,
            "window_size": "1200x800"
        },
        "business": {
            "loan_days_default": 14,
            "loan_limit_per_user": 3,
            "fine_per_day": 0.50
        },
        "entities": [
            "Book", "Author", "User", "Loan", "Category"
        ]
    }

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None, config_obj: Any = None):
        """
        Inicializar gestor de configuración.

        Args:
            config_dict: Configuración inicial como diccionario
            config_obj: Configuración inicial como objeto (FrameworkConfig)
        """
        self.config = self.DEFAULT_CONFIG.copy()

        # Si se pasa un objeto de configuración, convertirlo a diccionario
        if config_obj is not None:
            config_dict = self._config_obj_to_dict(config_obj)

        if config_dict:
            self._merge_config(config_dict)

        self._load_from_env()
        self._validate_config()

    def _config_obj_to_dict(self, config_obj: Any) -> Dict[str, Any]:
        """Convertir objeto de configuración a diccionario."""
        config_dict = {}

        # Mapeo de atributos del objeto a estructura de diccionario
        if hasattr(config_obj, 'database_format'):
            config_dict.setdefault('database', {})['format'] = config_obj.database_format

        if hasattr(config_obj, 'api_enabled'):
            config_dict.setdefault('api', {})['enabled'] = config_obj.api_enabled
        if hasattr(config_obj, 'api_host'):
            config_dict.setdefault('api', {})['host'] = config_obj.api_host
        if hasattr(config_obj, 'api_port'):
            config_dict.setdefault('api', {})['port'] = config_obj.api_port

        if hasattr(config_obj, 'ui_enabled'):
            config_dict.setdefault('ui', {})['enabled'] = config_obj.ui_enabled
        if hasattr(config_obj, 'ui_theme'):
            config_dict.setdefault('ui', {})['theme'] = config_obj.ui_theme

        if hasattr(config_obj, 'backup_enabled'):
            config_dict.setdefault('database', {})['backup_enabled'] = config_obj.backup_enabled

        if hasattr(config_obj, 'entities'):
            config_dict['entities'] = config_obj.entities

        return config_dict

    def _merge_config(self, new_config: Dict[str, Any]):
        """Fusionar configuración nueva con la existente."""
        def merge_dict(target: Dict, source: Dict):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value

        merge_dict(self.config, new_config)

    def _load_from_env(self):
        """Cargar configuración desde variables de entorno."""
        # Base de datos
        if os.getenv("DAF_DB_FORMAT"):
            self.config["database"]["format"] = os.getenv("DAF_DB_FORMAT")

        # API
        if os.getenv("DAF_API_HOST"):
            self.config["api"]["host"] = os.getenv("DAF_API_HOST")
        if os.getenv("DAF_API_PORT"):
            self.config["api"]["port"] = int(os.getenv("DAF_API_PORT"))

        # UI
        if os.getenv("DAF_UI_THEME"):
            self.config["ui"]["theme"] = os.getenv("DAF_UI_THEME")

    def _validate_config(self):
        """Validar configuración cargada."""
        # Validar formato de base de datos
        valid_formats = ["sqlite", "json", "xml", "csv", "txt"]
        if self.config["database"]["format"] not in valid_formats:
            raise ValueError(f"Formato de BD no válido: {self.config['database']['format']}")

        # Validar puerto API
        port = self.config["api"]["port"]
        if not isinstance(port, int) or not (1024 <= port <= 65535):
            raise ValueError(f"Puerto API no válido: {port}")

        # Validar tema UI
        valid_themes = ["corporate", "dark", "nature", "sunset"]
        if self.config["ui"]["theme"] not in valid_themes:
            raise ValueError(f"Tema UI no válido: {self.config['ui']['theme']}")

    def load_from_file(self, file_path: str):
        """
        Cargar configuración desde archivo JSON.

        Args:
            file_path: Ruta al archivo de configuración
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            file_config = json.load(f)

        self._merge_config(file_config)
        self._validate_config()

    def save_to_file(self, file_path: str):
        """
        Guardar configuración actual a archivo JSON.

        Args:
            file_path: Ruta donde guardar la configuración
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtener valor de configuración por ruta punteada.

        Args:
            key_path: Ruta punteada (ej: "database.format")
            default: Valor por defecto si no existe

        Returns:
            Valor de configuración
        """
        keys = key_path.split('.')
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any):
        """
        Establecer valor de configuración por ruta punteada.

        Args:
            key_path: Ruta punteada (ej: "database.format")
            value: Nuevo valor
        """
        keys = key_path.split('.')
        config = self.config

        # Navegar hasta el penúltimo nivel
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Establecer valor
        config[keys[-1]] = value

        # Revalidar configuración
        self._validate_config()

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Obtener sección completa de configuración.

        Args:
            section: Nombre de la sección

        Returns:
            Diccionario con la configuración de la sección
        """
        return self.config.get(section, {})

    def create_default_config_file(self, file_path: str):
        """
        Crear archivo de configuración por defecto.

        Args:
            file_path: Ruta donde crear el archivo
        """
        self.save_to_file(file_path)

    def __getitem__(self, key: str) -> Any:
        """Acceso directo por clave de sección."""
        return self.config[key]

    def __setitem__(self, key: str, value: Dict[str, Any]):
        """Establecimiento directo de sección."""
        self.config[key] = value
        self._validate_config()

    def __repr__(self):
        return f"ConfigManager(sections={list(self.config.keys())})"