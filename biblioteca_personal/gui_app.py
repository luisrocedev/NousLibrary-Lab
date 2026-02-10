#!/usr/bin/env python3
"""
Interfaz gráfica moderna para el Sistema de Gestión de Biblioteca Personal
Utiliza ttkbootstrap para un diseño profesional con temas modernos.

Autor: DAM2526
"""

import sys
from pathlib import Path

# Añadir raíz al path
sys.path.insert(0, str(Path(__file__).parent))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.constants import END
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

from models import Book, Author, User
from data_managers import DataManagerFactory
from data_access_framework import create_framework, Book as FrameworkBook, Author as FrameworkAuthor, User as FrameworkUser
from utils.logger import Logger

# ════════════════════════════════════════════════════════════════
#  CONSTANTES
# ════════════════════════════════════════════════════════════════
FORMATOS = {
    'TXT - Texto plano': 'txt',
    'CSV - Separado por comas': 'csv',
    'JSON - Notación de objetos': 'json',
    'XML - Marcado extensible': 'xml',
    'SQLite - Base de datos': 'db'
}

GENEROS = [
    "Novela", "Ciencia ficción", "Fantasía", "Terror", "Poesía",
    "Ensayo", "Historia", "Biografía", "Infantil", "Juvenil",
    "Romance", "Misterio", "Thriller", "Autoayuda", "Ciencia",
    "Filosofía", "Arte", "Otro"
]

IDIOMAS = ["Español", "Inglés", "Francés", "Alemán", "Italiano", "Portugués", "Otro"]

DATA_PATH = "data"


