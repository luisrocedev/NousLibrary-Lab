"""
Gestor de datos para archivos de texto plano (.txt)

Este módulo implementa el manejo de datos usando archivos de texto
con formato estructurado para almacenar libros, autores y usuarios.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from models import Book, Author, User
from data_managers import BookDataManager, AuthorDataManager, UserDataManager

class TXTBookDataManager(BookDataManager):
    """
    Gestor de libros para archivos TXT
    """

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "books.txt"

    def save(self, entity: Book) -> bool:
        """Guarda un libro en archivo TXT"""
        try:
            # Cargar todos los libros existentes
            books = self.load_all()

            # Actualizar o agregar el libro
            found = False
            for i, book in enumerate(books):
                if book.id == entity.id:
                    books[i] = entity
                    found = True
                    break

            if not found:
                books.append(entity)

            # Guardar todos los libros
            return self._save_all_books(books)

        except Exception as e:
            self.logger.error(f"Error al guardar libro TXT: {e}")
            return False

    def load(self, entity_id: str) -> Optional[Book]:
        """Carga un libro desde archivo TXT"""
        try:
            books = self.load_all()
            for book in books:
                if book.id == entity_id:
                    return book
            return None
        except Exception as e:
            self.logger.error(f"Error al cargar libro TXT: {e}")
            return None

    def load_all(self) -> List[Book]:
        """Carga todos los libros desde archivo TXT"""
        books = []
        try:
            if not self.file_path.exists():
                return books

            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if not content:
                return books

            # El archivo contiene un JSON array de libros
            books_data = json.loads(content)
            for book_data in books_data:
                try:
                    book = Book.from_dict(book_data)
                    books.append(book)
                except Exception as e:
                    self.logger.warning(f"Error al cargar libro {book_data.get('id', 'desconocido')}: {e}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Error al parsear archivo TXT de libros: {e}")
        except Exception as e:
            self.logger.error(f"Error al cargar libros TXT: {e}")

        return books

    def delete(self, entity_id: str) -> bool:
        """Elimina un libro del archivo TXT"""
        try:
            books = self.load_all()
            books = [book for book in books if book.id != entity_id]

            return self._save_all_books(books)

        except Exception as e:
            self.logger.error(f"Error al eliminar libro TXT: {e}")
            return False

    def exists(self, entity_id: str) -> bool:
        """Verifica si un libro existe"""
        return self.load(entity_id) is not None

    def search(self, criteria: Dict[str, Any]) -> List[Book]:
        """Busca libros que cumplan con los criterios"""
        try:
            books = self.load_all()
            results = []

            for book in books:
                match = True
                for key, value in criteria.items():
                    if hasattr(book, key):
                        book_value = getattr(book, key)
                        if isinstance(book_value, str) and isinstance(value, str):
                            # Búsqueda case-insensitive para strings
                            if value.lower() not in book_value.lower():
                                match = False
                                break
                        elif book_value != value:
                            match = False
                            break
                    else:
                        match = False
                        break

                if match:
                    results.append(book)

            return results

        except Exception as e:
            self.logger.error(f"Error al buscar libros TXT: {e}")
            return []

    def _save_all_books(self, books: List[Book]) -> bool:
        """Guarda todos los libros en el archivo TXT"""
        try:
            # Convertir libros a diccionarios
            books_data = [book.to_dict() for book in books]

            # Guardar como JSON
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(books_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            self.logger.error(f"Error al guardar libros TXT: {e}")
            return False

class TXTAuthorDataManager(AuthorDataManager):
    """
    Gestor de autores para archivos TXT
    """

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "authors.txt"

    def save(self, entity: Author) -> bool:
        """Guarda un autor en archivo TXT"""
        try:
            authors = self.load_all()

            # Actualizar o agregar el autor
            found = False
            for i, author in enumerate(authors):
                if author.id == entity.id:
                    authors[i] = entity
                    found = True
                    break

            if not found:
                authors.append(entity)

            return self._save_all_authors(authors)

        except Exception as e:
            self.logger.error(f"Error al guardar autor TXT: {e}")
            return False

    def load(self, entity_id: str) -> Optional[Author]:
        """Carga un autor desde archivo TXT"""
        try:
            authors = self.load_all()
            for author in authors:
                if author.id == entity_id:
                    return author
            return None
        except Exception as e:
            self.logger.error(f"Error al cargar autor TXT: {e}")
            return None

    def load_all(self) -> List[Author]:
        """Carga todos los autores desde archivo TXT"""
        authors = []
        try:
            if not self.file_path.exists():
                return authors

            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if not content:
                return authors

            authors_data = json.loads(content)
            for author_data in authors_data:
                try:
                    author = Author.from_dict(author_data)
                    authors.append(author)
                except Exception as e:
                    self.logger.warning(f"Error al cargar autor {author_data.get('id', 'desconocido')}: {e}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Error al parsear archivo TXT de autores: {e}")
        except Exception as e:
            self.logger.error(f"Error al cargar autores TXT: {e}")

        return authors

    def delete(self, entity_id: str) -> bool:
        """Elimina un autor del archivo TXT"""
        try:
            authors = self.load_all()
            authors = [author for author in authors if author.id != entity_id]

            return self._save_all_authors(authors)

        except Exception as e:
            self.logger.error(f"Error al eliminar autor TXT: {e}")
            return False

    def exists(self, entity_id: str) -> bool:
        """Verifica si un autor existe"""
        return self.load(entity_id) is not None

    def search(self, criteria: Dict[str, Any]) -> List[Author]:
        """Busca autores que cumplan con los criterios"""
        try:
            authors = self.load_all()
            results = []

            for author in authors:
                match = True
                for key, value in criteria.items():
                    if hasattr(author, key):
                        author_value = getattr(author, key)
                        if isinstance(author_value, str) and isinstance(value, str):
                            if value.lower() not in author_value.lower():
                                match = False
                                break
                        elif author_value != value:
                            match = False
                            break
                    else:
                        match = False
                        break

                if match:
                    results.append(author)

            return results

        except Exception as e:
            self.logger.error(f"Error al buscar autores TXT: {e}")
            return []

    def _save_all_authors(self, authors: List[Author]) -> bool:
        """Guarda todos los autores en el archivo TXT"""
        try:
            authors_data = [author.to_dict() for author in authors]

            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(authors_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            self.logger.error(f"Error al guardar autores TXT: {e}")
            return False

class TXTUserDataManager(UserDataManager):
    """
    Gestor de usuarios para archivos TXT
    """

    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "users.txt"

    def save(self, entity: User) -> bool:
        """Guarda un usuario en archivo TXT"""
        try:
            users = self.load_all()

            # Actualizar o agregar el usuario
            found = False
            for i, user in enumerate(users):
                if user.id == entity.id:
                    users[i] = entity
                    found = True
                    break

            if not found:
                users.append(entity)

            return self._save_all_users(users)

        except Exception as e:
            self.logger.error(f"Error al guardar usuario TXT: {e}")
            return False

    def load(self, entity_id: str) -> Optional[User]:
        """Carga un usuario desde archivo TXT"""
        try:
            users = self.load_all()
            for user in users:
                if user.id == entity_id:
                    return user
            return None
        except Exception as e:
            self.logger.error(f"Error al cargar usuario TXT: {e}")
            return None

    def load_all(self) -> List[User]:
        """Carga todos los usuarios desde archivo TXT"""
        users = []
        try:
            if not self.file_path.exists():
                return users

            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if not content:
                return users

            users_data = json.loads(content)
            for user_data in users_data:
                try:
                    user = User.from_dict(user_data)
                    users.append(user)
                except Exception as e:
                    self.logger.warning(f"Error al cargar usuario {user_data.get('id', 'desconocido')}: {e}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Error al parsear archivo TXT de usuarios: {e}")
        except Exception as e:
            self.logger.error(f"Error al cargar usuarios TXT: {e}")

        return users

    def delete(self, entity_id: str) -> bool:
        """Elimina un usuario del archivo TXT"""
        try:
            users = self.load_all()
            users = [user for user in users if user.id != entity_id]

            return self._save_all_users(users)

        except Exception as e:
            self.logger.error(f"Error al eliminar usuario TXT: {e}")
            return False

    def exists(self, entity_id: str) -> bool:
        """Verifica si un usuario existe"""
        return self.load(entity_id) is not None

    def search(self, criteria: Dict[str, Any]) -> List[User]:
        """Busca usuarios que cumplan con los criterios"""
        try:
            users = self.load_all()
            results = []

            for user in users:
                match = True
                for key, value in criteria.items():
                    if hasattr(user, key):
                        user_value = getattr(user, key)
                        if isinstance(user_value, str) and isinstance(value, str):
                            if value.lower() not in user_value.lower():
                                match = False
                                break
                        elif user_value != value:
                            match = False
                            break
                    else:
                        match = False
                        break

                if match:
                    results.append(user)

            return results

        except Exception as e:
            self.logger.error(f"Error al buscar usuarios TXT: {e}")
            return []

    def _save_all_users(self, users: List[User]) -> bool:
        """Guarda todos los usuarios en el archivo TXT"""
        try:
            users_data = [user.to_dict() for user in users]

            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            self.logger.error(f"Error al guardar usuarios TXT: {e}")
            return False