#!/usr/bin/env python3
"""
Script de prueba simple para verificar las funciones de eliminación
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_managers import DataManagerFactory
from models import Book, Author, User
from datetime import datetime

def test_delete_functions():
    """Prueba las funciones de eliminación directamente"""

    print("=== PRUEBA DE FUNCIONES DE ELIMINACIÓN ===\n")

    # Crear managers
    book_mgr = DataManagerFactory.create_book_manager('json')
    author_mgr = DataManagerFactory.create_author_manager('json')
    user_mgr = DataManagerFactory.create_user_manager('json')

    # Limpiar datos existentes
    print("Limpiando datos existentes...")
    for book in book_mgr.load_all():
        book_mgr.delete(book.id)
    for author in author_mgr.load_all():
        author_mgr.delete(author.id)
    for user in user_mgr.load_all():
        user_mgr.delete(user.id)

    # Crear datos de prueba
    print("Creando datos de prueba...")
    author = Author(id="test_author", name="Autor de Prueba", birth_date=datetime(1980, 1, 1), nationality="Test")
    book = Book(id="test_book", title="Libro de Prueba", author_id="test_author", publication_year=2023, genre="Test")
    user = User(id="test_user", name="Usuario de Prueba", email="test@example.com")

    author_mgr.save(author)
    book_mgr.save(book)
    user_mgr.save(user)

    print(f"✓ Creados: {len(author_mgr.load_all())} autores, {len(book_mgr.load_all())} libros, {len(user_mgr.load_all())} usuarios")

    # Probar eliminación de usuario (debería funcionar)
    print("\nProbando eliminación de usuario...")
    result = user_mgr.delete("test_user")
    print(f"Resultado eliminación usuario: {result}")
    print(f"Usuarios restantes: {len(user_mgr.load_all())}")

    # Probar eliminación de autor con libro (debería funcionar en el manager, pero no en GUI)
    print("\nProbando eliminación de autor con libro...")
    result = author_mgr.delete("test_author")
    print(f"Resultado eliminación autor: {result}")
    print(f"Autores restantes: {len(author_mgr.load_all())}")

    # Si el autor se eliminó, el libro queda huérfano
    print(f"Libros restantes: {len(book_mgr.load_all())}")

    # Limpiar
    for book in book_mgr.load_all():
        book_mgr.delete(book.id)

    print("\n=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_delete_functions()