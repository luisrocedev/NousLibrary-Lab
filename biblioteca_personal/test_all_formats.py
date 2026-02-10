#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento de TODOS los formatos
"""

import sys, shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models import Book, Author, User
from data_managers import DataManagerFactory

FORMATOS = ['txt', 'csv', 'json', 'xml', 'db']

def test_format(fmt: str) -> bool:
    """Prueba CRUD completo para un formato dado"""
    print(f"\n{'='*50}")
    print(f"  PRUEBAS FORMATO: {fmt.upper()}")
    print(f"{'='*50}")

    test_dir = f'test_data_{fmt}'
    test_path = Path(test_dir)
    if test_path.exists():
        shutil.rmtree(test_path)

    ok = True
    try:
        # Gestores
        bm = DataManagerFactory.create_book_manager(fmt, test_dir)
        am = DataManagerFactory.create_author_manager(fmt, test_dir)
        um = DataManagerFactory.create_user_manager(fmt, test_dir)

        # ---- AUTORES ----
        author = Author(name="Gabriel García Márquez", nationality="Colombiano")
        assert am.save(author), "Guardar autor"
        print("  ✓ Autor guardado")

        loaded = am.load(author.id)
        assert loaded and loaded.name == author.name, "Cargar autor"
        print("  ✓ Autor cargado")

        found = am.search({'name': 'Gabriel'})
        assert len(found) > 0, "Buscar autor"
        print("  ✓ Autor buscado")

        author.biography = "Nobel de Literatura 1982"
        assert am.save(author), "Actualizar autor"
        print("  ✓ Autor actualizado")

        # ---- LIBROS ----
        book = Book(
            title="Cien años de soledad",
            author_id=author.id,
            isbn="978-84-376-0494-7",
            publication_year=1967,
            genre="Novela",
            description="Realismo mágico",
            pages=471,
            publisher="Sudamericana"
        )
        assert bm.save(book), "Guardar libro"
        print("  ✓ Libro guardado")

        loaded = bm.load(book.id)
        assert loaded and loaded.title == book.title, "Cargar libro"
        print("  ✓ Libro cargado")

        found = bm.search({'title': 'Cien'})
        assert len(found) > 0, "Buscar libro"
        print("  ✓ Libro buscado")

        all_books = bm.load_all()
        assert len(all_books) == 1, "Listar libros"
        print("  ✓ Libros listados")

        book.description = "Obra maestra del realismo mágico"
        assert bm.save(book), "Actualizar libro"
        updated = bm.load(book.id)
        assert updated.description == book.description, "Verificar actualización"
        print("  ✓ Libro actualizado y verificado")

        assert bm.delete(book.id), "Eliminar libro"
        assert bm.load(book.id) is None, "Verificar eliminación"
        print("  ✓ Libro eliminado")

        # ---- USUARIOS ----
        user = User(name="Ana García", email="ana@test.com", phone="666123456")
        assert um.save(user), "Guardar usuario"
        print("  ✓ Usuario guardado")

        loaded = um.load(user.id)
        assert loaded and loaded.email == user.email, "Cargar usuario"
        print("  ✓ Usuario cargado")

        found = um.search({'email': 'ana'})
        assert len(found) > 0, "Buscar usuario"
        print("  ✓ Usuario buscado")

        assert um.delete(user.id), "Eliminar usuario"
        print("  ✓ Usuario eliminado")

        # Limpiar autor
        am.delete(author.id)

        print(f"\n  🎉 FORMATO {fmt.upper()}: TODAS LAS PRUEBAS CORRECTAS")

    except AssertionError as e:
        print(f"  ✗ FALLO: {e}")
        ok = False
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        ok = False
    finally:
        if test_path.exists():
            shutil.rmtree(test_path)

    return ok


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║  PRUEBAS COMPLETAS - TODOS LOS FORMATOS         ║")
    print("║  TXT · CSV · JSON · XML · SQLite                ║")
    print("╚══════════════════════════════════════════════════╝")

    results = {}
    for fmt in FORMATOS:
        results[fmt] = test_format(fmt)

    print("\n" + "="*50)
    print("  RESUMEN DE RESULTADOS")
    print("="*50)
    all_ok = True
    for fmt, ok in results.items():
        status = "✓ CORRECTO" if ok else "✗ FALLIDO"
        print(f"  {fmt.upper():>5}: {status}")
        if not ok:
            all_ok = False

    print("="*50)
    if all_ok:
        print("  🎉 TODOS LOS FORMATOS FUNCIONAN CORRECTAMENTE")
    else:
        print("  ❌ ALGUNOS FORMATOS FALLARON")
    print("="*50)

    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
