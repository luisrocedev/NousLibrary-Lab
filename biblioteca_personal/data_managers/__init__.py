"""
Gestores de datos base para el Sistema de Gestión de Biblioteca Personal

Este módulo define la interfaz base y clases abstractas para los gestores
de datos que manejan diferentes formatos de archivo.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
from pathlib import Path
import os

from models import Book, Author, User
from utils.logger import Logger

T = TypeVar('T')  # Tipo genérico para entidades

class DataManager(ABC, Generic[T]):
    """
    Clase base abstracta para gestores de datos

    Define la interfaz común para todas las implementaciones de gestores
    de datos, independientemente del formato de archivo utilizado.
    """

    def __init__(self, base_path: str = "data"):
        """
        Inicializa el gestor de datos

        Args:
            base_path: Ruta base donde se almacenarán los archivos
        """
        self.base_path = Path(base_path)
        self.logger = Logger()

        # Crear directorio base si no existe
        self.base_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def save(self, entity: T) -> bool:
        """
        Guarda una entidad en el almacenamiento

        Args:
            entity: Entidad a guardar

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        pass

    @abstractmethod
    def load(self, entity_id: str) -> Optional[T]:
        """
        Carga una entidad desde el almacenamiento

        Args:
            entity_id: ID de la entidad a cargar

        Returns:
            Optional[T]: Entidad cargada o None si no existe
        """
        pass

    @abstractmethod
    def load_all(self) -> List[T]:
        """
        Carga todas las entidades del almacenamiento

        Returns:
            List[T]: Lista de todas las entidades
        """
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """
        Elimina una entidad del almacenamiento

        Args:
            entity_id: ID de la entidad a eliminar

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        pass

    @abstractmethod
    def exists(self, entity_id: str) -> bool:
        """
        Verifica si una entidad existe en el almacenamiento

        Args:
            entity_id: ID de la entidad a verificar

        Returns:
            bool: True si existe, False en caso contrario
        """
        pass

    @abstractmethod
    def search(self, criteria: Dict[str, Any]) -> List[T]:
        """
        Busca entidades que cumplan con los criterios especificados

        Args:
            criteria: Diccionario con los criterios de búsqueda

        Returns:
            List[T]: Lista de entidades que cumplen los criterios
        """
        pass

class BookDataManager(DataManager[Book]):
    """
    Gestor específico para libros
    """
    pass

class AuthorDataManager(DataManager[Author]):
    """
    Gestor específico para autores
    """
    pass

class UserDataManager(DataManager[User]):
    """
    Gestor específico para usuarios
    """
    pass

class DataManagerFactory:
    """
    Factory para crear instancias de gestores de datos

    Permite crear gestores de datos para diferentes formatos de archivo
    de manera centralizada.
    """

    @staticmethod
    def create_book_manager(format_type: str, base_path: str = "data") -> BookDataManager:
        format_type = format_type.lower()
        if format_type == 'txt':
            from .txt_manager import TXTBookDataManager
            return TXTBookDataManager(base_path)
        elif format_type == 'csv':
            from .csv_manager import CSVBookDataManager
            return CSVBookDataManager(base_path)
        elif format_type == 'json':
            from .json_manager import JSONBookDataManager
            return JSONBookDataManager(base_path)
        elif format_type == 'xml':
            from .xml_manager import XMLBookDataManager
            return XMLBookDataManager(base_path)
        elif format_type == 'db':
            from .db_manager import DBBookDataManager
            return DBBookDataManager(base_path)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")

    @staticmethod
    def create_author_manager(format_type: str, base_path: str = "data") -> AuthorDataManager:
        format_type = format_type.lower()
        if format_type == 'txt':
            from .txt_manager import TXTAuthorDataManager
            return TXTAuthorDataManager(base_path)
        elif format_type == 'csv':
            from .csv_manager import CSVAuthorDataManager
            return CSVAuthorDataManager(base_path)
        elif format_type == 'json':
            from .json_manager import JSONAuthorDataManager
            return JSONAuthorDataManager(base_path)
        elif format_type == 'xml':
            from .xml_manager import XMLAuthorDataManager
            return XMLAuthorDataManager(base_path)
        elif format_type == 'db':
            from .db_manager import DBAuthorDataManager
            return DBAuthorDataManager(base_path)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")

    @staticmethod
    def create_user_manager(format_type: str, base_path: str = "data") -> UserDataManager:
        format_type = format_type.lower()
        if format_type == 'txt':
            from .txt_manager import TXTUserDataManager
            return TXTUserDataManager(base_path)
        elif format_type == 'csv':
            from .csv_manager import CSVUserDataManager
            return CSVUserDataManager(base_path)
        elif format_type == 'json':
            from .json_manager import JSONUserDataManager
            return JSONUserDataManager(base_path)
        elif format_type == 'xml':
            from .xml_manager import XMLUserDataManager
            return XMLUserDataManager(base_path)
        elif format_type == 'db':
            from .db_manager import DBUserDataManager
            return DBUserDataManager(base_path)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")