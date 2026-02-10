"""
Data Access Framework - Framework genérico de acceso a datos

Este framework proporciona una abstracción completa para el acceso a datos
en múltiples formatos, con API REST, interfaz gráfica moderna y servicios
de negocio reutilizables.

Autor: DAM2526 - DNI: 53945291X
Versión: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "DAM2526"
__description__ = "Framework genérico de acceso a datos con múltiples formatos"

from .core.entity_manager import EntityManager
from .core.data_access_framework import DataAccessFramework
from .models import Book, Author, User, Loan, Category
from .business import LoanService, ReportService, AuthService

# API pública principal
__all__ = [
    'DataAccessFramework',
    'EntityManager',
    'Book', 'Author', 'User', 'Loan', 'Category',
    'LoanService', 'ReportService', 'AuthService'
]

# Función de conveniencia para crear framework rápidamente
def create_framework(config_path: str = None, **config):
    """
    Crea una instancia del framework con configuración opcional.

    Args:
        config_path: Ruta al archivo de configuración JSON
        **config: Configuración directa como parámetros

    Returns:
        DataAccessFramework: Instancia configurada del framework
    """
    return DataAccessFramework(config_path=config_path, **config)