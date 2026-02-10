#!/usr/bin/env python3
"""
Script para crear datos de prueba para la aplicación de biblioteca
"""

import sys
from pathlib import Path

# Añadir raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from data_managers import DataManagerFactory
from models import Author, Book, User

def create_test_data():
    """Crear datos de prueba"""

    # Crear managers
    author_mgr = DataManagerFactory.create_author_manager('json')
    book_mgr = DataManagerFactory.create_book_manager('json')
    user_mgr = DataManagerFactory.create_user_manager('json')

    # Crear autores de prueba
    author1 = Author(name='Gabriel García Márquez', nationality='Colombiano', biography='Premio Nobel de Literatura')
    author2 = Author(name='Isabel Allende', nationality='Chilena', biography='Escritora chilena')

    author_mgr.save(author1)
    author_mgr.save(author2)

    # Crear libros de prueba
    book1 = Book(title='Cien años de soledad', author_id=author1.id, isbn='', publication_year=1967, genre='Novela', language='Español')
    book2 = Book(title='La casa de los espíritus', author_id=author2.id, isbn='', publication_year=1982, genre='Novela', language='Español')

    book_mgr.save(book1)
    book_mgr.save(book2)

    # Crear usuarios de prueba
    user1 = User(name='Juan Pérez', email='juan@example.com', phone='123456789', address='Calle Principal 123')
    user2 = User(name='María García', email='maria@example.com', phone='987654321', address='Avenida Central 456')

    user_mgr.save(user1)
    user_mgr.save(user2)

    print('Datos de prueba creados exitosamente')

if __name__ == '__main__':
    create_test_data()