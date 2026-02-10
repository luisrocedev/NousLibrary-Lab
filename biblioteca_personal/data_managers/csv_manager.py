"""
Gestor de datos para archivos CSV (.csv)

Implementa el almacenamiento de datos usando archivos CSV (Comma Separated Values)
con cabeceras, utilizando csv.DictReader y csv.DictWriter de la librería estándar.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

from models import Book, Author, User
from data_managers import BookDataManager, AuthorDataManager, UserDataManager


class CSVBookDataManager(BookDataManager):
    """Gestor de libros en formato CSV"""

    FIELDNAMES = [
        'id', 'title', 'author_id', 'isbn', 'publication_year',
        'genre', 'description', 'pages', 'language', 'publisher',
        'available', 'borrowed_by', 'borrow_date', 'due_date'
    ]

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "books.csv"

    def _write_all(self, books: List[Book]) -> bool:
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
                for b in books:
                    writer.writerow(b.to_dict())
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo CSV libros: {e}")
            return False

    def save(self, entity: Book) -> bool:
        try:
            books = self.load_all()
            found = False
            for i, b in enumerate(books):
                if b.id == entity.id:
                    books[i] = entity
                    found = True
                    break
            if not found:
                books.append(entity)
            return self._write_all(books)
        except Exception as e:
            self.logger.error(f"Error guardando libro CSV: {e}")
            return False

    def load(self, entity_id: str) -> Optional[Book]:
        for b in self.load_all():
            if b.id == entity_id:
                return b
        return None

    def load_all(self) -> List[Book]:
        books = []
        if not self.file_path.exists():
            return books
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convertir tipos
                    if row.get('publication_year') and row['publication_year'] != '':
                        row['publication_year'] = int(row['publication_year'])
                    else:
                        row['publication_year'] = None
                    if row.get('pages') and row['pages'] != '' and row['pages'] != 'None':
                        row['pages'] = int(row['pages'])
                    else:
                        row['pages'] = None
                    row['available'] = row.get('available', 'True') in ('True', 'true', '1', True)
                    for k in ('borrowed_by', 'borrow_date', 'due_date'):
                        if row.get(k) in ('', 'None', None):
                            row[k] = None
                    try:
                        books.append(Book.from_dict(row))
                    except Exception as e:
                        self.logger.warning(f"Error cargando fila CSV libro: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo CSV libros: {e}")
        return books

    def delete(self, entity_id: str) -> bool:
        books = [b for b in self.load_all() if b.id != entity_id]
        return self._write_all(books)

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
                            match = False
                            break
                    elif bv != v:
                        match = False
                        break
                else:
                    match = False
                    break
            if match:
                results.append(b)
        return results


class CSVAuthorDataManager(AuthorDataManager):
    """Gestor de autores en formato CSV"""

    FIELDNAMES = ['id', 'name', 'birth_date', 'nationality', 'biography', 'books']

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "authors.csv"

    def _write_all(self, authors: List[Author]) -> bool:
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
                for a in authors:
                    d = a.to_dict()
                    d['books'] = ';'.join(d.get('books', []))
                    writer.writerow(d)
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo CSV autores: {e}")
            return False

    def save(self, entity: Author) -> bool:
        try:
            authors = self.load_all()
            found = False
            for i, a in enumerate(authors):
                if a.id == entity.id:
                    authors[i] = entity
                    found = True
                    break
            if not found:
                authors.append(entity)
            return self._write_all(authors)
        except Exception as e:
            self.logger.error(f"Error guardando autor CSV: {e}")
            return False

    def load(self, entity_id: str) -> Optional[Author]:
        for a in self.load_all():
            if a.id == entity_id:
                return a
        return None

    def load_all(self) -> List[Author]:
        authors = []
        if not self.file_path.exists():
            return authors
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for k in ('birth_date',):
                        if row.get(k) in ('', 'None', None):
                            row[k] = None
                    books_str = row.get('books', '')
                    row['books'] = [x for x in books_str.split(';') if x] if books_str else []
                    try:
                        authors.append(Author.from_dict(row))
                    except Exception as e:
                        self.logger.warning(f"Error cargando fila CSV autor: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo CSV autores: {e}")
        return authors

    def delete(self, entity_id: str) -> bool:
        authors = [a for a in self.load_all() if a.id != entity_id]
        return self._write_all(authors)

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


class CSVUserDataManager(UserDataManager):
    """Gestor de usuarios en formato CSV"""

    FIELDNAMES = [
        'id', 'name', 'email', 'phone', 'address',
        'registration_date', 'active', 'borrowed_books', 'max_books'
    ]

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "users.csv"

    def _write_all(self, users: List[User]) -> bool:
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
                for u in users:
                    d = u.to_dict()
                    d['borrowed_books'] = ';'.join(d.get('borrowed_books', []))
                    writer.writerow(d)
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo CSV usuarios: {e}")
            return False

    def save(self, entity: User) -> bool:
        try:
            users = self.load_all()
            found = False
            for i, u in enumerate(users):
                if u.id == entity.id:
                    users[i] = entity
                    found = True
                    break
            if not found:
                users.append(entity)
            return self._write_all(users)
        except Exception as e:
            self.logger.error(f"Error guardando usuario CSV: {e}")
            return False

    def load(self, entity_id: str) -> Optional[User]:
        for u in self.load_all():
            if u.id == entity_id:
                return u
        return None

    def load_all(self) -> List[User]:
        users = []
        if not self.file_path.exists():
            return users
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['active'] = row.get('active', 'True') in ('True', 'true', '1', True)
                    row['max_books'] = int(row.get('max_books', 5))
                    books_str = row.get('borrowed_books', '')
                    row['borrowed_books'] = [x for x in books_str.split(';') if x] if books_str else []
                    try:
                        users.append(User.from_dict(row))
                    except Exception as e:
                        self.logger.warning(f"Error cargando fila CSV usuario: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo CSV usuarios: {e}")
        return users

    def delete(self, entity_id: str) -> bool:
        users = [u for u in self.load_all() if u.id != entity_id]
        return self._write_all(users)

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
