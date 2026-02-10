"""
Gestor de datos para archivos XML (.xml)

Implementa el almacenamiento de datos usando archivos XML con
xml.etree.ElementTree de la librería estándar de Python.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import List, Dict, Any, Optional

from models import Book, Author, User
from data_managers import BookDataManager, AuthorDataManager, UserDataManager


def _prettify(elem: ET.Element) -> str:
    """Devuelve un XML con indentación legible"""
    rough = ET.tostring(elem, encoding='unicode')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ")


def _dict_to_xml(parent: ET.Element, tag: str, data: dict) -> ET.Element:
    """Convierte un diccionario en un subelemento XML"""
    elem = ET.SubElement(parent, tag)
    for k, v in data.items():
        child = ET.SubElement(elem, k)
        if isinstance(v, list):
            child.text = ';'.join(str(x) for x in v)
        elif v is None:
            child.text = ''
        else:
            child.text = str(v)
    return elem


def _xml_to_dict(elem: ET.Element) -> dict:
    """Convierte un elemento XML en diccionario"""
    d = {}
    for child in elem:
        text = child.text if child.text else ''
        d[child.tag] = text
    return d


class XMLBookDataManager(BookDataManager):
    """Gestor de libros en formato XML"""

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "books.xml"

    def _write_all(self, books: List[Book]) -> bool:
        try:
            root = ET.Element("library")
            books_elem = ET.SubElement(root, "books")
            for b in books:
                _dict_to_xml(books_elem, "book", b.to_dict())
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(_prettify(root))
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo XML libros: {e}")
            return False

    def _parse_book_dict(self, d: dict) -> dict:
        """Convierte tipos de cadena a los tipos correctos para Book"""
        if d.get('publication_year') and d['publication_year'] not in ('', 'None'):
            d['publication_year'] = int(d['publication_year'])
        else:
            d['publication_year'] = None
        if d.get('pages') and d['pages'] not in ('', 'None'):
            d['pages'] = int(d['pages'])
        else:
            d['pages'] = None
        d['available'] = d.get('available', 'True') in ('True', 'true', '1')
        for k in ('borrowed_by', 'borrow_date', 'due_date'):
            if d.get(k) in ('', 'None'):
                d[k] = None
        return d

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
            self.logger.error(f"Error guardando libro XML: {e}")
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
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            books_elem = root.find("books")
            if books_elem is None:
                return books
            for book_elem in books_elem.findall("book"):
                d = self._parse_book_dict(_xml_to_dict(book_elem))
                try:
                    books.append(Book.from_dict(d))
                except Exception as e:
                    self.logger.warning(f"Error cargando libro XML: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo XML libros: {e}")
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


class XMLAuthorDataManager(AuthorDataManager):
    """Gestor de autores en formato XML"""

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "authors.xml"

    def _write_all(self, authors: List[Author]) -> bool:
        try:
            root = ET.Element("library")
            authors_elem = ET.SubElement(root, "authors")
            for a in authors:
                _dict_to_xml(authors_elem, "author", a.to_dict())
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(_prettify(root))
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo XML autores: {e}")
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
            self.logger.error(f"Error guardando autor XML: {e}")
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
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            authors_elem = root.find("authors")
            if authors_elem is None:
                return authors
            for author_elem in authors_elem.findall("author"):
                d = _xml_to_dict(author_elem)
                for k in ('birth_date',):
                    if d.get(k) in ('', 'None'):
                        d[k] = None
                books_str = d.get('books', '')
                d['books'] = [x for x in books_str.split(';') if x] if books_str else []
                try:
                    authors.append(Author.from_dict(d))
                except Exception as e:
                    self.logger.warning(f"Error cargando autor XML: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo XML autores: {e}")
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


class XMLUserDataManager(UserDataManager):
    """Gestor de usuarios en formato XML"""

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "users.xml"

    def _write_all(self, users: List[User]) -> bool:
        try:
            root = ET.Element("library")
            users_elem = ET.SubElement(root, "users")
            for u in users:
                _dict_to_xml(users_elem, "user", u.to_dict())
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(_prettify(root))
            return True
        except Exception as e:
            self.logger.error(f"Error escribiendo XML usuarios: {e}")
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
            self.logger.error(f"Error guardando usuario XML: {e}")
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
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            users_elem = root.find("users")
            if users_elem is None:
                return users
            for user_elem in users_elem.findall("user"):
                d = _xml_to_dict(user_elem)
                d['active'] = d.get('active', 'True') in ('True', 'true', '1')
                d['max_books'] = int(d.get('max_books', 5))
                books_str = d.get('borrowed_books', '')
                d['borrowed_books'] = [x for x in books_str.split(';') if x] if books_str else []
                try:
                    users.append(User.from_dict(d))
                except Exception as e:
                    self.logger.warning(f"Error cargando usuario XML: {e}")
        except Exception as e:
            self.logger.error(f"Error leyendo XML usuarios: {e}")
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
