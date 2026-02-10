"""
Menú principal del Sistema de Gestión de Biblioteca Personal

Este módulo implementa la interfaz de usuario principal que permite
al usuario interactuar con el sistema de biblioteca.
"""

import os
from typing import Dict, Any
from pathlib import Path

from data_managers import DataManagerFactory
from models import Book, Author, User
from utils.logger import Logger

class MenuPrincipal:
    """
    Clase que maneja el menú principal de la aplicación
    """

    def __init__(self):
        """
        Inicializa el menú principal
        """
        self.logger = Logger()
        self.format_type = self._seleccionar_formato()
        self.data_path = "data"

        # Crear gestores de datos
        self.book_manager = DataManagerFactory.create_book_manager(self.format_type, self.data_path)
        self.author_manager = DataManagerFactory.create_author_manager(self.format_type, self.data_path)
        self.user_manager = DataManagerFactory.create_user_manager(self.format_type, self.data_path)

        self.logger.info(f"Sistema inicializado con formato: {self.format_type}")

    def _seleccionar_formato(self) -> str:
        """
        Permite al usuario seleccionar el formato de almacenamiento

        Returns:
            str: Formato seleccionado ('txt' por ahora)
        """
        while True:
            self._limpiar_pantalla()
            print("=== SISTEMA DE GESTIÓN DE BIBLIOTECA PERSONAL ===")
            print("=" * 50)
            print("\nSeleccione el formato de almacenamiento de datos:")
            print("1. Archivos de texto (.txt) - IMPLEMENTADO")
            print("2. Archivos CSV (.csv) - PRÓXIMAMENTE")
            print("3. Archivos JSON (.json) - PRÓXIMAMENTE")
            print("4. Archivos XML (.xml) - PRÓXIMAMENTE")
            print("5. Base de datos SQLite (.db) - PRÓXIMAMENTE")
            print("\n0. Salir")

            opcion = input("\nSeleccione una opción (1 para continuar, 0 para salir): ").strip()

            if opcion == '0':
                print("¡Hasta luego!")
                exit(0)
            elif opcion == '1':
                return 'txt'
            else:
                print("Por ahora solo está implementado el formato TXT. Presione Enter para continuar...")
                input()

    def ejecutar(self):
        """
        Ejecuta el bucle principal del menú
        """
        while True:
            self._mostrar_menu_principal()
            opcion = input("\nSeleccione una opción (0-6): ").strip()

            if opcion == '0':
                self._salir()
                break
            elif opcion == '1':
                self._menu_libros()
            elif opcion == '2':
                self._menu_autores()
            elif opcion == '3':
                self._menu_usuarios()
            elif opcion == '4':
                self._menu_prestamos()
            elif opcion == '5':
                self._menu_reportes()
            elif opcion == '6':
                self._cambiar_formato()
            else:
                print("Opción inválida. Presione Enter para continuar...")
                input()

    def _mostrar_menu_principal(self):
        """
        Muestra el menú principal
        """
        self._limpiar_pantalla()
        print("=== SISTEMA DE GESTIÓN DE BIBLIOTECA PERSONAL ===")
        print("=" * 50)
        print(f"Formato actual: {self.format_type.upper()}")
        print("\nMENÚ PRINCIPAL:")
        print("1. Gestión de Libros")
        print("2. Gestión de Autores")
        print("3. Gestión de Usuarios")
        print("4. Gestión de Préstamos")
        print("5. Reportes y Estadísticas")
        print("6. Cambiar formato de almacenamiento")
        print("\n0. Salir")

    def _menu_libros(self):
        """
        Maneja el menú de gestión de libros
        """
        while True:
            self._limpiar_pantalla()
            print("=== GESTIÓN DE LIBROS ===")
            print("=" * 30)
            print("1. Agregar libro")
            print("2. Buscar libro")
            print("3. Listar todos los libros")
            print("4. Actualizar libro")
            print("5. Eliminar libro")
            print("\n0. Volver al menú principal")

            opcion = input("\nSeleccione una opción (0-5): ").strip()

            if opcion == '0':
                break
            elif opcion == '1':
                self._agregar_libro()
            elif opcion == '2':
                self._buscar_libro()
            elif opcion == '3':
                self._listar_libros()
            elif opcion == '4':
                self._actualizar_libro()
            elif opcion == '5':
                self._eliminar_libro()
            else:
                print("Opción inválida. Presione Enter para continuar...")
                input()

    def _menu_autores(self):
        """
        Maneja el menú de gestión de autores
        """
        while True:
            self._limpiar_pantalla()
            print("=== GESTIÓN DE AUTORES ===")
            print("=" * 32)
            print("1. Agregar autor")
            print("2. Buscar autor")
            print("3. Listar todos los autores")
            print("4. Actualizar autor")
            print("5. Eliminar autor")
            print("\n0. Volver al menú principal")

            opcion = input("\nSeleccione una opción (0-5): ").strip()

            if opcion == '0':
                break
            elif opcion == '1':
                self._agregar_autor()
            elif opcion == '2':
                self._buscar_autor()
            elif opcion == '3':
                self._listar_autores()
            elif opcion == '4':
                self._actualizar_autor()
            elif opcion == '5':
                self._eliminar_autor()
            else:
                print("Opción inválida. Presione Enter para continuar...")
                input()

    def _menu_usuarios(self):
        """
        Maneja el menú de gestión de usuarios
        """
        while True:
            self._limpiar_pantalla()
            print("=== GESTIÓN DE USUARIOS ===")
            print("=" * 33)
            print("1. Agregar usuario")
            print("2. Buscar usuario")
            print("3. Listar todos los usuarios")
            print("4. Actualizar usuario")
            print("5. Eliminar usuario")
            print("\n0. Volver al menú principal")

            opcion = input("\nSeleccione una opción (0-5): ").strip()

            if opcion == '0':
                break
            elif opcion == '1':
                self._agregar_usuario()
            elif opcion == '2':
                self._buscar_usuario()
            elif opcion == '3':
                self._listar_usuarios()
            elif opcion == '4':
                self._actualizar_usuario()
            elif opcion == '5':
                self._eliminar_usuario()
            else:
                print("Opción inválida. Presione Enter para continuar...")
                input()

    def _menu_prestamos(self):
        """
        Maneja el menú de gestión de préstamos
        """
        while True:
            self._limpiar_pantalla()
            print("=== GESTIÓN DE PRÉSTAMOS ===")
            print("=" * 34)
            print("1. Prestar libro")
            print("2. Devolver libro")
            print("3. Ver préstamos activos")
            print("4. Ver libros prestados por usuario")
            print("\n0. Volver al menú principal")

            opcion = input("\nSeleccione una opción (0-4): ").strip()

            if opcion == '0':
                break
            elif opcion == '1':
                self._prestar_libro()
            elif opcion == '2':
                self._devolver_libro()
            elif opcion == '3':
                self._ver_prestamos_activos()
            elif opcion == '4':
                self._ver_libros_usuario()
            else:
                print("Opción inválida. Presione Enter para continuar...")
                input()

    def _menu_reportes(self):
        """
        Maneja el menú de reportes y estadísticas
        """
        while True:
            self._limpiar_pantalla()
            print("=== REPORTES Y ESTADÍSTICAS ===")
            print("=" * 38)
            print("1. Estadísticas generales")
            print("2. Libros por género")
            print("3. Libros por autor")
            print("4. Usuarios más activos")
            print("5. Exportar datos")
            print("\n0. Volver al menú principal")

            opcion = input("\nSeleccione una opción (0-5): ").strip()

            if opcion == '0':
                break
            elif opcion == '1':
                self._estadisticas_generales()
            elif opcion == '2':
                self._libros_por_genero()
            elif opcion == '3':
                self._libros_por_autor()
            elif opcion == '4':
                self._usuarios_mas_activos()
            elif opcion == '5':
                self._exportar_datos()
            else:
                print("Opción inválida. Presione Enter para continuar...")
                input()

    def _cambiar_formato(self):
        """
        Permite cambiar el formato de almacenamiento
        """
        print("\nCambiar formato de almacenamiento...")
        print("Por ahora solo está disponible el formato TXT.")
        print("En futuras versiones se implementarán otros formatos.")
        input("\nPresione Enter para continuar...")

    def _salir(self):
        """
        Maneja la salida del programa
        """
        print("\n¿Está seguro que desea salir? (s/n): ", end="")
        if input().lower() == 's':
            self.logger.info("Aplicación finalizada por el usuario")
            print("¡Hasta luego!")
            exit(0)

    # Métodos de gestión de libros
    def _agregar_libro(self):
        """Agrega un nuevo libro"""
        print("\n=== AGREGAR LIBRO ===")
        try:
            title = input("Título: ").strip()
            if not title:
                raise ValueError("El título es obligatorio")

            author_id = input("ID del autor: ").strip()
            if not author_id:
                raise ValueError("El ID del autor es obligatorio")

            # Verificar que el autor existe
            if not self.author_manager.exists(author_id):
                print("Error: El autor no existe. Primero debe crear el autor.")
                input("\nPresione Enter para continuar...")
                return

            isbn = input("ISBN (opcional): ").strip()
            publication_year = input("Año de publicación (opcional): ").strip()
            publication_year = int(publication_year) if publication_year else None

            genre = input("Género: ").strip()
            description = input("Descripción: ").strip()
            pages = input("Número de páginas (opcional): ").strip()
            pages = int(pages) if pages else None

            language = input("Idioma (por defecto: Español): ").strip() or "Español"
            publisher = input("Editorial: ").strip()

            libro = Book(
                title=title,
                author_id=author_id,
                isbn=isbn,
                publication_year=publication_year,
                genre=genre,
                description=description,
                pages=pages,
                language=language,
                publisher=publisher
            )

            if self.book_manager.save(libro):
                print("Libro agregado exitosamente.")
                self.logger.log_operation("CREATE", "Book", libro.id, True)
            else:
                print("Error al agregar el libro.")
                self.logger.log_operation("CREATE", "Book", libro.id, False)

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
            self.logger.error(f"Error al agregar libro: {e}")

        input("\nPresione Enter para continuar...")

    def _buscar_libro(self):
        """Busca un libro por ID o título"""
        print("\n=== BUSCAR LIBRO ===")
        criterio = input("Ingrese ID o título del libro: ").strip()

        if not criterio:
            print("Debe ingresar un criterio de búsqueda.")
            input("\nPresione Enter para continuar...")
            return

        # Buscar por ID primero
        libro = self.book_manager.load(criterio)
        if libro:
            self._mostrar_libro(libro)
        else:
            # Buscar por título
            libros = self.book_manager.search({'title': criterio})
            if libros:
                print(f"Se encontraron {len(libros)} libro(s):")
                for libro in libros:
                    self._mostrar_libro(libro)
                    print("-" * 50)
            else:
                print("No se encontraron libros con ese criterio.")

        input("\nPresione Enter para continuar...")

    def _listar_libros(self):
        """Lista todos los libros"""
        print("\n=== LISTADO DE LIBROS ===")
        libros = self.book_manager.load_all()

        if not libros:
            print("No hay libros registrados.")
        else:
            print(f"Total de libros: {len(libros)}")
            print("-" * 80)
            for libro in libros:
                print(f"ID: {libro.id}")
                print(f"Título: {libro.title}")
                print(f"Autor ID: {libro.author_id}")
                print(f"Género: {libro.genre}")
                print(f"Disponible: {'Sí' if libro.available else 'No'}")
                print("-" * 80)

        input("\nPresione Enter para continuar...")

    def _actualizar_libro(self):
        """Actualiza un libro existente"""
        print("\n=== ACTUALIZAR LIBRO ===")
        libro_id = input("Ingrese el ID del libro a actualizar: ").strip()

        if not libro_id:
            print("Debe ingresar un ID de libro.")
            input("\nPresione Enter para continuar...")
            return

        libro = self.book_manager.load(libro_id)
        if not libro:
            print("Libro no encontrado.")
            input("\nPresione Enter para continuar...")
            return

        print("Deje en blanco los campos que no desea cambiar:")
        try:
            title = input(f"Título ({libro.title}): ").strip() or libro.title
            genre = input(f"Género ({libro.genre}): ").strip() or libro.genre
            description = input(f"Descripción ({libro.description}): ").strip() or libro.description
            publisher = input(f"Editorial ({libro.publisher}): ").strip() or libro.publisher

            libro.title = title
            libro.genre = genre
            libro.description = description
            libro.publisher = publisher

            if self.book_manager.save(libro):
                print("Libro actualizado exitosamente.")
                self.logger.log_operation("UPDATE", "Book", libro.id, True)
            else:
                print("Error al actualizar el libro.")
                self.logger.log_operation("UPDATE", "Book", libro.id, False)

        except Exception as e:
            print(f"Error: {e}")
            self.logger.error(f"Error al actualizar libro {libro_id}: {e}")

        input("\nPresione Enter para continuar...")

    def _eliminar_libro(self):
        """Elimina un libro"""
        print("\n=== ELIMINAR LIBRO ===")
        libro_id = input("Ingrese el ID del libro a eliminar: ").strip()

        if not libro_id:
            print("Debe ingresar un ID de libro.")
            input("\nPresione Enter para continuar...")
            return

        libro = self.book_manager.load(libro_id)
        if not libro:
            print("Libro no encontrado.")
            input("\nPresione Enter para continuar...")
            return

        self._mostrar_libro(libro)
        confirmacion = input("\n¿Está seguro que desea eliminar este libro? (s/n): ").strip().lower()

        if confirmacion == 's':
            if self.book_manager.delete(libro_id):
                print("Libro eliminado exitosamente.")
                self.logger.log_operation("DELETE", "Book", libro_id, True)
            else:
                print("Error al eliminar el libro.")
                self.logger.log_operation("DELETE", "Book", libro_id, False)
        else:
            print("Operación cancelada.")

        input("\nPresione Enter para continuar...")

    # Métodos auxiliares
    def _mostrar_libro(self, libro: Book):
        """Muestra los detalles de un libro"""
        print(f"ID: {libro.id}")
        print(f"Título: {libro.title}")
        print(f"Autor ID: {libro.author_id}")
        print(f"ISBN: {libro.isbn}")
        print(f"Año: {libro.publication_year}")
        print(f"Género: {libro.genre}")
        print(f"Descripción: {libro.description}")
        print(f"Páginas: {libro.pages}")
        print(f"Idioma: {libro.language}")
        print(f"Editorial: {libro.publisher}")
        print(f"Disponible: {'Sí' if libro.available else 'No'}")
        if libro.borrowed_by:
            print(f"Prestado a: {libro.borrowed_by}")

    def _limpiar_pantalla(self):
        """Limpia la pantalla de la consola"""
        os.system('clear' if os.name == 'posix' else 'cls')

    # Métodos placeholder para funcionalidades no implementadas aún
    def _agregar_autor(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _buscar_autor(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _listar_autores(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _actualizar_autor(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _eliminar_autor(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _agregar_usuario(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _buscar_usuario(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _listar_usuarios(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _actualizar_usuario(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _eliminar_usuario(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _prestar_libro(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _devolver_libro(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _ver_prestamos_activos(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _ver_libros_usuario(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _estadisticas_generales(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _libros_por_genero(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _libros_por_autor(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _usuarios_mas_activos(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")

    def _exportar_datos(self):
        print("Funcionalidad no implementada aún.")
        input("\nPresione Enter para continuar...")