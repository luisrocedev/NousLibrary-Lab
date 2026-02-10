"""
Modelos de datos del framework

Incluye todas las entidades del sistema con validación completa.

Autor: DAM2526
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


@dataclass
class BaseEntity:
    """Entidad base con campos comunes."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

    def to_dict(self) -> Dict[str, Any]:
        """Convertir entidad a diccionario."""
        result = {}
        for field_name, field_info in self.__dataclass_fields__.items():
            value = getattr(self, field_name)
            if isinstance(value, datetime):
                result[field_name] = value.isoformat()
            else:
                result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """Crear entidad desde diccionario."""
        # Convertir strings de fecha a objetos datetime
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class Book(BaseEntity):
    """Modelo de Libro."""
    title: str = ""
    author_id: str = ""
    isbn: str = ""
    genre: str = ""
    language: str = "Español"
    year: int = datetime.now().year
    pages: int = 0
    category_id: Optional[str] = None
    available: bool = True

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        """Validar campos del libro."""
        if not self.title.strip():
            raise ValueError("El título es obligatorio")

        if self.isbn and not self._validate_isbn(self.isbn):
            raise ValueError("ISBN inválido")

        if self.year < 1000 or self.year > datetime.now().year + 1:
            raise ValueError("Año de publicación inválido")

        if self.pages < 0:
            raise ValueError("Número de páginas no puede ser negativo")

    def _validate_isbn(self, isbn: str) -> bool:
        """Validar ISBN-10 o ISBN-13."""
        isbn = isbn.replace("-", "").replace(" ", "")

        if len(isbn) == 10:
            # ISBN-10
            try:
                total = sum(int(isbn[i]) * (10 - i) for i in range(9))
                check_digit = (11 - (total % 11)) % 11
                return str(check_digit if check_digit < 10 else 'X') == isbn[9].upper()
            except ValueError:
                return False

        elif len(isbn) == 13:
            # ISBN-13
            try:
                total = sum(int(isbn[i]) * (1 if i % 2 == 0 else 3) for i in range(12))
                check_digit = (10 - (total % 10)) % 10
                return str(check_digit) == isbn[12]
            except ValueError:
                return False

        return False


@dataclass
class Author(BaseEntity):
    """Modelo de Autor."""
    name: str = ""
    last_name: str = ""
    birth_date: Optional[datetime] = None
    nationality: str = ""
    biography: str = ""

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.birth_date, str):
            self.birth_date = datetime.fromisoformat(self.birth_date)
        self._validate()

    def _validate(self):
        """Validar campos del autor."""
        if not self.name.strip():
            raise ValueError("El nombre es obligatorio")

        if not self.last_name.strip():
            raise ValueError("Los apellidos son obligatorios")

        if self.birth_date and self.birth_date > datetime.now():
            raise ValueError("La fecha de nacimiento no puede ser futura")

    @property
    def full_name(self) -> str:
        """Nombre completo del autor."""
        return f"{self.name} {self.last_name}"


@dataclass
class User(BaseEntity):
    """Modelo de Usuario."""
    name: str = ""
    last_name: str = ""
    email: str = ""
    password_hash: str = ""
    role: str = "user"  # user, admin, librarian
    active: bool = True

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        """Validar campos del usuario."""
        if not self.name.strip():
            raise ValueError("El nombre es obligatorio")

        if not self.last_name.strip():
            raise ValueError("Los apellidos son obligatorios")

        if not self._validate_email(self.email):
            raise ValueError("Email inválido")

        if self.role not in ["user", "admin", "librarian"]:
            raise ValueError("Rol de usuario inválido")

    def _validate_email(self, email: str) -> bool:
        """Validar formato de email."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @property
    def full_name(self) -> str:
        """Nombre completo del usuario."""
        return f"{self.name} {self.last_name}"

    def set_password(self, password: str):
        """Establecer contraseña hasheada."""
        import hashlib
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        """Verificar contraseña."""
        import hashlib
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


@dataclass
class Category(BaseEntity):
    """Modelo de Categoría."""
    name: str = ""
    description: str = ""
    parent_id: Optional[str] = None  # Para categorías jerárquicas

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        """Validar campos de la categoría."""
        if not self.name.strip():
            raise ValueError("El nombre de la categoría es obligatorio")


@dataclass
class Loan(BaseEntity):
    """Modelo de Préstamo."""
    book_id: str = ""
    user_id: str = ""
    loan_date: datetime = field(default_factory=datetime.now)
    due_date: datetime = field(default_factory=lambda: datetime.now().replace(day=datetime.now().day + 14))
    return_date: Optional[datetime] = None
    status: str = "active"  # active, returned, overdue
    notes: str = ""

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.loan_date, str):
            self.loan_date = datetime.fromisoformat(self.loan_date)
        if isinstance(self.due_date, str):
            self.due_date = datetime.fromisoformat(self.due_date)
        if isinstance(self.return_date, str):
            self.return_date = datetime.fromisoformat(self.return_date)
        self._validate()

    def _validate(self):
        """Validar campos del préstamo."""
        if not self.book_id:
            raise ValueError("El ID del libro es obligatorio")

        if not self.user_id:
            raise ValueError("El ID del usuario es obligatorio")

        if self.loan_date > self.due_date:
            raise ValueError("La fecha de préstamo no puede ser posterior a la fecha de vencimiento")

        if self.return_date and self.return_date < self.loan_date:
            raise ValueError("La fecha de devolución no puede ser anterior a la fecha de préstamo")

        if self.status not in ["active", "returned", "overdue"]:
            raise ValueError("Estado de préstamo inválido")

    @property
    def is_overdue(self) -> bool:
        """Verificar si el préstamo está vencido."""
        return self.status == "active" and datetime.now() > self.due_date

    @property
    def days_overdue(self) -> int:
        """Días de retraso."""
        if not self.is_overdue:
            return 0
        return (datetime.now() - self.due_date).days

    def return_book(self, return_date: datetime = None):
        """Marcar libro como devuelto."""
        self.return_date = return_date or datetime.now()
        self.status = "returned"
        self.updated_at = datetime.now()

    def mark_overdue(self):
        """Marcar préstamo como vencido."""
        self.status = "overdue"
        self.updated_at = datetime.now()


# Exportar todas las clases
__all__ = ["Book", "Author", "User", "Loan", "Category", "BaseEntity"]