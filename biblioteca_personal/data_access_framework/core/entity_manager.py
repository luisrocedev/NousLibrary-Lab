"""
Entity Manager - Gestor genérico de entidades

Proporciona una interfaz unificada para operaciones CRUD
sobre cualquier tipo de entidad, abstrayendo el formato de almacenamiento.

Autor: DAM2526
"""

from typing import Type, TypeVar, Generic, List, Optional, Any, Dict
from abc import ABC, abstractmethod

from ..data_managers import DataManagerFactory

T = TypeVar('T')


class Repository(Generic[T]):
    """
    Repositorio genérico para operaciones CRUD sobre una entidad.
    """

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def save(self, entity: T) -> bool:
        """Guardar entidad."""
        return self.data_manager.save(entity)

    def load(self, entity_id: str) -> Optional[T]:
        """Cargar entidad por ID."""
        return self.data_manager.load(entity_id)

    def load_all(self) -> List[T]:
        """Cargar todas las entidades."""
        return self.data_manager.load_all()

    def delete(self, entity_id: str) -> bool:
        """Eliminar entidad por ID."""
        return self.data_manager.delete(entity_id)

    def exists(self, entity_id: str) -> bool:
        """Verificar si entidad existe."""
        return self.data_manager.exists(entity_id)

    def find_by(self, **criteria) -> List[T]:
        """
        Buscar entidades por criterios.

        Args:
            **criteria: Criterios de búsqueda (ej: name="Juan", active=True)

        Returns:
            Lista de entidades que cumplen los criterios
        """
        all_entities = self.load_all()
        results = []

        for entity in all_entities:
            match = True
            for key, value in criteria.items():
                if not hasattr(entity, key) or getattr(entity, key) != value:
                    match = False
                    break
            if match:
                results.append(entity)

        return results


class EntityManager:
    """
    Gestor central de entidades que coordina repositorios
    para diferentes tipos de entidades.
    """

    def __init__(self, data_factory: DataManagerFactory, default_format: str = "sqlite"):
        """
        Inicializar gestor de entidades.

        Args:
            data_factory: Factory de gestores de datos
            default_format: Formato de datos por defecto
        """
        self.data_factory = data_factory
        self.default_format = default_format
        self._repositories = {}

    def get_repository(self, entity_class: Type[T]) -> Repository[T]:
        """
        Obtener repositorio para una clase de entidad.

        Args:
            entity_class: Clase de la entidad

        Returns:
            Repository configurado para esa entidad
        """
        entity_name = entity_class.__name__

        if entity_name not in self._repositories:
            # Crear gestor de datos para esta entidad
            data_manager = self.data_factory.create_manager(
                self.default_format,
                entity_class
            )
            self._repositories[entity_name] = Repository(data_manager)

        return self._repositories[entity_name]

    def migrate_entity(self, entity_class: Type[T], from_format: str, to_format: str):
        """
        Migrar datos de una entidad entre formatos.

        Args:
            entity_class: Clase de la entidad
            from_format: Formato origen
            to_format: Formato destino
        """
        # Cargar datos del formato origen
        from_manager = self.data_factory.create_manager(from_format, entity_class)
        entities = from_manager.load_all()

        # Guardar en formato destino
        to_manager = self.data_factory.create_manager(to_format, entity_class)
        for entity in entities:
            to_manager.save(entity)

    def get_entity_stats(self, entity_class: Type[T]) -> Dict[str, Any]:
        """
        Obtener estadísticas de una entidad.

        Args:
            entity_class: Clase de la entidad

        Returns:
            Diccionario con estadísticas
        """
        repo = self.get_repository(entity_class)
        entities = repo.load_all()

        stats = {
            "count": len(entities),
            "entity_type": entity_class.__name__
        }

        # Estadísticas específicas según el tipo de entidad
        if hasattr(entity_class, '__annotations__'):
            stats["fields"] = list(entity_class.__annotations__.keys())

        return stats

    def validate_entity(self, entity: T) -> List[str]:
        """
        Validar entidad según sus reglas de negocio.

        Args:
            entity: Instancia de entidad a validar

        Returns:
            Lista de errores de validación
        """
        errors = []

        # Validación básica de campos requeridos
        if hasattr(entity, '__dataclass_fields__'):
            for field_name, field_info in entity.__dataclass_fields__.items():
                value = getattr(entity, field_name)
                # Aquí se podrían agregar validaciones más específicas
                # según el tipo de campo y entidad

        return errors