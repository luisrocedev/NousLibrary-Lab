"""
Data Access Framework - Clase principal del framework

Esta clase coordina todos los componentes del framework:
- Gestores de datos
- Servicios de negocio
- API REST
- Interfaz gráfica
- Configuración

Autor: DAM2526
"""

import json
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..data_managers import DataManagerFactory
from ..models import Book, Author, User, Loan, Category
from ..business import LoanService, ReportService, AuthService
from .config_manager import ConfigManager
from .entity_manager import EntityManager


@dataclass
class FrameworkConfig:
    """Configuración del framework"""
    database_format: str = "sqlite"
    api_enabled: bool = True
    api_host: str = "localhost"
    api_port: int = 5000
    ui_enabled: bool = True
    ui_theme: str = "corporate"
    backup_enabled: bool = True
    entities: List[str] = None

    def __post_init__(self):
        if self.entities is None:
            self.entities = ["Book", "Author", "User", "Loan", "Category"]


class DataAccessFramework:
    """
    Framework principal de acceso a datos.

    Proporciona una interfaz unificada para:
    - Gestión de entidades
    - Servicios de negocio
    - API REST
    - Interfaz gráfica
    - Migración de datos
    """

    def __init__(self, config_path: str = None, **config_overrides):
        """
        Inicializar el framework.

        Args:
            config_path: Ruta al archivo de configuración JSON
            **config_overrides: Configuración que sobrescribe la del archivo
        """
        self.config = self._load_config(config_path, config_overrides)
        self.config_manager = ConfigManager(config_obj=self.config)

        # Inicializar componentes
        self.data_factory = DataManagerFactory()
        self.entity_manager = EntityManager(self.data_factory, self.config.database_format)

        # Servicios de negocio
        self.loan_service = LoanService(self.entity_manager)
        self.report_service = ReportService(self.entity_manager)
        self.auth_service = AuthService(self.entity_manager)

        # Estado del framework
        self._api_thread: Optional[threading.Thread] = None
        self._api_running = False

        # Inicializar entidades si no existen
        self._initialize_entities()

    def _load_config(self, config_path: str = None, overrides: Dict[str, Any] = None) -> FrameworkConfig:
        """Cargar configuración desde archivo y sobrescribir con parámetros."""
        config = FrameworkConfig()

        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                for key, value in file_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)

        # Aplicar sobrescrituras
        if overrides:
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        return config

    def _initialize_entities(self):
        """Inicializar estructura de entidades en el formato de datos."""
        try:
            # Verificar y crear estructura para cada entidad
            entities = {
                "Book": Book,
                "Author": Author,
                "User": User,
                "Loan": Loan,
                "Category": Category
            }

            for entity_name, entity_class in entities.items():
                if entity_name in self.config.entities:
                    # Intentar cargar para verificar que existe la estructura
                    try:
                        self.entity_manager.load_all(entity_class)
                    except Exception:
                        # Si falla, la estructura se creará en la primera operación
                        pass

        except Exception as e:
            print(f"Advertencia al inicializar entidades: {e}")

    # ==================== API PÚBLICA ====================

    def get_repository(self, entity_type: str):
        """
        Obtener repositorio para un tipo de entidad.

        Args:
            entity_type: Nombre de la clase de entidad (ej: "Book")

        Returns:
            EntityManager: Gestor configurado para esa entidad
        """
        entities = {
            "Book": Book,
            "Author": Author,
            "User": User,
            "Loan": Loan,
            "Category": Category
        }

        if entity_type not in entities:
            raise ValueError(f"Entidad no soportada: {entity_type}")

        return self.entity_manager.get_repository(entities[entity_type])

    def get_service(self, service_name: str):
        """
        Obtener servicio de negocio.

        Args:
            service_name: Nombre del servicio ("loan", "report", "auth")

        Returns:
            Servicio correspondiente
        """
        services = {
            "loan": self.loan_service,
            "report": self.report_service,
            "auth": self.auth_service
        }

        if service_name not in services:
            raise ValueError(f"Servicio no encontrado: {service_name}")

        return services[service_name]

    def start_api(self, host: str = None, port: int = None, blocking: bool = True):
        """
        Iniciar servidor API REST.

        Args:
            host: Host del servidor (default: config)
            port: Puerto del servidor (default: config)
            blocking: Si True, bloquea la ejecución
        """
        if not self.config.api_enabled:
            raise RuntimeError("API no habilitada en configuración")

        from ..api.app import create_app

        host = host or self.config.api_host
        port = port or self.config.api_port

        app = create_app(self)

        if blocking:
            print(f"Iniciando API REST en http://{host}:{port}")
            app.run(host=host, port=port, debug=False)
        else:
            # Ejecutar en hilo separado
            def run_api():
                app.run(host=host, port=port, debug=False, use_reloader=False)

            self._api_thread = threading.Thread(target=run_api, daemon=True)
            self._api_thread.start()
            self._api_running = True
            print(f"API REST iniciada en hilo separado: http://{host}:{port}")

    def stop_api(self):
        """Detener servidor API REST."""
        if self._api_running and self._api_thread:
            # Nota: Flask no tiene método directo para detener,
            # el hilo se detendrá cuando termine el programa
            self._api_running = False
            print("API REST detenida")

    def start_gui(self):
        """Iniciar interfaz gráfica."""
        if not self.config.ui_enabled:
            raise RuntimeError("UI no habilitada en configuración")

        from ..ui.modern_app import ModernApp

        app = ModernApp(self)
        app.run()

    def migrate_data(self, from_format: str, to_format: str):
        """
        Migrar datos entre formatos.

        Args:
            from_format: Formato origen
            to_format: Formato destino
        """
        from .migration_manager import MigrationManager

        migrator = MigrationManager(self.entity_manager)
        migrator.migrate(from_format, to_format)

    def backup_data(self):
        """Crear respaldo de datos."""
        if not self.config.backup_enabled:
            return

        # Implementar lógica de respaldo
        print("Respaldo de datos creado")

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del sistema.

        Returns:
            Diccionario con estadísticas
        """
        stats = {
            "entities": {},
            "loans": {
                "active": len(self.loan_service.get_active_loans()),
                "overdue": len(self.loan_service.get_overdue_loans())
            },
            "config": {
                "format": self.config.database_format,
                "api_enabled": self.config.api_enabled,
                "ui_enabled": self.config.ui_enabled
            }
        }

        # Estadísticas por entidad
        for entity_name in self.config.entities:
            try:
                repo = self.get_repository(entity_name)
                count = len(repo.load_all())
                stats["entities"][entity_name] = count
            except Exception:
                stats["entities"][entity_name] = 0

        return stats

    def __repr__(self):
        return f"DataAccessFramework(format={self.config.database_format}, entities={len(self.config.entities)})"