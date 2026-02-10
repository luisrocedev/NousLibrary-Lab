"""
Gestor de datos para archivos JSON (.json)

Implementa el almacenamiento de datos usando archivos JSON nativos
con la librería estándar json de Python.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from models import Book, Author, User
from data_managers import BookDataManager, AuthorDataManager, UserDataManager


class JSONBookDataManager(BookDataManager):
    """Gestor de libros en formato JSON"""

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "books.json"

    def _write_all(self, books: List[Book]) -> bool:
        try:
            data = {"books": [b.to_dict() for b in books]}
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo JSON libros: {e}")
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
            self.logger.error(f"Error guardando libro JSON: {e}")
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
                data = json.load(f)
            for bd in data.get("books", []):
                try:
                    books.append(Book.from_dict(bd))
                except Exception as e:
                    self.logger.warning(f"Error cargando libro JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo JSON libros: {e}")
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
                            match = False; break
                    elif bv != v:
                        match = False; break
                else:
                    match = False; break
            if match:
                results.append(b)
        return results


class JSONAuthorDataManager(AuthorDataManager):
    """Gestor de autores en formato JSON"""

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "authors.json"

    def _write_all(self, authors: List[Author]) -> bool:
        try:
            data = {"authors": [a.to_dict() for a in authors]}
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo JSON autores: {e}")
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
            self.logger.error(f"Error guardando autor JSON: {e}")
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
                data = json.load(f)
            for ad in data.get("authors", []):
                try:
                    authors.append(Author.from_dict(ad))
                except Exception as e:
                    self.logger.warning(f"Error cargando autor JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo JSON autores: {e}")
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


class JSONUserDataManager(UserDataManager):
    """Gestor de usuarios en formato JSON"""

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "users.json"

    def _write_all(self, users: List[User]) -> bool:
        try:
            data = {"users": [u.to_dict() for u in users]}
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo JSON usuarios: {e}")
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
            self.logger.error(f"Error guardando usuario JSON: {e}")
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
                data = json.load(f)
            for ud in data.get("users", []):
                try:
                    users.append(User.from_dict(ud))
                except Exception as e:
                    self.logger.warning(f"Error cargando usuario JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo JSON usuarios: {e}")
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