# ════════════════════════════════════════════════════════════════
#  APLICACIÓN PRINCIPAL
# ════════════════════════════════════════════════════════════════
class BibliotecaApp:
    """Aplicación principal con interfaz ttkbootstrap"""

    def __init__(self):
        self.logger = Logger()
        self.format_type = 'sqlite'  # formato por defecto del framework

        # Inicializar framework
        self.framework = create_framework(database_format=self.format_type)
        self.book_repo = self.framework.entity_manager.get_repository(FrameworkBook)
        self.author_repo = self.framework.entity_manager.get_repository(FrameworkAuthor)
        self.user_repo = self.framework.entity_manager.get_repository(FrameworkUser)

        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("📚 Biblioteca Personal - Framework Integrado")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 600)

        # Variables de estado
        self.selected_book_id = None
        self.selected_author_id = None
        self.selected_user_id = None

        # Construir interfaz
        self._build_ui()

        # Cargar datos iniciales
        self._refresh_all()

        self.logger.info("Interfaz gráfica iniciada")

    # ─────────────── Gestores de datos ───────────────
    def _init_managers(self):
        self.book_mgr = DataManagerFactory.create_book_manager(self.format_type, DATA_PATH)
        self.author_mgr = DataManagerFactory.create_author_manager(self.format_type, DATA_PATH)
        self.user_mgr = DataManagerFactory.create_user_manager(self.format_type, DATA_PATH)

    def _change_format(self, *_):
        label = self.format_var.get()
        new_fmt = FORMATOS.get(label, 'sqlite')
        if new_fmt != self.format_type:
            old_fmt = self.format_type
            self.format_type = new_fmt

            # Migrar datos al nuevo formato
            try:
                self.framework.entity_manager.migrate_entity(FrameworkBook, old_fmt, new_fmt)
                self.framework.entity_manager.migrate_entity(FrameworkAuthor, old_fmt, new_fmt)
                self.framework.entity_manager.migrate_entity(FrameworkUser, old_fmt, new_fmt)

                # Recrear framework con nuevo formato
                self.framework = create_framework(database_format=self.format_type)
                self.book_repo = self.framework.entity_manager.get_repository(FrameworkBook)
                self.author_repo = self.framework.entity_manager.get_repository(FrameworkAuthor)
                self.user_repo = self.framework.entity_manager.get_repository(FrameworkUser)

                self._refresh_all()
                self.status_var.set(f"Formato cambiado a {new_fmt.upper()}")
                self.logger.info(f"Formato cambiado de {old_fmt} a {new_fmt}")
            except Exception as e:
                messagebox.showerror("Error al cambiar formato", f"No se pudo migrar los datos: {str(e)}")
                self.format_type = old_fmt  # Revertir cambio

    # ─────────────── Construcción de la UI ───────────────
    def _build_ui(self):
        # ──── Barra superior ────
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X)

        ttk.Label(top, text="📚 Biblioteca Personal",
                  font=("Helvetica", 18, "bold"),
                  padding=(15, 8)).pack(side=tk.LEFT)

        # Selector de formato
        fmt_frame = ttk.Frame(top)
        fmt_frame.pack(side=tk.RIGHT)

        ttk.Label(fmt_frame, text="Formato:", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=(0, 5))
        self.format_var = tk.StringVar(value='JSON - Notación de objetos')
        fmt_combo = ttk.Combobox(fmt_frame, textvariable=self.format_var,
                                  values=list(FORMATOS.keys()),
                                  state="readonly", width=28)
        fmt_combo.pack(side=tk.LEFT)
        fmt_combo.bind("<<ComboboxSelected>>", self._change_format)

        # ──── Notebook con pestañas ────
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 0))

        # Pestañas
        self.tab_books = ttk.Frame(self.notebook)
        self.tab_authors = ttk.Frame(self.notebook)
        self.tab_users = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_books, text="  📖 Libros  ")
        self.notebook.add(self.tab_authors, text="  ✍️ Autores  ")
        self.notebook.add(self.tab_users, text="  👤 Usuarios  ")
        self.notebook.add(self.tab_stats, text="  📊 Estadísticas  ")

        self._build_books_tab()
        self._build_authors_tab()
        self._build_users_tab()
        self._build_stats_tab()

        # ──── Barra de estado ────
        status_bar = ttk.Frame(self.root, padding=(10, 5))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Listo")
        ttk.Label(status_bar, textvariable=self.status_var,
                  font=("Helvetica", 10)).pack(side=tk.LEFT)

        self.count_var = tk.StringVar(value="")
        ttk.Label(status_bar, textvariable=self.count_var,
                  font=("Helvetica", 10)).pack(side=tk.RIGHT)

    # ══════════════════════════════════════════
    #  PESTAÑA LIBROS
    # ══════════════════════════════════════════
    def _build_books_tab(self):
        # Panel izquierdo: Formulario
        left = ttk.LabelFrame(self.tab_books, text="Datos del libro")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        fields = [
            ("Título *", "book_title"),
            ("ISBN", "book_isbn"),
            ("Año publicación", "book_year"),
            ("Páginas", "book_pages"),
            ("Editorial", "book_publisher"),
            ("Descripción", "book_desc"),
        ]

        self.book_vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(left, text=label, font=("Helvetica", 10)).grid(
                row=i, column=0, sticky=tk.W, pady=2)
            var = tk.StringVar()
            self.book_vars[key] = var
            if key == "book_desc":
                entry = ttk.Entry(left, textvariable=var, width=30)
            else:
                entry = ttk.Entry(left, textvariable=var, width=30)
            entry.grid(row=i, column=1, pady=2, padx=(5, 0))

        row_idx = len(fields)

        # Autor (combo)
        ttk.Label(left, text="Autor *", font=("Helvetica", 10)).grid(
            row=row_idx, column=0, sticky=tk.W, pady=2)
        self.book_author_var = tk.StringVar()
        self.book_author_combo = ttk.Combobox(left, textvariable=self.book_author_var,
                                               width=28, state="readonly")
        self.book_author_combo.grid(row=row_idx, column=1, pady=2, padx=(5, 0))
        row_idx += 1

        # Género (combo)
        ttk.Label(left, text="Género", font=("Helvetica", 10)).grid(
            row=row_idx, column=0, sticky=tk.W, pady=2)
        self.book_genre_var = tk.StringVar()
        ttk.Combobox(left, textvariable=self.book_genre_var,
                     values=GENEROS, width=28, state="readonly").grid(
            row=row_idx, column=1, pady=2, padx=(5, 0))
        row_idx += 1

        # Idioma (combo)
        ttk.Label(left, text="Idioma", font=("Helvetica", 10)).grid(
            row=row_idx, column=0, sticky=tk.W, pady=2)
        self.book_lang_var = tk.StringVar(value="Español")
        ttk.Combobox(left, textvariable=self.book_lang_var,
                     values=IDIOMAS, width=28, state="readonly").grid(
            row=row_idx, column=1, pady=2, padx=(5, 0))
        row_idx += 1

        # Botones de acción
        btn_frame = ttk.Frame(left)
        btn_frame.grid(row=row_idx, column=0, columnspan=2, pady=(15, 5))

        self.book_add_btn = ttk.Button(btn_frame, text="➕ Agregar",
                                       command=self._add_book, width=12)
        self.book_add_btn.pack(side=tk.LEFT, padx=2)

        self.book_update_btn = ttk.Button(btn_frame, text="💾 Actualizar",
                                          command=self._update_book, width=12, state="disabled")
        self.book_update_btn.pack(side=tk.LEFT, padx=2)

        self.book_delete_btn = ttk.Button(btn_frame, text="🗑️ Eliminar",
                                          command=self._delete_book, width=12, state="disabled")
        self.book_delete_btn.pack(side=tk.LEFT, padx=2)

        row_idx += 1
        ttk.Button(left, text="🧹 Limpiar formulario",
                   command=self._clear_book_form).grid(row=row_idx, column=0, columnspan=2, pady=5)

        # Panel derecho: Tabla + búsqueda
        right = ttk.Frame(self.tab_books)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barra de búsqueda
        search_frame = ttk.Frame(right)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_frame, text="🔍", font=("Helvetica", 14)).pack(side=tk.LEFT)
        self.book_search_var = tk.StringVar()
        self.book_search_var.trace_add("write", lambda *_: self._refresh_books())
        ttk.Entry(search_frame, textvariable=self.book_search_var,
                  width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Actualizar",
                   command=self._refresh_books).pack(side=tk.RIGHT)

        # Treeview
        cols = ("title", "author", "genre", "year", "pages", "available")
        self.book_tree = ttk.Treeview(right, columns=cols, show="headings", height=18)

        self.book_tree.heading("title", text="Título")
        self.book_tree.heading("author", text="Autor")
        self.book_tree.heading("genre", text="Género")
        self.book_tree.heading("year", text="Año")
        self.book_tree.heading("pages", text="Páginas")
        self.book_tree.heading("available", text="Estado")

        self.book_tree.column("title", width=220)
        self.book_tree.column("author", width=150)
        self.book_tree.column("genre", width=100)
        self.book_tree.column("year", width=60, anchor=tk.CENTER)
        self.book_tree.column("pages", width=60, anchor=tk.CENTER)
        self.book_tree.column("available", width=90, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scrollbar.set)

        self.book_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.book_tree.bind("<<TreeviewSelect>>", self._on_book_select)

    def _refresh_books(self):
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        search = self.book_search_var.get().lower()
        books = self.book_repo.load_all()
        authors = {a.id: a.name for a in self.author_repo.load_all()}

        count = 0
        for b in books:
            author_name = authors.get(b.author_id, "Desconocido")
            if search and search not in b.title.lower() and search not in author_name.lower() \
               and search not in b.genre.lower():
                continue

            estado = "Disponible" if b.available else "Prestado"
            self.book_tree.insert("", END, iid=b.id, values=(
                b.title, author_name, b.genre,
                b.publication_year or "", b.pages or "", estado
            ))
            count += 1

        self.count_var.set(f"Libros: {count}")
        self._update_author_combos()

    def _on_book_select(self, event):
        sel = self.book_tree.selection()
        if not sel:
            self.selected_book_id = None
            self.book_update_btn.config(state="disabled")
            self.book_delete_btn.config(state="disabled")
            return

        book_id = sel[0]
        self.selected_book_id = book_id
        self.book_update_btn.config(state="normal")
        self.book_delete_btn.config(state="normal")

        book = self.book_mgr.load(book_id)
        if not book:
            return
        book = self.book_mgr.load(book_id)
        if not book:
            return

        self.book_vars['book_title'].set(book.title)
        self.book_vars['book_isbn'].set(book.isbn)
        self.book_vars['book_year'].set(str(book.publication_year) if book.publication_year else "")
        self.book_vars['book_pages'].set(str(book.pages) if book.pages else "")
        self.book_vars['book_publisher'].set(book.publisher)
        self.book_vars['book_desc'].set(book.description)
        self.book_genre_var.set(book.genre)
        self.book_lang_var.set(book.language)

        # Buscar nombre del autor
        author = self.author_mgr.load(book.author_id)
        if author:
            self.book_author_var.set(f"{author.name} ({author.id[:8]})")

    def _add_book(self):
        title = self.book_vars['book_title'].get().strip()
        if not title:
            messagebox.showwarning("El título es obligatorio", "Campo requerido")
            return

        author_sel = self.book_author_var.get()
        if not author_sel:
            messagebox.showwarning("Debe seleccionar un autor", "Campo requerido")
            return

        # Extraer ID del autor del combo
        author_id = self._extract_author_id(author_sel)
        if not author_id:
            messagebox.showwarning("Autor no válido", "Error")
            return

        year = self.book_vars['book_year'].get().strip()
        pages = self.book_vars['book_pages'].get().strip()

        try:
            book = Book(
                title=title,
                author_id=author_id,
                isbn=self.book_vars['book_isbn'].get().strip(),
                publication_year=int(year) if year else None,
                genre=self.book_genre_var.get(),
                description=self.book_vars['book_desc'].get().strip(),
                pages=int(pages) if pages else None,
                language=self.book_lang_var.get(),
                publisher=self.book_vars['book_publisher'].get().strip()
            )

            if self.book_repo.save(book):
                self._refresh_books()
                self._clear_book_form()
                self.status_var.set(f"Libro '{title}' agregado correctamente")
                self.logger.log_operation("CREATE", "Book", book.id, True)
            else:
                messagebox.showerror("Error al guardar el libro", "Error")
        except ValueError as e:
            messagebox.showerror(str(e), "Error de validación")

    def _update_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("Seleccione un libro de la tabla", "Debe seleccionar un libro para actualizar")
            return

        book = self.book_repo.load(self.selected_book_id)
        if not book:
            return

        title = self.book_vars['book_title'].get().strip()
        if not title:
            messagebox.showwarning("El título es obligatorio", "Campo requerido")
            return

        year = self.book_vars['book_year'].get().strip()
        pages = self.book_vars['book_pages'].get().strip()

        book.title = title
        book.isbn = self.book_vars['book_isbn'].get().strip()
        book.publication_year = int(year) if year else None
        book.pages = int(pages) if pages else None
        book.publisher = self.book_vars['book_publisher'].get().strip()
        book.description = self.book_vars['book_desc'].get().strip()
        book.genre = self.book_genre_var.get()
        book.language = self.book_lang_var.get()

        author_sel = self.book_author_var.get()
        aid = self._extract_author_id(author_sel)
        if aid:
            book.author_id = aid

        if self.book_repo.save(book):
            self._refresh_books()
            self.status_var.set(f"Libro '{title}' actualizado")
            self.logger.log_operation("UPDATE", "Book", book.id, True)
        else:
            messagebox.showerror("Error al actualizar", "Error")

    def _delete_book(self):
        print("DEBUG: _delete_book called!")
        print(f"DEBUG: selected_book_id = {self.selected_book_id}")
        if not self.selected_book_id:
            print("DEBUG: No book selected")
            messagebox.showwarning("Seleccione un libro", "Debe seleccionar un libro para eliminar")
            return

        print("DEBUG: Showing book confirmation dialog")
        if messagebox.askyesno("¿Eliminar el libro seleccionado?", "Confirmar"):
            print("DEBUG: User confirmed deletion")
            if self.book_repo.delete(self.selected_book_id):
                print("DEBUG: Book deleted successfully")
                self._refresh_books()
                self._clear_book_form()
                self._update_author_combos()
                self.status_var.set("Libro eliminado")
                self.logger.log_operation("DELETE", "Book", self.selected_book_id, True)
            else:
                print("DEBUG: Failed to delete book")
                messagebox.showerror("Error al eliminar", "No se pudo eliminar el libro")
                self.logger.log_operation("DELETE", "Book", self.selected_book_id, True)

    def _clear_book_form(self):
        for var in self.book_vars.values():
            var.set("")
        self.book_genre_var.set("")
        self.book_lang_var.set("Español")
        self.book_author_var.set("")
        self.selected_book_id = None
        self.book_update_btn.config(state="disabled")
        self.book_delete_btn.config(state="disabled")

    def _extract_author_id(self, text: str) -> str:
        """Extrae el ID del autor desde el texto del combo '  Nombre (id_corto)'"""
        if '(' in text and text.endswith(')'):
            short_id = text.split('(')[-1].rstrip(')')
            for a in self.author_mgr.load_all():
                if a.id.startswith(short_id):
                    return a.id
        return ""

    def _update_author_combos(self):
        authors = self.author_mgr.load_all()
        values = [f"{a.name} ({a.id[:8]})" for a in authors]
        self.book_author_combo.configure(values=values)

    # ══════════════════════════════════════════
    #  PESTAÑA AUTORES
    # ══════════════════════════════════════════
    def _build_authors_tab(self):
        left = ttk.LabelFrame(self.tab_authors, text="Datos del autor")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        fields = [
            ("Nombre *", "author_name"),
            ("Nacionalidad", "author_nationality"),
            ("Biografía", "author_bio"),
        ]

        self.author_vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(left, text=label, font=("Helvetica", 10)).grid(
                row=i, column=0, sticky=tk.W, pady=3)
            var = tk.StringVar()
            self.author_vars[key] = var
            entry = ttk.Entry(left, textvariable=var, width=30)
            entry.grid(row=i, column=1, pady=3, padx=(5, 0))

        row_idx = len(fields)

        btn_frame = ttk.Frame(left)
        btn_frame.grid(row=row_idx, column=0, columnspan=2, pady=(15, 5))

        self.author_add_btn = ttk.Button(btn_frame, text="➕ Agregar",
                                         command=self._add_author, width=12)
        self.author_add_btn.pack(side=tk.LEFT, padx=2)

        self.author_update_btn = ttk.Button(btn_frame, text="💾 Actualizar",
                                            command=self._update_author, width=12, state="disabled")
        self.author_update_btn.pack(side=tk.LEFT, padx=2)

        self.author_delete_btn = ttk.Button(btn_frame, text="🗑️ Eliminar",
                                            command=self._delete_author, width=12, state="disabled")
        self.author_delete_btn.pack(side=tk.LEFT, padx=2)

        row_idx += 1
        ttk.Button(left, text="🧹 Limpiar formulario",
                   command=self._clear_author_form).grid(row=row_idx, column=0, columnspan=2, pady=5)

        # Panel derecho
        right = ttk.Frame(self.tab_authors)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(right)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(search_frame, text="🔍", font=("Helvetica", 14)).pack(side=tk.LEFT)
        self.author_search_var = tk.StringVar()
        self.author_search_var.trace_add("write", lambda *_: self._refresh_authors())
        ttk.Entry(search_frame, textvariable=self.author_search_var, width=40).pack(side=tk.LEFT, padx=5)

        cols = ("name", "nationality", "biography", "num_books")
        self.author_tree = ttk.Treeview(right, columns=cols, show="headings", height=18)

        self.author_tree.heading("name", text="Nombre")
        self.author_tree.heading("nationality", text="Nacionalidad")
        self.author_tree.heading("biography", text="Biografía")
        self.author_tree.heading("num_books", text="Libros")

        self.author_tree.column("name", width=200)
        self.author_tree.column("nationality", width=120)
        self.author_tree.column("biography", width=300)
        self.author_tree.column("num_books", width=60, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.author_tree.yview)
        self.author_tree.configure(yscrollcommand=scrollbar.set)
        self.author_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.author_tree.bind("<<TreeviewSelect>>", self._on_author_select)

    def _refresh_authors(self):
        for item in self.author_tree.get_children():
            self.author_tree.delete(item)

        search = self.author_search_var.get().lower()
        authors = self.author_repo.load_all()
        books = self.book_repo.load_all()

        # Contar libros por autor
        book_count = {}
        for b in books:
            book_count[b.author_id] = book_count.get(b.author_id, 0) + 1

        for a in authors:
            if search and search not in a.name.lower() and search not in a.nationality.lower():
                continue
            self.author_tree.insert("", END, iid=a.id, values=(
                a.name, a.nationality, a.biography[:80],
                book_count.get(a.id, 0)
            ))

    def _on_author_select(self, event):
        print("DEBUG: _on_author_select called")
        sel = self.author_tree.selection()
        print(f"DEBUG: author selection = {sel}")
        if not sel:
            self.selected_author_id = None
            self.author_update_btn.config(state="disabled")
            self.author_delete_btn.config(state="disabled")
            return

        self.selected_author_id = sel[0]
        print(f"DEBUG: selected_author_id set to {self.selected_author_id}")
        self.author_update_btn.config(state="normal")
        self.author_delete_btn.config(state="normal")
        print("DEBUG: Author buttons enabled")

        author = self.author_mgr.load(self.selected_author_id)
        if author:
            self.author_vars['author_name'].set(author.name)
            self.author_vars['author_nationality'].set(author.nationality)
            self.author_vars['author_bio'].set(author.biography)

    def _add_author(self):
        name = self.author_vars['author_name'].get().strip()
        if not name:
            messagebox.showwarning("El nombre es obligatorio", "Campo requerido")
            return

        author = Author(
            name=name,
            nationality=self.author_vars['author_nationality'].get().strip(),
            biography=self.author_vars['author_bio'].get().strip()
        )

        if self.author_repo.save(author):
            self._refresh_authors()
            self._clear_author_form()
            self._update_author_combos()
            self.status_var.set(f"Autor '{name}' agregado")
        else:
            messagebox.showerror("Error al guardar el autor", "Error")

    def _update_author(self):
        if not self.selected_author_id:
            messagebox.showwarning("Seleccione un autor", "Debe seleccionar un autor para actualizar")
            return

        author = self.author_repo.load(self.selected_author_id)
        if not author:
            return

        name = self.author_vars['author_name'].get().strip()
        if not name:
            messagebox.showwarning("El nombre es obligatorio", "Campo requerido")
            return

        author.name = name
        author.nationality = self.author_vars['author_nationality'].get().strip()
        author.biography = self.author_vars['author_bio'].get().strip()

        if self.author_repo.save(author):
            self._refresh_authors()
            self._update_author_combos()
            self.status_var.set(f"Autor '{name}' actualizado")

    def _delete_author(self):
        print("DEBUG: _delete_author called!")
        print(f"DEBUG: selected_author_id = {self.selected_author_id}")
        if not self.selected_author_id:
            print("DEBUG: No author selected")
            messagebox.showwarning("Seleccione un autor", "Debe seleccionar un autor para eliminar")
            return

        # Verificar si el autor tiene libros asociados
        author_books = [b for b in self.book_repo.load_all() if b.author_id == self.selected_author_id]
        print(f"DEBUG: Found {len(author_books)} books for author")
        if author_books:
            messagebox.showerror("No se puede eliminar",
                               f"El autor tiene {len(author_books)} libro(s) asociado(s). "
                               "Elimine primero los libros del autor.")
            return

        print("DEBUG: Showing confirmation dialog")
        if messagebox.askyesno("¿Eliminar el autor seleccionado?", "Confirmar"):
            print("DEBUG: User confirmed deletion")
            if self.author_repo.delete(self.selected_author_id):
                print("DEBUG: Author deleted successfully")
                self._refresh_authors()
                self._clear_author_form()
                self._update_author_combos()
                self.status_var.set("Autor eliminado")
                self.logger.log_operation("DELETE", "Author", self.selected_author_id, True)
            else:
                print("DEBUG: Failed to delete author")
                messagebox.showerror("Error al eliminar", "No se pudo eliminar el autor")

    def _clear_author_form(self):
        for var in self.author_vars.values():
            var.set("")
        self.selected_author_id = None
        self.author_update_btn.config(state="disabled")
        self.author_delete_btn.config(state="disabled")

    # ══════════════════════════════════════════
    #  PESTAÑA USUARIOS
    # ══════════════════════════════════════════
    def _build_users_tab(self):
        left = ttk.LabelFrame(self.tab_users, text="Datos del usuario")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        fields = [
            ("Nombre *", "user_name"),
            ("Email *", "user_email"),
            ("Teléfono", "user_phone"),
            ("Dirección", "user_address"),
        ]

        self.user_vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(left, text=label, font=("Helvetica", 10)).grid(
                row=i, column=0, sticky=tk.W, pady=3)
            var = tk.StringVar()
            self.user_vars[key] = var
            ttk.Entry(left, textvariable=var, width=30).grid(
                row=i, column=1, pady=3, padx=(5, 0))

        row_idx = len(fields)

        btn_frame = ttk.Frame(left)
        btn_frame.grid(row=row_idx, column=0, columnspan=2, pady=(15, 5))

        self.user_add_btn = ttk.Button(btn_frame, text="➕ Agregar",
                                       command=self._add_user, width=12)
        self.user_add_btn.pack(side=tk.LEFT, padx=2)

        self.user_update_btn = ttk.Button(btn_frame, text="💾 Actualizar",
                                          command=self._update_user, width=12, state="disabled")
        self.user_update_btn.pack(side=tk.LEFT, padx=2)

        self.user_delete_btn = ttk.Button(btn_frame, text="🗑️ Eliminar",
                                          command=self._delete_user, width=12, state="disabled")
        self.user_delete_btn.pack(side=tk.LEFT, padx=2)

        row_idx += 1
        ttk.Button(left, text="🧹 Limpiar formulario",
                   command=self._clear_user_form).grid(row=row_idx, column=0, columnspan=2, pady=5)

        # Panel derecho
        right = ttk.Frame(self.tab_users)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(right)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(search_frame, text="🔍", font=("Helvetica", 14)).pack(side=tk.LEFT)
        self.user_search_var = tk.StringVar()
        self.user_search_var.trace_add("write", lambda *_: self._refresh_users())
        ttk.Entry(search_frame, textvariable=self.user_search_var, width=40).pack(side=tk.LEFT, padx=5)

        cols = ("name", "email", "phone", "active", "borrowed")
        self.user_tree = ttk.Treeview(right, columns=cols, show="headings", height=18)

        self.user_tree.heading("name", text="Nombre")
        self.user_tree.heading("email", text="Email")
        self.user_tree.heading("phone", text="Teléfono")
        self.user_tree.heading("active", text="Activo")
        self.user_tree.heading("borrowed", text="Préstamos")

        self.user_tree.column("name", width=180)
        self.user_tree.column("email", width=200)
        self.user_tree.column("phone", width=120)
        self.user_tree.column("active", width=70, anchor=tk.CENTER)
        self.user_tree.column("borrowed", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.user_tree.bind("<<TreeviewSelect>>", self._on_user_select)

    def _refresh_users(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

        search = self.user_search_var.get().lower()
        users = self.user_repo.load_all()

        for u in users:
            if search and search not in u.name.lower() and search not in u.email.lower():
                continue
            self.user_tree.insert("", END, iid=u.id, values=(
                u.name, u.email, u.phone,
                "Sí" if u.active else "No",
                len(u.borrowed_books)
            ))

    def _on_user_select(self, event):
        sel = self.user_tree.selection()
        if not sel:
            self.selected_user_id = None
            self.user_update_btn.config(state="disabled")
            self.user_delete_btn.config(state="disabled")
            return

        self.selected_user_id = sel[0]
        self.user_update_btn.config(state="normal")
        self.user_delete_btn.config(state="normal")

        user = self.user_mgr.load(self.selected_user_id)
        if user:
            self.user_vars['user_name'].set(user.name)
            self.user_vars['user_email'].set(user.email)
            self.user_vars['user_phone'].set(user.phone)
            self.user_vars['user_address'].set(user.address)

    def _add_user(self):
        name = self.user_vars['user_name'].get().strip()
        email = self.user_vars['user_email'].get().strip()
        if not name or not email:
            messagebox.showwarning("Nombre y email son obligatorios", "Campo requerido")
            return

        try:
            user = User(
                name=name,
                email=email,
                phone=self.user_vars['user_phone'].get().strip(),
                address=self.user_vars['user_address'].get().strip()
            )
            if self.user_mgr.save(user):
                self._refresh_users()
                self._clear_user_form()
                self.status_var.set(f"Usuario '{name}' agregado")
        except ValueError as e:
            messagebox.showerror(str(e), "Error de validación")

    def _update_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("Seleccione un usuario", "Debe seleccionar un usuario para actualizar")
            return

        user = self.user_mgr.load(self.selected_user_id)
        if not user:
            return

        name = self.user_vars['user_name'].get().strip()
        email = self.user_vars['user_email'].get().strip()
        if not name or not email:
            messagebox.showwarning("Nombre y email son obligatorios", "Campo requerido")
            return

        user.name = name
        user.email = email
        user.phone = self.user_vars['user_phone'].get().strip()
        user.address = self.user_vars['user_address'].get().strip()

        if self.user_mgr.save(user):
            self._refresh_users()
            self.status_var.set(f"Usuario '{name}' actualizado")

    def _delete_user(self):
        print("DEBUG: _delete_user called!")
        print(f"DEBUG: selected_user_id = {self.selected_user_id}")
        if not self.selected_user_id:
            print("DEBUG: No user selected")
            messagebox.showwarning("Seleccione un usuario", "Debe seleccionar un usuario para eliminar")
            return

        print("DEBUG: Showing user confirmation dialog")
        if messagebox.askyesno("¿Eliminar el usuario seleccionado?", "Confirmar"):
            print("DEBUG: User confirmed deletion")
            if self.user_mgr.delete(self.selected_user_id):
                print("DEBUG: User deleted successfully")
                self._refresh_users()
                self._clear_user_form()
                self.status_var.set("Usuario eliminado")
                self.logger.log_operation("DELETE", "User", self.selected_user_id, True)
            else:
                print("DEBUG: Failed to delete user")
                messagebox.showerror("Error al eliminar", "No se pudo eliminar el usuario")

    def _clear_user_form(self):
        for var in self.user_vars.values():
            var.set("")
        self.selected_user_id = None
        self.user_update_btn.config(state="disabled")
        self.user_delete_btn.config(state="disabled")

    # ══════════════════════════════════════════
    #  PESTAÑA ESTADÍSTICAS
    # ══════════════════════════════════════════
    def _build_stats_tab(self):
        # Contenedor principal scrollable
        container = ttk.Frame(self.tab_stats)
        container.pack(fill=tk.BOTH, expand=True)

        # Botón de refresco
        ttk.Button(container, text="🔄 Actualizar estadísticas",
                   command=self._refresh_stats).pack(pady=(0, 10))

        # Métricas principales
        self.stats_frame = ttk.Frame(container)
        self.stats_frame.pack(fill=tk.BOTH, expand=True)

        # Fila de tarjetas de métricas
        cards_frame = ttk.Frame(self.stats_frame)
        cards_frame.pack(fill=tk.X, pady=(0, 15))

        self.stat_cards = {}
        metrics = [
            ("total_books", "📖 Total Libros", "info"),
            ("total_authors", "✍️ Total Autores", "success"),
            ("total_users", "👤 Total Usuarios", "warning"),
            ("available_books", "✅ Disponibles", "primary"),
            ("current_format", "💾 Formato Actual", "secondary"),
        ]

        for key, title, style in metrics:
            card = ttk.LabelFrame(cards_frame, text=title)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            var = tk.StringVar(value="0")
            self.stat_cards[key] = var
            ttk.Label(card, textvariable=var, font=("Helvetica", 28, "bold"),
                      anchor=tk.CENTER).pack(fill=tk.X)

        # Detalles
        details_frame = ttk.Frame(self.stats_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)

        # Libros por género
        genre_frame = ttk.LabelFrame(details_frame, text="📊 Libros por género",
                                      padding=10)
        genre_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.genre_tree = ttk.Treeview(genre_frame, columns=("genre", "count"),
                                        show="headings", height=10)
        self.genre_tree.heading("genre", text="Género")
        self.genre_tree.heading("count", text="Cantidad")
        self.genre_tree.column("genre", width=200)
        self.genre_tree.column("count", width=80, anchor=tk.CENTER)
        self.genre_tree.pack(fill=tk.BOTH, expand=True)

        # Libros por autor
        author_frame = ttk.LabelFrame(details_frame, text="📊 Libros por autor",
                                       padding=10)
        author_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.author_stats_tree = ttk.Treeview(author_frame, columns=("author", "count"),
                                               show="headings", height=10)
        self.author_stats_tree.heading("author", text="Autor")
        self.author_stats_tree.heading("count", text="Libros")
        self.author_stats_tree.column("author", width=200)
        self.author_stats_tree.column("count", width=80, anchor=tk.CENTER)
        self.author_stats_tree.pack(fill=tk.BOTH, expand=True)

    def _refresh_stats(self):
        books = self.book_mgr.load_all()
        authors = self.author_mgr.load_all()
        users = self.user_mgr.load_all()

        self.stat_cards['total_books'].set(str(len(books)))
        self.stat_cards['total_authors'].set(str(len(authors)))
        self.stat_cards['total_users'].set(str(len(users)))
        self.stat_cards['available_books'].set(str(sum(1 for b in books if b.available)))
        self.stat_cards['current_format'].set(self.format_type.upper())

        # Libros por género
        for item in self.genre_tree.get_children():
            self.genre_tree.delete(item)

        genres = {}
        for b in books:
            g = b.genre or "Sin género"
            genres[g] = genres.get(g, 0) + 1

        for genre, count in sorted(genres.items(), key=lambda x: -x[1]):
            self.genre_tree.insert("", END, values=(genre, count))

        # Libros por autor
        for item in self.author_stats_tree.get_children():
            self.author_stats_tree.delete(item)

        author_names = {a.id: a.name for a in authors}
        author_counts = {}
        for b in books:
            name = author_names.get(b.author_id, "Desconocido")
            author_counts[name] = author_counts.get(name, 0) + 1

        for name, count in sorted(author_counts.items(), key=lambda x: -x[1]):
            self.author_stats_tree.insert("", END, values=(name, count))

    # ─────────────── Refreshing global ───────────────
    def _refresh_all(self):
        self._refresh_books()
        self._refresh_authors()
        self._refresh_users()
        self._refresh_stats()

    # ─────────────── Ejecutar ───────────────
    def run(self):
        self.root.mainloop()


# ════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════════════
def main():
    app = BibliotecaApp()
    app.run()


if __name__ == "__main__":
    main()
