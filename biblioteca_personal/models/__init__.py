"""
Modelos de datos para el Sistema de Gestión de Biblioteca Personal

Este módulo define las clases principales que representan las entidades
del sistema: Libro, Autor y Usuario.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

@dataclass
class Author:
    """
    Representa un autor en el sistema de biblioteca
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    birth_date: Optional[datetime] = None
    nationality: str = ""
    biography: str = ""
    books: List[str] = field(default_factory=list)  # IDs de libros

    def __post_init__(self):
        """Validación después de la inicialización"""
        if not self.name.strip():
            raise ValueError("El nombre del autor no puede estar vacío")

    def to_dict(self) -> dict:
        """Convierte el autor a diccionario para serialización"""
        return {
            'id': self.id,
            'name': self.name,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'nationality': self.nationality,
            'biography': self.biography,
            'books': self.books
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Author':
        """Crea un autor desde un diccionario"""
        birth_date = None
        if data.get('birth_date'):
            birth_date = datetime.fromisoformat(data['birth_date'])

        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data['name'],
            birth_date=birth_date,
            nationality=data.get('nationality', ''),
            biography=data.get('biography', ''),
            books=data.get('books', [])
        )

@dataclass
class Book:
    """
    Representa un libro en el sistema de biblioteca
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    author_id: str = ""
    isbn: str = ""
    publication_year: Optional[int] = None
    genre: str = ""
    description: str = ""
    pages: Optional[int] = None
    language: str = "Español"
    publisher: str = ""
    available: bool = True
    borrowed_by: Optional[str] = None  # ID del usuario que lo tiene prestado
    borrow_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    def __post_init__(self):
        """Validación después de la inicialización"""
        if not self.title.strip():
            raise ValueError("El título del libro no puede estar vacío")
        if not self.author_id.strip():
            raise ValueError("El ID del autor no puede estar vacío")

        # Validar ISBN si se proporciona
        if self.isbn and not self._validate_isbn(self.isbn):
            raise ValueError("ISBN inválido")

    def _validate_isbn(self, isbn: str) -> bool:
        """Valida un ISBN-10 o ISBN-13"""
        # Remover guiones y espacios
        isbn = ''.join(c for c in isbn if c.isdigit() or c == 'X')

        if len(isbn) == 10:
            # ISBN-10
            total = 0
            for i, digit in enumerate(isbn[:-1]):
                if not digit.isdigit():
                    return False
                total += int(digit) * (10 - i)
            check_digit = isbn[-1]
            if check_digit == 'X':
                total += 10
            elif check_digit.isdigit():
                total += int(check_digit)
            else:
                return False
            return total % 11 == 0
        elif len(isbn) == 13:
            # ISBN-13
            if not all(c.isdigit() for c in isbn):
                return False
            total = 0
            for i, digit in enumerate(isbn[:-1]):
                weight = 1 if i % 2 == 0 else 3
                total += int(digit) * weight
            check_digit = (10 - (total % 10)) % 10
            return str(check_digit) == isbn[-1]
        return False

    def to_dict(self) -> dict:
        """Convierte el libro a diccionario para serialización"""
        return {
            'id': self.id,
            'title': self.title,
            'author_id': self.author_id,
            'isbn': self.isbn,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'description': self.description,
            'pages': self.pages,
            'language': self.language,
            'publisher': self.publisher,
            'available': self.available,
            'borrowed_by': self.borrowed_by,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Book':
        """Crea un libro desde un diccionario"""
        borrow_date = None
        due_date = None

        if data.get('borrow_date'):
            borrow_date = datetime.fromisoformat(data['borrow_date'])
        if data.get('due_date'):
            due_date = datetime.fromisoformat(data['due_date'])

        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data['title'],
            author_id=data['author_id'],
            isbn=data.get('isbn', ''),
            publication_year=data.get('publication_year'),
            genre=data.get('genre', ''),
            description=data.get('description', ''),
            pages=data.get('pages'),
            language=data.get('language', 'Español'),
            publisher=data.get('publisher', ''),
            available=data.get('available', True),
            borrowed_by=data.get('borrowed_by'),
            borrow_date=borrow_date,
            due_date=due_date
        )

@dataclass
class User:
    """
    Representa un usuario del sistema de biblioteca
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    registration_date: datetime = field(default_factory=datetime.now)
    active: bool = True
    borrowed_books: List[str] = field(default_factory=list)  # IDs de libros prestados
    max_books: int = 5  # Máximo número de libros que puede tener prestados

    def __post_init__(self):
        """Validación después de la inicialización"""
        if not self.name.strip():
            raise ValueError("El nombre del usuario no puede estar vacío")
        if not self.email.strip():
            raise ValueError("El email del usuario no puede estar vacío")

        # Validar email básico
        if '@' not in self.email or '.' not in self.email:
            raise ValueError("Email inválido")

    def can_borrow_book(self) -> bool:
        """Verifica si el usuario puede pedir prestado otro libro"""
        return len(self.borrowed_books) < self.max_books and self.active

    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario para serialización"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'registration_date': self.registration_date.isoformat(),
            'active': self.active,
            'borrowed_books': self.borrowed_books,
            'max_books': self.max_books
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Crea un usuario desde un diccionario"""
        registration_date = datetime.now()
        if data.get('registration_date'):
            registration_date = datetime.fromisoformat(data['registration_date'])

        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            registration_date=registration_date,
            active=data.get('active', True),
            borrowed_books=data.get('borrowed_books', []),
            max_books=data.get('max_books', 5)
        )