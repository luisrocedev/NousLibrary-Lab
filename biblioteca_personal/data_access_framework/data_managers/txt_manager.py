"""
Gestor de datos genérico para archivos de texto plano (.txt)

Este módulo implementa el manejo de datos usando archivos de texto
con formato estructurado para almacenar entidades.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
import logging

from . import DataManager


class TXTDataManager(DataManager):
    """
    Gestor genérico de datos para archivos TXT
    """

    def __init__(self, entity_class: Type, base_path: str = "data"):
        super().__init__(base_path)
        self.entity_class = entity_class
        self.entity_name = entity_class.__name__.lower()
        self.file_path = self.base_path / f"{self.entity_name}s.txt"
        self.logger = logging.getLogger(__name__)

    def _save_all_entities(self, entities: List) -> bool:
        """Guarda todas las entidades en el archivo TXT"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                for entity in entities:
                    # Convertir entidad a dict y luego a JSON
                    entity_dict = entity.to_dict()
                    json_line = json.dumps(entity_dict, ensure_ascii=False)
                    f.write(json_line + '\n')
            return True
        except Exception as e:
            self.logger.error(f"Error guardando {self.entity_name}s TXT: {e}")
            return False

    def _load_all_raw(self) -> List[Dict[str, Any]]:
        """Cargar datos crudos del archivo TXT."""
        if not self.file_path.exists():
            return []

        entities_data = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entity_dict = json.loads(line)
                            entities_data.append(entity_dict)
                        except json.JSONDecodeError as e:
                            self.logger.error(f"Error decodificando línea TXT: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo {self.entity_name}s TXT: {e}")

        return entities_data

    def save(self, entity) -> bool:
        """Guarda una entidad en archivo TXT"""
        try:
            # Cargar todas las entidades existentes
            entities = self.load_all()

            # Actualizar o agregar la entidad
            found = False
            for i, e in enumerate(entities):
                if e.id == entity.id:
                    entities[i] = entity
                    found = True
                    break

            if not found:
                entities.append(entity)

            # Guardar todas las entidades
            return self._save_all_entities(entities)

        except Exception as e:
            self.logger.error(f"Error guardando {self.entity_name} TXT: {e}")
            return False

    def load(self, entity_id: str):
        """Carga una entidad desde archivo TXT"""
        try:
            entities = self.load_all()
            for entity in entities:
                if entity.id == entity_id:
                    return entity
            return None
        except Exception as e:
            self.logger.error(f"Error cargando {self.entity_name} TXT: {e}")
            return None

    def load_all(self) -> List:
        """Carga todas las entidades desde archivo TXT"""
