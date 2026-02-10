"""
Gestor de datos genérico para archivos XML (.xml)

Implementa el almacenamiento de datos usando archivos XML con
xml.etree.ElementTree de la librería estándar de Python.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
import logging

from . import DataManager


def _prettify(elem: ET.Element) -> str:
    """Devuelve un XML con indentación legible"""
    rough = ET.tostring(elem, encoding='unicode')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ")


def _dict_to_xml(parent: ET.Element, tag: str, data: dict) -> ET.Element:
    """Convierte un diccionario en un subelemento XML"""
    elem = ET.SubElement(parent, tag)
    for k, v in data.items():
        child = ET.SubElement(elem, k)
        if isinstance(v, list):
            child.text = ';'.join(str(x) for x in v)
        elif v is None:
            child.text = ''
        else:
            child.text = str(v)
    return elem


def _xml_to_dict(elem: ET.Element) -> dict:
    """Convierte un elemento XML en diccionario"""
    d = {}
    for child in elem:
        text = child.text if child.text else ''
        d[child.tag] = text
    return d


class XMLDataManager(DataManager):
    """Gestor genérico de datos en formato XML"""

    def __init__(self, entity_class: Type, base_path: str = "data"):
        super().__init__(base_path)
        self.entity_class = entity_class
        self.entity_name = entity_class.__name__.lower()
        self.file_path = self.base_path / f"{self.entity_name}s.xml"
        self.logger = logging.getLogger(__name__)

    def _write_all(self, entities: List) -> bool:
        try:
            root = ET.Element(f"{self.entity_name}s")
            for entity in entities:
                _dict_to_xml(root, self.entity_name, entity.to_dict())

            xml_str = _prettify(root)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo XML {self.entity_name}s: {e}")
            return False

    def _load_all_raw(self) -> List[Dict[str, Any]]:
        """Cargar datos crudos del archivo XML."""
        if not self.file_path.exists():
            return []

        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            return [_xml_to_dict(child) for child in root]
        except Exception as e:
            self.logger.error(f"Error leyendo XML {self.entity_name}s: {e}")
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
            self.logger.error(f"Error guardando {self.entity_name} XML: {e}")
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
            self.logger.error(f"Error eliminando {self.entity_name} XML: {e}")
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
