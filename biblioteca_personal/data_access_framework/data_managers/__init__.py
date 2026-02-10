"""
Data Managers - Gestores de datos por formato

Proporciona fábricas y gestores para diferentes formatos de datos.

Autor: DAM2526
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
import os
from pathlib import Path


class DataManager(ABC):
    """Interfaz base para gestores de datos."""

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    @abstractmethod
    def save(self, entity) -> bool:
        """Guardar una entidad."""
        pass

    @abstractmethod
    def load(self, entity_id: str):
        """Cargar una entidad por ID."""
        pass

    @abstractmethod
    def load_all(self) -> List:
        """Cargar todas las entidades."""
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Eliminar una entidad."""
        pass

    @abstractmethod
    def search(self, criteria: Dict[str, Any]) -> List:
        """Buscar entidades por criterios."""
        pass


class DataManagerFactory:
    """Fábrica para crear gestores de datos."""

    _managers = {}

    @classmethod
    def register_manager(cls, format_type: str, manager_class: Type[DataManager]):
        """Registrar un gestor para un formato."""
        cls._managers[format_type.lower()] = manager_class

    @classmethod
    def create_manager(cls, format_type: str, entity_class: Type, base_path: str = "data") -> DataManager:
        """Crear un gestor para un tipo de entidad y formato."""
        format_type = format_type.lower()
        if format_type not in cls._managers:
            raise ValueError(f"Formato no soportado: {format_type}")

        manager_class = cls._managers[format_type]
        return manager_class(entity_class, base_path)


# Importar gestores específicos
from .json_manager import JSONDataManager
from .xml_manager import XMLDataManager
from .csv_manager import CSVDataManager
from .txt_manager import TXTDataManager
from .db_manager import DBDataManager

# Registrar gestores
DataManagerFactory.register_manager('json', JSONDataManager)
DataManagerFactory.register_manager('xml', XMLDataManager)
DataManagerFactory.register_manager('csv', CSVDataManager)
DataManagerFactory.register_manager('txt', TXTDataManager)
DataManagerFactory.register_manager('sqlite', DBDataManager)
DataManagerFactory.register_manager('db', DBDataManager)