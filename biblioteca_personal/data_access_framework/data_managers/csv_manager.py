"""
Gestor de datos genérico para archivos CSV (.csv)

Implementa el almacenamiento de datos usando archivos CSV (Comma Separated Values)
con cabeceras, utilizando csv.DictReader y csv.DictWriter de la librería estándar.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
import logging

from . import DataManager


class CSVDataManager(DataManager):
    """Gestor genérico de datos en formato CSV"""

    def __init__(self, entity_class: Type, base_path: str = "data"):
        super().__init__(base_path)
        self.entity_class = entity_class
        self.entity_name = entity_class.__name__.lower()
        self.file_path = self.base_path / f"{self.entity_name}s.csv"
        self.logger = logging.getLogger(__name__)

        # Obtener fieldnames de la clase
        if hasattr(entity_class, 'CSV_FIELDNAMES'):
            self.fieldnames = entity_class.CSV_FIELDNAMES
        else:
            # Intentar obtener de una instancia de ejemplo
            try:
                example = entity_class()
                self.fieldnames = list(example.to_dict().keys())
            except:
                self.fieldnames = ['id']  # fallback mínimo

    def _write_all(self, entities: List) -> bool:
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                for entity in entities:
                    writer.writerow(entity.to_dict())
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo CSV {self.entity_name}s: {e}")
            return False

    def _load_all_raw(self) -> List[Dict[str, Any]]:
        """Cargar datos crudos del archivo CSV."""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            self.logger.error(f"Error leyendo CSV {self.entity_name}s: {e}")
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
            self.logger.error(f"Error guardando {self.entity_name} CSV: {e}")
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
            self.logger.error(f"Error eliminando {self.entity_name} CSV: {e}")
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

        return results
