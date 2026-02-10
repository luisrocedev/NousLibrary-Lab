#!/usr/bin/env python3
"""
Sistema de Gestión de Biblioteca Personal
Aplicación principal con interfaz gráfica moderna (ttkbootstrap)
Soporte multi-formato: TXT, CSV, JSON, XML, SQLite

Autor: DAM2526
Fecha: Diciembre 2024
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path para importar módulos locales
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import Logger


def main():
    """
    Función principal - Lanza la interfaz gráfica moderna con ttkbootstrap
    """
    logger = Logger()

    try:
        logger.info("Iniciando Sistema de Gestión de Biblioteca Personal (GUI)")

        # Importar y lanzar la interfaz gráfica
        from gui_app import BibliotecaApp
        app = BibliotecaApp()
        app.run()

    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
        print("\n¡Hasta luego!")
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {str(e)}")
        print(f"Error crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()