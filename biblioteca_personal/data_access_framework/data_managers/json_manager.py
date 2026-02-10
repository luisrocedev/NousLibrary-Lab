"""
Gestor de datos genérico para archivos JSON (.json)

Implementa el almacenamiento de datos usando archivos JSON nativos
con la librería estándar json de Python.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
import logging

from . import DataManager


class JSONDataManager(DataManager):
    """Gestor genérico de datos en formato JSON"""

    def __init__(self, entity_class: Type, base_path: str = "data"):
        super().__init__(base_path)
        self.entity_class = entity_class
        self.entity_name = entity_class.__name__.lower()
        self.file_path = self.base_path / f"{self.entity_name}s.json"
        self.logger = logging.getLogger(__name__)

    def _write_all(self, entities: List) -> bool:
        try:
            data = {f"{self.entity_name}s": [e.to_dict() for e in entities]}
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo JSON {self.entity_name}s: {e}")
            return False

    def _load_all_raw(self) -> List[Dict[str, Any]]:
        """Cargar datos crudos del archivo JSON."""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get(f"{self.entity_name}s", [])
        except Exception as e:
            self.logger.error(f"Error leyendo JSON {self.entity_name}s: {e}")
            return []

    def save(self, entity) -> bool:
        try:
            entities = self.load_all()
            found = False
            for i, e in enumerate(entities):
                if e.id == entity.id:
                    entities[i] = entity
                    found = True
                    break
            if not found:
                entities.append(entity)
            return self._write_all(entities)
        except Exception as e:
            self.logger.error(f"Error guardando {self.entity_name} JSON: {e}")
            return False

    def load(self, entity_id: str):
        for e in self.load_all():
            if e.id == entity_id:
                return e
        return None

    def load_all(self) -> List:
        raw_data = self._load_all_raw()
        entities = []
        for item in raw_data:
            try:
                entity = self.entity_class.from_dict(item)
                entities.append(entity)
            except Exception as e:
                self.logger.error(f"Error creando {self.entity_name} desde dict: {e}")
        return entities

    def delete(self, entity_id: str) -> bool:
        try:
            entities = self.load_all()
            entities = [e for e in entities if e.id != entity_id]
            return self._write_all(entities)
        except Exception as e:
            self.logger.error(f"Error eliminando {self.entity_name} JSON: {e}")
            return False

    def search(self, criteria: Dict[str, Any]) -> List:
        entities = self.load_all()
        results = []

        for entity in entities:
            match = True
            for key, value in criteria.items():
                if not hasattr(entity, key):
                    match = False
                    break

                entity_value = getattr(entity, key)
                if isinstance(value, str) and isinstance(entity_value, str):
                    if value.lower() not in entity_value.lower():
                        match = False
                        break
                elif entity_value != value:
                    match = False
                    break

            if match:
                results.append(entity)

