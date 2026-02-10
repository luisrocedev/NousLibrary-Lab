"""
Migration Manager - Gestor de migraciones entre formatos

Permite migrar datos completos entre diferentes formatos de almacenamiento,
manejando dependencias y validaciones.

Autor: DAM2526
"""

import shutil
from pathlib import Path
from typing import Type, List, Dict, Any
from datetime import datetime

from .entity_manager import EntityManager


class MigrationManager:
    """
    Gestor de migraciones que coordina la migración de datos
    entre diferentes formatos de almacenamiento.
    """

    def __init__(self, entity_manager: EntityManager):
        """
        Inicializar gestor de migraciones.

        Args:
            entity_manager: Gestor de entidades del framework
        """
        self.entity_manager = entity_manager
        self.migration_log = []

    def migrate(self, from_format: str, to_format: str, entities: List[str] = None):
        """
        Migrar datos entre formatos.

        Args:
            from_format: Formato origen
            to_format: Formato destino
            entities: Lista de entidades a migrar (todas si None)
        """
        if from_format == to_format:
            raise ValueError("Los formatos origen y destino deben ser diferentes")

        print(f"🔄 Iniciando migración: {from_format} → {to_format}")

        # Obtener entidades a migrar
        if entities is None:
            entities = ["Book", "Author", "User", "Loan", "Category"]

        # Mapear nombres de entidades a clases
        entity_classes = self._get_entity_classes()

        # Crear backup antes de migrar
        self._create_backup(from_format)

        migrated_count = 0
        errors = []

        # Migrar cada entidad
        for entity_name in entities:
            if entity_name in entity_classes:
                try:
                    print(f"  ↳ Migrando {entity_name}...")
                    count = self._migrate_entity(
                        entity_classes[entity_name],
                        from_format,
                        to_format
                    )
                    migrated_count += count
                    print(f"    ✅ {count} registros migrados")

                except Exception as e:
                    error_msg = f"Error migrando {entity_name}: {str(e)}"
                    print(f"    ❌ {error_msg}")
                    errors.append(error_msg)
                    self.migration_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "entity": entity_name,
                        "status": "error",
                        "message": str(e)
                    })

        # Log de migración completa
        self.migration_log.append({
            "timestamp": datetime.now().isoformat(),
            "operation": "migration_complete",
            "from_format": from_format,
            "to_format": to_format,
            "total_migrated": migrated_count,
            "errors": len(errors)
        })

        # Reporte final
        print(f"🎯 Migración completada: {migrated_count} registros migrados")
        if errors:
            print(f"⚠️  {len(errors)} errores encontrados")
            for error in errors:
                print(f"   - {error}")

        return {
            "success": len(errors) == 0,
            "migrated_count": migrated_count,
            "errors": errors
        }

    def _migrate_entity(self, entity_class: Type, from_format: str, to_format: str) -> int:
        """
        Migrar una entidad específica entre formatos.

        Args:
            entity_class: Clase de la entidad
            from_format: Formato origen
            to_format: Formato destino

        Returns:
            Número de registros migrados
        """
        # Usar el método del EntityManager
        self.entity_manager.migrate_entity(entity_class, from_format, to_format)

        # Verificar migración contando registros en destino
        dest_repo = self.entity_manager.get_repository(entity_class)
        return len(dest_repo.load_all())

    def _get_entity_classes(self) -> Dict[str, Type]:
        """Obtener mapa de nombres de entidades a clases."""
        from ..models import Book, Author, User, Loan, Category

        return {
            "Book": Book,
            "Author": Author,
            "User": User,
            "Loan": Loan,
            "Category": Category
        }

    def _create_backup(self, format_type: str):
        """
        Crear backup de datos antes de migración.

        Args:
            format_type: Formato a respaldar
        """
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{format_type}_{timestamp}"

            # Para formatos de archivo, copiar directorio data
            if format_type in ["json", "xml", "csv", "txt"]:
                data_dir = Path("data")
                if data_dir.exists():
                    backup_path = backup_dir / backup_name
                    shutil.copytree(data_dir, backup_path)
                    print(f"💾 Backup creado: {backup_path}")

            # Para SQLite, copiar archivo de BD
            elif format_type == "sqlite":
                db_file = Path("data/library.db")
                if db_file.exists():
                    backup_path = backup_dir / f"{backup_name}.db"
                    shutil.copy2(db_file, backup_path)
                    print(f"💾 Backup creado: {backup_path}")

        except Exception as e:
            print(f"⚠️  Error creando backup: {e}")

    def validate_migration(self, from_format: str, to_format: str) -> Dict[str, Any]:
        """
        Validar que una migración es posible.

        Args:
            from_format: Formato origen
            to_format: Formato destino

        Returns:
            Diccionario con resultado de validación
        """
        issues = []

        # Verificar que los formatos son soportados
        supported_formats = ["sqlite", "json", "xml", "csv", "txt"]
        if from_format not in supported_formats:
            issues.append(f"Formato origen no soportado: {from_format}")
        if to_format not in supported_formats:
            issues.append(f"Formato destino no soportado: {to_format}")

        # Verificar que existen datos en el origen
        entity_classes = self._get_entity_classes()
        total_records = 0

        for entity_name, entity_class in entity_classes.items():
            try:
                repo = self.entity_manager.get_repository(entity_class)
                count = len(repo.load_all())
                total_records += count
            except Exception:
                pass

        if total_records == 0:
            issues.append("No se encontraron datos para migrar")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_records": total_records
        }

    def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Obtener historial de migraciones realizadas.

        Returns:
            Lista de migraciones con metadata
        """
        return self.migration_log.copy()

    def rollback_migration(self, migration_id: str):
        """
        Revertir una migración (funcionalidad futura).

        Args:
            migration_id: ID de la migración a revertir
        """
        # Implementar rollback usando backups
        raise NotImplementedError("Rollback de migraciones no implementado aún")