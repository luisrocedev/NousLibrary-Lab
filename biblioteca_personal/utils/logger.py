"""
Utilidades de logging para el Sistema de Gestión de Biblioteca Personal

Este módulo proporciona funcionalidades de logging centralizadas
para toda la aplicación.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

class Logger:
    """
    Clase para manejar el logging de la aplicación

    Proporciona logging tanto a consola como a archivo con diferentes
    niveles de severidad.
    """

    def __init__(self, log_file: str = "biblioteca.log", level: int = logging.INFO):
        """
        Inicializa el logger

        Args:
            log_file: Nombre del archivo de log
            level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger('BibliotecaPersonal')
        self.logger.setLevel(level)

        # Evitar duplicados de handlers
        if self.logger.handlers:
            return

        # Formato del log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler para archivo
        log_path = Path("logs") / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """Log a debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log an info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log a warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log a critical message"""
        self.logger.critical(message)

    def log_operation(self, operation: str, entity_type: str, entity_id: str = None, success: bool = True):
        """
        Log específico para operaciones CRUD

        Args:
            operation: Tipo de operación (CREATE, READ, UPDATE, DELETE)
            entity_type: Tipo de entidad (Book, Author, User)
            entity_id: ID de la entidad (opcional)
            success: Si la operación fue exitosa
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"{operation} {entity_type}"
        if entity_id:
            message += f" (ID: {entity_id})"
        message += f" - {status}"

        if success:
            self.info(message)
        else:
            self.error(message)

class ProgressLogger:
    """
    Logger para mostrar progreso de operaciones largas
    """

    def __init__(self, total_items: int, description: str = "Procesando"):
        """
        Inicializa el logger de progreso

        Args:
            total_items: Número total de items a procesar
            description: Descripción de la operación
        """
        self.total_items = total_items
        self.description = description
        self.processed = 0
        self.start_time = datetime.now()
        self.logger = Logger()

    def update(self, increment: int = 1):
        """
        Actualiza el progreso

        Args:
            increment: Número de items procesados en este paso
        """
        self.processed += increment
        percentage = (self.processed / self.total_items) * 100

        elapsed = datetime.now() - self.start_time
        if self.processed > 0:
            estimated_total = elapsed / (self.processed / self.total_items)
            remaining = estimated_total - elapsed
            eta = f" ETA: {remaining.seconds}s"
        else:
            eta = ""

        print(f"\r{self.description}: {self.processed}/{self.total_items} "
              ".1f"
              f"{eta}", end="", flush=True)

        if self.processed >= self.total_items:
            total_time = datetime.now() - self.start_time
            print(f"\nCompletado en {total_time.seconds}.{total_time.microseconds // 100000}s")
            self.logger.info(f"{self.description} completado: {self.total_items} items en "
                           f"{total_time.seconds}.{total_time.microseconds // 100000}s")