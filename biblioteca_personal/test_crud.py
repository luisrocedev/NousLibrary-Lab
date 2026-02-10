#!/usr/bin/env python3
"""
Script de prueba para verificar las funcionalidades CRUD mejoradas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_managers import DataManagerFactory
from models import Book, Author, User
from utils.logger import Logger

def test_crud_operations():
    """Prueba las operaciones CRUD con énfasis en eliminación"""

    # Crear logger
    logger = Logger()

    # Crear managers para diferentes formatos
    formats = ['json', 'txt', 'csv', 'xml', 'db']
    managers = {}

    for fmt in formats:
        managers[fmt] = {
            'books': DataManagerFactory.create_book_manager(fmt),
            'authors': DataManagerFactory.create_author_manager(fmt),
            'users': DataManagerFactory.create_user_manager(fmt)
        }

    print("=== PRUEBA DE OPERACIONES CRUD ===\n")

    # Crear datos de prueba
    from datetime import datetime
    author1 = Author(id="1", name="Gabriel García Márquez", birth_date=datetime(1927, 3, 6), nationality="Colombiano")
    author2 = Author(id="2", name="Mario Vargas Llosa", birth_date=datetime(1936, 3, 28), nationality="Peruano")

    book1 = Book(id="1", title="Cien años de soledad", author_id="1", publication_year=1967, genre="Novela")
    book2 = Book(id="2", title="La ciudad y los perros", author_id="2", publication_year=1962, genre="Novela")

    user1 = User(id="1", name="Admin User", email="admin@example.com")
    user2 = User(id="2", name="Regular User", email="user@example.com")

    for fmt in formats:
        print(f"--- Probando formato: {fmt.upper()} ---")

        book_mgr = managers[fmt]['books']
        author_mgr = managers[fmt]['authors']
        user_mgr = managers[fmt]['users']

        try:
            # Limpiar datos existentes
            for book in book_mgr.load_all():
                book_mgr.delete(book.id)
            for author in author_mgr.load_all():
                author_mgr.delete(author.id)
            for user in user_mgr.load_all():
                user_mgr.delete(user.id)

            # Crear autores
            print("Creando autores...")
            author_mgr.save(author1)
            author_mgr.save(author2)
            print(f"✓ Autores creados: {len(author_mgr.load_all())}")

            # Crear libros
            print("Creando libros...")
            book_mgr.save(book1)
            book_mgr.save(book2)
            print(f"✓ Libros creados: {len(book_mgr.load_all())}")

            # Crear usuarios
            print("Creando usuarios...")
            user_mgr.save(user1)
            user_mgr.save(user2)
            print(f"✓ Usuarios creados: {len(user_mgr.load_all())}")

            # Probar eliminación de usuario (debería funcionar)
            print("Eliminando usuario...")
            result = user_mgr.delete(user2.id)
            print(f"✓ Usuario eliminado: {result}")

            # Verificar que no se puede eliminar autor con libros
            print("Intentando eliminar autor con libros asociados...")
            result = author_mgr.delete(author1.id)  # Debería fallar
            print(f"Resultado eliminación autor con libros: {result}")

            # Eliminar libros primero
            print("Eliminando libros...")
            book_mgr.delete(book1.id)
            book_mgr.delete(book2.id)
            print(f"✓ Libros restantes: {len(book_mgr.load_all())}")

            # Ahora sí debería poder eliminar el autor
            print("Eliminando autor sin libros asociados...")
            result = author_mgr.delete(author1.id)
            print(f"✓ Autor eliminado: {result}")

            # Eliminar el otro autor
            result = author_mgr.delete(author2.id)
            print(f"✓ Segundo autor eliminado: {result}")

            # Eliminar usuario restante
            result = user_mgr.delete(user1.id)
            print(f"✓ Usuario restante eliminado: {result}")

            print(f"✓ Formato {fmt} completado exitosamente\n")

        except Exception as e:
            print(f"✗ Error en formato {fmt}: {e}\n")

    print("=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_crud_operations()