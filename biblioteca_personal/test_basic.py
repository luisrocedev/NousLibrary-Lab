#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento básico del sistema
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from models import Book, Author, User
from data_managers import DataManagerFactory

def test_book_operations():
    """Prueba las operaciones básicas de libros"""
    print("=== PRUEBA DE OPERACIONES CON LIBROS ===")

    # Crear gestor de libros
    book_manager = DataManagerFactory.create_book_manager('txt', 'test_data')

    # Crear un autor de prueba
    author_manager = DataManagerFactory.create_author_manager('txt', 'test_data')
    author = Author(name="Gabriel García Márquez", nationality="Colombiano")
    author_manager.save(author)

    # Crear un libro de prueba
    book = Book(
        title="Cien años de soledad",
        author_id=author.id,
        isbn="978-84-376-0494-7",
        publication_year=1967,
        genre="Novela",
        description="Una de las obras más importantes del realismo mágico",
        pages=471,
        publisher="Editorial Sudamericana"
    )

    print(f"Creando libro: {book.title}")

    # Guardar libro
    if book_manager.save(book):
        print("✓ Libro guardado correctamente")
    else:
        print("✗ Error al guardar libro")
        return False

    # Cargar libro
    loaded_book = book_manager.load(book.id)
    if loaded_book and loaded_book.title == book.title:
        print("✓ Libro cargado correctamente")
    else:
        print("✗ Error al cargar libro")
        return False

    # Buscar libro por título
    found_books = book_manager.search({'title': 'Cien años'})
    if found_books and len(found_books) > 0:
        print("✓ Búsqueda por título funciona correctamente")
    else:
        print("✗ Error en búsqueda por título")
        return False

    # Listar todos los libros
    all_books = book_manager.load_all()
    if len(all_books) > 0:
        print(f"✓ Se encontraron {len(all_books)} libro(s)")
    else:
        print("✗ Error al listar libros")
        return False

    # Actualizar libro
    book.description = "Obra maestra del realismo mágico latinoamericano"
    if book_manager.save(book):
        print("✓ Libro actualizado correctamente")
    else:
        print("✗ Error al actualizar libro")
        return False

    # Verificar actualización
    updated_book = book_manager.load(book.id)
    if updated_book and updated_book.description == book.description:
        print("✓ Actualización verificada correctamente")
    else:
        print("✗ Error en verificación de actualización")
        return False

    # Eliminar libro
    if book_manager.delete(book.id):
        print("✓ Libro eliminado correctamente")
    else:
        print("✗ Error al eliminar libro")
        return False

    # Verificar eliminación
    deleted_book = book_manager.load(book.id)
    if deleted_book is None:
        print("✓ Eliminación verificada correctamente")
    else:
        print("✗ Error en verificación de eliminación")
        return False

    # Limpiar autor de prueba
    author_manager.delete(author.id)

    print("✓ Todas las pruebas de libros pasaron correctamente\n")
    return True

def test_author_operations():
    """Prueba las operaciones básicas de autores"""
    print("=== PRUEBA DE OPERACIONES CON AUTORES ===")

    # Crear gestor de autores
    author_manager = DataManagerFactory.create_author_manager('txt', 'test_data')

    # Crear autor de prueba
    author = Author(
        name="Mario Vargas Llosa",
        birth_date=None,  # Podemos agregar fecha después
        nationality="Peruano",
        biography="Premio Nobel de Literatura 2010"
    )

    print(f"Creando autor: {author.name}")

    # Guardar autor
    if author_manager.save(author):
        print("✓ Autor guardado correctamente")
    else:
        print("✗ Error al guardar autor")
        return False

    # Cargar autor
    loaded_author = author_manager.load(author.id)
    if loaded_author and loaded_author.name == author.name:
        print("✓ Autor cargado correctamente")
    else:
        print("✗ Error al cargar autor")
        return False

    # Buscar autor por nombre
    found_authors = author_manager.search({'name': 'Mario'})
    if found_authors and len(found_authors) > 0:
        print("✓ Búsqueda por nombre funciona correctamente")
    else:
        print("✗ Error en búsqueda por nombre")
        return False

    # Actualizar autor
    author.biography = "Premio Nobel de Literatura 2010. Uno de los más importantes escritores contemporáneos."
    if author_manager.save(author):
        print("✓ Autor actualizado correctamente")
    else:
        print("✗ Error al actualizar autor")
        return False

    # Eliminar autor
    if author_manager.delete(author.id):
        print("✓ Autor eliminado correctamente")
    else:
        print("✗ Error al eliminar autor")
        return False

    print("✓ Todas las pruebas de autores pasaron correctamente\n")
    return True

def test_user_operations():
    """Prueba las operaciones básicas de usuarios"""
    print("=== PRUEBA DE OPERACIONES CON USUARIOS ===")

    # Crear gestor de usuarios
    user_manager = DataManagerFactory.create_user_manager('txt', 'test_data')

    # Crear usuario de prueba
    user = User(
        name="Ana García",
        email="ana.garcia@email.com",
        phone="666-123-456",
        address="Calle Mayor 123, Madrid"
    )

    print(f"Creando usuario: {user.name}")

    # Guardar usuario
    if user_manager.save(user):
        print("✓ Usuario guardado correctamente")
    else:
        print("✗ Error al guardar usuario")
        return False

    # Cargar usuario
    loaded_user = user_manager.load(user.id)
    if loaded_user and loaded_user.email == user.email:
        print("✓ Usuario cargado correctamente")
    else:
        print("✗ Error al cargar usuario")
        return False

    # Buscar usuario por email
    found_users = user_manager.search({'email': 'ana.garcia'})
    if found_users and len(found_users) > 0:
        print("✓ Búsqueda por email funciona correctamente")
    else:
        print("✗ Error en búsqueda por email")
        return False

    # Actualizar usuario
    user.phone = "666-987-654"
    if user_manager.save(user):
        print("✓ Usuario actualizado correctamente")
    else:
        print("✗ Error al actualizar usuario")
        return False

    # Eliminar usuario
    if user_manager.delete(user.id):
        print("✓ Usuario eliminado correctamente")
    else:
        print("✗ Error al eliminar usuario")
        return False

    print("✓ Todas las pruebas de usuarios pasaron correctamente\n")
    return True

def main():
    """Función principal de pruebas"""
    print("INICIANDO PRUEBAS DEL SISTEMA DE BIBLIOTECA PERSONAL")
    print("=" * 60)

    # Crear directorio de pruebas
    test_dir = Path('test_data')
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    try:
        # Ejecutar pruebas
        success = True
        success &= test_book_operations()
        success &= test_author_operations()
        success &= test_user_operations()

        if success:
            print("🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
            print("El sistema de biblioteca personal funciona correctamente.")
        else:
            print("❌ ALGUNAS PRUEBAS FALLARON")
            print("Revisa los errores anteriores.")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO DURANTE LAS PRUEBAS: {e}")
        success = False

    finally:
        # Limpiar directorio de pruebas
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)