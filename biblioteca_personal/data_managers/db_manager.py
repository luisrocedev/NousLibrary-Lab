"""
Gestor de datos para base de datos SQLite (.db)

Implementa el almacenamiento de datos usando SQLite3 de la librería estándar
de Python, con tablas relacionales para libros, autores y usuarios.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from models import Book, Author, User
from data_managers import BookDataManager, AuthorDataManager, UserDataManager


class SQLiteConnection:
    """Gestor de conexión SQLite compartido"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_tables()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_tables(self):
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS authors (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    birth_date TEXT,
                    nationality TEXT DEFAULT '',
                    biography TEXT DEFAULT '',
                    books TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS books (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    author_id TEXT NOT NULL,
                    isbn TEXT DEFAULT '',
                    publication_year INTEGER,
                    genre TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    pages INTEGER,
                    language TEXT DEFAULT 'Español',
                    publisher TEXT DEFAULT '',
                    available INTEGER DEFAULT 1,
                    borrowed_by TEXT,
                    borrow_date TEXT,
                    due_date TEXT
                );
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT DEFAULT '',
                    address TEXT DEFAULT '',
                    registration_date TEXT,
                    active INTEGER DEFAULT 1,
                    borrowed_books TEXT DEFAULT '',
                    max_books INTEGER DEFAULT 5
                );
            """)
            conn.commit()
        finally:
            conn.close()


class DBBookDataManager(BookDataManager):
    """Gestor de libros en SQLite"""

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.db_path = str(self.base_path / "biblioteca.db")
        self.sqlite = SQLiteConnection(self.db_path)

    def save(self, entity: Book) -> bool:
        try:
            conn = self.sqlite._get_conn()
            d = entity.to_dict()
            d['available'] = 1 if d['available'] else 0
            conn.execute("""
                INSERT OR REPLACE INTO books
                (id, title, author_id, isbn, publication_year, genre,
                 description, pages, language, publisher, available,
                 borrowed_by, borrow_date, due_date)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (d['id'], d['title'], d['author_id'], d['isbn'],
                  d['publication_year'], d['genre'], d['description'],
                  d['pages'], d['language'], d['publisher'], d['available'],
                  d['borrowed_by'], d['borrow_date'], d['due_date']))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error guardando libro SQLite: {e}")
            return False

    def load(self, entity_id: str) -> Optional[Book]:
        try:
            conn = self.sqlite._get_conn()
            row = conn.execute("SELECT * FROM books WHERE id=?", (entity_id,)).fetchone()
            conn.close()
            if row:
                return self._row_to_book(dict(row))
            return None
        except Exception as e:
            self.logger.error(f"Error cargando libro SQLite: {e}")
            return None

    def load_all(self) -> List[Book]:
        books = []
        try:
            conn = self.sqlite._get_conn()
            rows = conn.execute("SELECT * FROM books").fetchall()
            conn.close()
            for row in rows:
                try:
                    books.append(self._row_to_book(dict(row)))
                except Exception as e:
                    self.logger.warning(f"Error parseando libro SQLite: {e}")
        except Exception as e:
            self.logger.error(f"Error listando libros SQLite: {e}")
        return books

    def delete(self, entity_id: str) -> bool:
        try:
            conn = self.sqlite._get_conn()
            conn.execute("DELETE FROM books WHERE id=?", (entity_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error eliminando libro SQLite: {e}")
            return False

    def exists(self, entity_id: str) -> bool:
        return self.load(entity_id) is not None

    def search(self, criteria: Dict[str, Any]) -> List[Book]:
        results = []
        for b in self.load_all():
            match = True
            for k, v in criteria.items():
                if hasattr(b, k):
                    bv = getattr(b, k)
                    if isinstance(bv, str) and isinstance(v, str):
                        if v.lower() not in bv.lower():
                            match = False; break
                    elif bv != v:
                        match = False; break
                else:
                    match = False; break
            if match:
                results.append(b)
        return results

    @staticmethod
    def _row_to_book(d: dict) -> Book:
        d['available'] = bool(d.get('available', 1))
        for k in ('borrowed_by', 'borrow_date', 'due_date'):
            if d.get(k) in ('', None, 'None'):
                d[k] = None
        return Book.from_dict(d)


class DBAuthorDataManager(AuthorDataManager):
    """Gestor de autores en SQLite"""

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.db_path = str(self.base_path / "biblioteca.db")
        self.sqlite = SQLiteConnection(self.db_path)

    def save(self, entity: Author) -> bool:
        try:
            conn = self.sqlite._get_conn()
            d = entity.to_dict()
            d['books'] = ';'.join(d.get('books', []))
            conn.execute("""
                INSERT OR REPLACE INTO authors
                (id, name, birth_date, nationality, biography, books)
                VALUES (?,?,?,?,?,?)
            """, (d['id'], d['name'], d['birth_date'],
                  d['nationality'], d['biography'], d['books']))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error guardando autor SQLite: {e}")
            return False

    def load(self, entity_id: str) -> Optional[Author]:
        try:
            conn = self.sqlite._get_conn()
            row = conn.execute("SELECT * FROM authors WHERE id=?", (entity_id,)).fetchone()
            conn.close()
            if row:
                return self._row_to_author(dict(row))
            return None
        except Exception as e:
            self.logger.error(f"Error cargando autor SQLite: {e}")
            return None

    def load_all(self) -> List[Author]:
        authors = []
        try:
            conn = self.sqlite._get_conn()
            rows = conn.execute("SELECT * FROM authors").fetchall()
            conn.close()
            for row in rows:
                try:
                    authors.append(self._row_to_author(dict(row)))
                except Exception as e:
                    self.logger.warning(f"Error parseando autor SQLite: {e}")
        except Exception as e:
            self.logger.error(f"Error listando autores SQLite: {e}")
        return authors

    def delete(self, entity_id: str) -> bool:
        try:
            conn = self.sqlite._get_conn()
            conn.execute("DELETE FROM authors WHERE id=?", (entity_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error eliminando autor SQLite: {e}")
            return False

    def exists(self, entity_id: str) -> bool:
        return self.load(entity_id) is not None

    def search(self, criteria: Dict[str, Any]) -> List[Author]:
        results = []
        for a in self.load_all():
            match = True
            for k, v in criteria.items():
                if hasattr(a, k):
                    av = getattr(a, k)
                    if isinstance(av, str) and isinstance(v, str):
                        if v.lower() not in av.lower():
                            match = False; break
                    elif av != v:
                        match = False; break
                else:
                    match = False; break
            if match:
                results.append(a)
        return results

    @staticmethod
    def _row_to_author(d: dict) -> Author:
        for k in ('birth_date',):
            if d.get(k) in ('', None, 'None'):
                d[k] = None
        books_str = d.get('books', '')
        d['books'] = [x for x in books_str.split(';') if x] if books_str else []
        return Author.from_dict(d)


class DBUserDataManager(UserDataManager):
    """Gestor de usuarios en SQLite"""

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.db_path = str(self.base_path / "biblioteca.db")
        self.sqlite = SQLiteConnection(self.db_path)

    def save(self, entity: User) -> bool:
        try:
            conn = self.sqlite._get_conn()
            d = entity.to_dict()
            d['active'] = 1 if d['active'] else 0
            d['borrowed_books'] = ';'.join(d.get('borrowed_books', []))
            conn.execute("""
                INSERT OR REPLACE INTO users
                (id, name, email, phone, address, registration_date,
                 active, borrowed_books, max_books)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (d['id'], d['name'], d['email'], d['phone'],
                  d['address'], d['registration_date'], d['active'],
                  d['borrowed_books'], d['max_books']))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error guardando usuario SQLite: {e}")
            return False

    def load(self, entity_id: str) -> Optional[User]:
        try:
            conn = self.sqlite._get_conn()
            row = conn.execute("SELECT * FROM users WHERE id=?", (entity_id,)).fetchone()
            conn.close()
            if row:
                return self._row_to_user(dict(row))
            return None
        except Exception as e:
            self.logger.error(f"Error cargando usuario SQLite: {e}")
            return None

    def load_all(self) -> List[User]:
        users = []
        try:
            conn = self.sqlite._get_conn()
            rows = conn.execute("SELECT * FROM users").fetchall()
            conn.close()
            for row in rows:
                try:
                    users.append(self._row_to_user(dict(row)))
                except Exception as e:
                    self.logger.warning(f"Error parseando usuario SQLite: {e}")
        except Exception as e:
            self.logger.error(f"Error listando usuarios SQLite: {e}")
        return users

    def delete(self, entity_id: str) -> bool:
        try:
            conn = self.sqlite._get_conn()
            conn.execute("DELETE FROM users WHERE id=?", (entity_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error eliminando usuario SQLite: {e}")
            return False

    def exists(self, entity_id: str) -> bool:
        return self.load(entity_id) is not None

    def search(self, criteria: Dict[str, Any]) -> List[User]:
        results = []
        for u in self.load_all():
            match = True
            for k, v in criteria.items():
                if hasattr(u, k):
                    uv = getattr(u, k)
                    if isinstance(uv, str) and isinstance(v, str):
                        if v.lower() not in uv.lower():
                            match = False; break
                    elif uv != v:
                        match = False; break
                else:
                    match = False; break
            if match:
                results.append(u)
        return results

    @staticmethod
    def _row_to_user(d: dict) -> User:
        d['active'] = bool(d.get('active', 1))
        d['max_books'] = int(d.get('max_books', 5))
        books_str = d.get('borrowed_books', '')
        d['borrowed_books'] = [x for x in books_str.split(';') if x] if books_str else []
        return User.from_dict(d)
