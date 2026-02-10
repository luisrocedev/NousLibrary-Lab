"""
Gestor de datos genérico para base de datos SQLite (.db)

Implementa el almacenamiento de datos usando SQLite3 de la librería estándar
de Python, con tablas relacionales.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
import logging
import json
from datetime import datetime

from . import DataManager


class DBDataManager(DataManager):
    """Gestor genérico de datos en base de datos SQLite"""

    def __init__(self, entity_class: Type, base_path: str = "data"):
        super().__init__(base_path)
        self.entity_class = entity_class
        self.entity_name = entity_class.__name__.lower()
        self.db_path = self.base_path / "data.db"
        self.logger = logging.getLogger(__name__)

        # Crear tabla si no existe
        self._create_table()

    def _get_conn(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_table(self):
        """Crear tabla para la entidad si no existe."""
        # Obtener estructura de la tabla de la clase
        if hasattr(self.entity_class, 'DB_SCHEMA'):
            schema = self.entity_class.DB_SCHEMA
        else:
            # Schema básico por defecto
            schema = f"""
                CREATE TABLE IF NOT EXISTS {self.entity_name}s (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
            """

        conn = self._get_conn()
        try:
            conn.execute(schema)
            conn.commit()
        except Exception as e:
            self.logger.error(f"Error creando tabla {self.entity_name}s: {e}")
        finally:
            conn.close()

    def _entity_to_db_row(self, entity) -> Dict[str, Any]:
        """Convertir entidad a fila de base de datos."""
        if hasattr(self.entity_class, 'DB_SCHEMA'):
            # Si tiene schema personalizado, usar campos específicos
            entity_dict = entity.to_dict()
            return entity_dict
        else:
            # Usar JSON serializado por defecto
            return {
                'id': entity.id,
                'data': json.dumps(entity.to_dict(), ensure_ascii=False)
            }

    def _db_row_to_entity_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convertir fila de DB a diccionario de entidad."""
        if hasattr(self.entity_class, 'DB_SCHEMA'):
            # Si tiene schema personalizado, devolver campos directos
            return dict(row)
        else:
            # Deserializar JSON por defecto
            return json.loads(row['data'])

    def save(self, entity) -> bool:
        try:
            conn = self._get_conn()
            row_data = self._entity_to_db_row(entity)

            # Usar INSERT OR REPLACE para upsert
            columns = ', '.join(row_data.keys())
            placeholders = ', '.join(['?' for _ in row_data])
            values = list(row_data.values())

            sql = f"""
                INSERT OR REPLACE INTO {self.entity_name}s ({columns})
                VALUES ({placeholders})
            """

            conn.execute(sql, values)
            conn.commit()
            return True

        except Exception as e:
            self.logger.error(f"Error guardando {self.entity_name} DB: {e}")
            return False
        finally:
            conn.close()

    def load(self, entity_id: str):
        try:
            conn = self._get_conn()
            cursor = conn.execute(
                f"SELECT * FROM {self.entity_name}s WHERE id = ?",
                (entity_id,)
            )
            row = cursor.fetchone()

            if row:
                entity_dict = self._db_row_to_entity_dict(row)
                return self.entity_class.from_dict(entity_dict)
            return None

        except Exception as e:
            self.logger.error(f"Error cargando {self.entity_name} DB: {e}")
            return None
        finally:
            conn.close()

    def load_all(self) -> List:
        """Cargar todas las entidades."""
        try:
            conn = self._get_conn()
            cursor = conn.execute(f"SELECT * FROM {self.entity_name}s")
            rows = cursor.fetchall()

            entities = []
            for row in rows:
                entity_dict = self._db_row_to_entity_dict(row)
                entities.append(self.entity_class.from_dict(entity_dict))

            return entities

        except Exception as e:
            self.logger.error(f"Error cargando todas las {self.entity_name}s DB: {e}")
            return []
        finally:
            conn.close()

    def delete(self, entity_id: str) -> bool:
        """Eliminar una entidad."""
        try:
            conn = self._get_conn()
            cursor = conn.execute(
                f"DELETE FROM {self.entity_name}s WHERE id = ?",
                (entity_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            self.logger.error(f"Error eliminando {self.entity_name} DB: {e}")
            return False
        finally:
            conn.close()

    def search(self, criteria: Dict[str, Any]) -> List:
        """Buscar entidades por criterios."""
        try:
            conn = self._get_conn()

            # Construir consulta WHERE
            where_parts = []
            params = []

            for key, value in criteria.items():
                if key in ['id', 'title', 'name', 'email', 'isbn', 'author_id', 'user_id', 'book_id']:
                    where_parts.append(f"{key} LIKE ?")
                    params.append(f"%{value}%")
                elif key in ['available', 'active', 'overdue']:
                    where_parts.append(f"{key} = ?")
                    params.append(1 if value else 0)
                elif key in ['loan_date', 'return_date', 'created_at']:
                    # Para fechas, buscar por rango o exacta
                    if isinstance(value, dict):
                        if 'start' in value:
                            where_parts.append(f"{key} >= ?")
                            params.append(value['start'])
                        if 'end' in value:
                            where_parts.append(f"{key} <= ?")
                            params.append(value['end'])
                    else:
                        where_parts.append(f"{key} = ?")
                        params.append(value)

            where_clause = " AND ".join(where_parts) if where_parts else "1=1"

            query = f"SELECT * FROM {self.entity_name}s WHERE {where_clause}"
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            entities = []
            for row in rows:
                entity_dict = self._db_row_to_entity_dict(row)
                entities.append(self.entity_class.from_dict(entity_dict))

            return entities

        except Exception as e:
            self.logger.error(f"Error buscando {self.entity_name}s DB: {e}")
            return []
        finally:
            conn.close()
