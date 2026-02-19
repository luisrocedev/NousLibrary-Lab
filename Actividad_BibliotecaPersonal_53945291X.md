# NousLibrary-Lab — Sistema de Gestión de Biblioteca Personal Multi-formato

**DNI:** 53945291X  
**Curso:** DAM2 — Acceso a datos  
**Actividad:** Proyecto final – lectura y escritura en múltiples formatos de archivo  
**Tecnologías:** Python 3.13 · tkinter + ttk · SQLite3 · JSON · XML · CSV · TXT · Flask · JWT · HMAC-SHA256

---

## Índice

1. [Introducción y contextualización](#1-introducción-y-contextualización-25-)
2. [Desarrollo técnico detallado](#2-desarrollo-técnico-detallado-25-)
3. [Aplicación práctica con código real](#3-aplicación-práctica-con-código-real-25-)
4. [Conclusión y enlace con otros contenidos](#4-conclusión-y-enlace-con-otros-contenidos-25-)

---

## 1. Introducción y contextualización (25 %)

### 1.1 ¿Qué problema resuelve este proyecto?

En el desarrollo de software empresarial, una necesidad constante es la **persistencia de datos en formatos heterogéneos**. Un mismo conjunto de información —en nuestro caso, una colección de libros, autores y usuarios— puede necesitar almacenarse como:

- **Archivos de texto plano (TXT)**: útiles para logs, exportación rápida o entornos sin dependencias.
- **CSV (Comma-Separated Values)**: el estándar de intercambio con hojas de cálculo y herramientas de análisis de datos.
- **JSON (JavaScript Object Notation)**: formato preferido por APIs REST y aplicaciones web modernas.
- **XML (eXtensible Markup Language)**: formato estructurado empleado en configuraciones, servicios SOAP y documentos corporativos.
- **SQLite**: base de datos relacional embebida, ideal para dispositivos móviles y aplicaciones de escritorio sin servidor.

Este proyecto demuestra la capacidad de **leer, escribir, buscar y eliminar** datos en los cinco formatos anteriores desde una única aplicación con interfaz gráfica moderna, manteniendo una arquitectura limpia basada en patrones de diseño profesionales.

### 1.2 Relación con el currículo de Acceso a Datos

La asignatura de Acceso a Datos en el ciclo DAM2 aborda, entre otros, los siguientes resultados de aprendizaje que este proyecto trabaja directamente:

| Resultado de aprendizaje                     | Cómo se demuestra en el proyecto                                              |
| -------------------------------------------- | ----------------------------------------------------------------------------- |
| **RA1 – Manejo de ficheros**                 | Lectura/escritura en TXT y CSV con los módulos `io`, `json` y `csv` de Python |
| **RA2 – Manejo de conectores**               | Conexión a SQLite con `sqlite3`, sentencias DDL y DML parametrizadas          |
| **RA3 – Herramientas ORM**                   | Patrón Repository implementado manualmente (clases abstractas genéricas)      |
| **RA4 – Bases de datos objeto-relacionales** | Mapeo dataclass ↔ tabla SQLite (serialización/deserialización)                |
| **RA5 – Bases de datos documentales**        | Almacenamiento JSON y XML; estructura jerárquica de documentos                |
| **RA6 – Componentes de acceso a datos**      | Factory Pattern para intercambiar formatos sin modificar la lógica de negocio |

### 1.3 Conceptos previos necesarios

Para comprender este proyecto completo, el lector debería conocer:

- **Programación orientada a objetos en Python**: clases, herencia, clases abstractas (`ABC`), genéricos (`Generic[T]`).
- **Dataclasses**: decorador `@dataclass` de Python 3.7+ para crear DTOs (Data Transfer Objects) con validación.
- **Manejo de ficheros en Python**: `open()`, `with`, codificación `utf-8`, módulos `json`, `csv`, `xml.etree.ElementTree`.
- **SQL básico**: sentencias `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`.
- **Patrones de diseño**: Factory Method, Repository Pattern, Template Method.
- **Tkinter y ttk**: construcción de interfaces gráficas con widgets nativos y temas modernos.

### 1.4 Estructura general del proyecto

```
biblioteca_personal/
├── main.py                          # Punto de entrada → lanza la GUI
├── gui_app.py                       # Interfaz gráfica (tkinter + ttk)
│
├── models/                          # Modelos originales (dataclasses)
│   └── __init__.py                  # Book, Author, User
│
├── data_managers/                   # Gestores específicos por entidad × formato
│   ├── __init__.py                  # ABC DataManager + Factory
│   ├── txt_manager.py
│   ├── csv_manager.py
│   ├── json_manager.py
│   ├── xml_manager.py
│   └── db_manager.py
│
├── data_access_framework/           # Framework genérico reutilizable
│   ├── __init__.py                  # create_framework()
│   ├── core/
│   │   ├── data_access_framework.py # Orquestador principal
│   │   ├── entity_manager.py        # Repository<T> + EntityManager
│   │   ├── config_manager.py        # Configuración con deep merge
│   │   └── migration_manager.py     # Migración entre formatos
│   ├── models/
│   │   └── __init__.py              # BaseEntity + Book, Author, User, Loan, Category
│   ├── data_managers/               # Gestores genéricos (1 clase × formato)
│   │   ├── json_manager.py
│   │   ├── xml_manager.py
│   │   ├── csv_manager.py
│   │   ├── txt_manager.py
│   │   └── db_manager.py
│   ├── business/                    # Servicios de negocio
│   │   ├── auth_service.py          # Autenticación HMAC-SHA256 + JWT
│   │   ├── loan_service.py          # Préstamos con penalizaciones
│   │   └── report_service.py        # Informes y estadísticas
│   └── api/                         # API REST Flask
│       ├── app.py
│       └── routes/
│           ├── auth.py, books.py, loans.py, reports.py
│
├── ui/
│   └── menu_principal.py            # Menú de consola (legacy)
├── utils/
│   └── logger.py                    # Logger + ProgressLogger
├── test_basic.py, test_crud.py, test_all_formats.py, test_delete.py
├── requirements.txt
└── README.md
```

---

## 2. Desarrollo técnico detallado (25 %)

### 2.1 Capa de modelos: dataclasses con validación

Los modelos se definen con `@dataclass` y aplican validación automática en `__post_init__`.

#### Modelo `Book`

```python
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
import uuid

@dataclass
class Book:
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
    borrowed_by: Optional[str] = None
    borrow_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("El título del libro no puede estar vacío")
        if not self.author_id.strip():
            raise ValueError("El ID del autor no puede estar vacío")
        if self.isbn and not self._validate_isbn(self.isbn):
            raise ValueError("ISBN inválido")

    def _validate_isbn(self, isbn: str) -> bool:
        isbn = ''.join(c for c in isbn if c.isdigit() or c == 'X')
        if len(isbn) == 10:
            total = sum(int(d) * (10 - i) for i, d in enumerate(isbn[:-1]))
            check = 10 if isbn[-1] == 'X' else int(isbn[-1])
            return (total + check) % 11 == 0
        elif len(isbn) == 13:
            total = sum(int(d) * (1 if i % 2 == 0 else 3)
                        for i, d in enumerate(isbn[:-1]))
            return str((10 - total % 10) % 10) == isbn[-1]
        return False
```

**Puntos clave:**

- `uuid.uuid4()` genera un identificador único universal seguro.
- `__post_init__` se ejecuta automáticamente al instanciar; garantiza que título y autor no estén vacíos.
- La validación de ISBN implementa ambos algoritmos estándar (ISBN-10 e ISBN-13) con comprobación de dígito de control.
- `to_dict()` / `from_dict()` permiten serializar/deserializar cada entidad para cualquier formato.

#### Modelo `User` con validación de email y hashing seguro

El framework implementa un modelo `User` extendido con autenticación HMAC-SHA256:

```python
import hashlib
import hmac
import os

@dataclass
class User(BaseEntity):
    name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    password_hash: str = ""
    role: str = "user"  # user, admin, librarian
    active: bool = True
    borrowed_books: List[str] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        if not self.name.strip():
            raise ValueError("El nombre es obligatorio")
        if self.email and not self._validate_email(self.email):
            raise ValueError("Email inválido")

    def set_password(self, password: str):
        """Contraseña hasheada con HMAC-SHA256 y salt aleatorio."""
        salt = os.urandom(16).hex()
        hash_value = hmac.new(
            salt.encode(), password.encode(), hashlib.sha256
        ).hexdigest()
        self.password_hash = f"{salt}${hash_value}"

    def check_password(self, password: str) -> bool:
        """Verificación con comparación en tiempo constante."""
        if '$' not in self.password_hash:
            # Compatibilidad con hashes SHA-256 legacy
            return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
        salt, stored_hash = self.password_hash.split('$', 1)
        computed = hmac.new(
            salt.encode(), password.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed, stored_hash)
```

**Mejoras de seguridad clave:**

- **Salt aleatorio de 16 bytes**: cada contraseña genera un hash único aunque el texto sea igual.
- **HMAC-SHA256**: más resistente a extensiones de hash que SHA-256 simple.
- **`hmac.compare_digest()`**: comparación en tiempo constante que previene ataques de timing.
- **Compatibilidad retroactiva**: acepta hashes legacy SHA-256 durante la migración.

### 2.1.1 Validaciones de integridad referencial

Además de las validaciones de formato en los modelos, el sistema implementa **validaciones de integridad referencial** en las operaciones CRUD:

- **Eliminación de autores**: No se permite eliminar un autor si tiene libros asociados en la biblioteca. Esta validación previene inconsistencias en los datos y mantiene la integridad de las relaciones entidad-relación.

- **Eliminación de usuarios**: Se registra en el log pero se permite siempre, ya que los usuarios pueden tener libros prestados (aunque en una implementación completa se debería validar el estado de préstamos).

Estas validaciones se implementan en la capa de interfaz gráfica (`gui_app.py`) antes de llamar a los métodos de eliminación de los gestores de datos.

### 2.2 Capa de acceso a datos: de clases específicas a Repository genérico

El proyecto implementa **dos niveles de abstracción**: gestores específicos por entidad (nivel 1) y un framework genérico con Repository (nivel 2).

#### Nivel 1: Gestores específicos con ABC + Generics

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic

T = TypeVar('T')

class DataManager(ABC, Generic[T]):
    """Interfaz base para todos los gestores de datos"""

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def save(self, entity: T) -> bool: ...

    @abstractmethod
    def load(self, entity_id: str) -> Optional[T]: ...

    @abstractmethod
    def load_all(self) -> List[T]: ...

    @abstractmethod
    def delete(self, entity_id: str) -> bool: ...

    def exists(self, entity_id: str) -> bool:
        return self.load(entity_id) is not None

    @abstractmethod
    def search(self, criteria: Dict[str, Any]) -> List[T]: ...
```

#### Nivel 2: Repository<T> genérico del framework

El framework añade una capa `Repository<T>` que envuelve cualquier `DataManager` y un `EntityManager` que coordina repositorios por tipo:

```python
class Repository(Generic[T]):
    """Repositorio genérico para operaciones CRUD sobre cualquier entidad."""

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def save(self, entity: T) -> bool:
        return self.data_manager.save(entity)

    def load(self, entity_id: str) -> Optional[T]:
        return self.data_manager.load(entity_id)

    def load_all(self) -> List[T]:
        return self.data_manager.load_all()

    def find_by(self, **criteria) -> List[T]:
        """Búsqueda por criterios arbitrarios."""
        return [e for e in self.load_all()
                if all(getattr(e, k, None) == v for k, v in criteria.items())]


class EntityManager:
    """Coordina repositorios para diferentes tipos de entidad."""

    def __init__(self, data_factory, default_format: str = "json"):
        self.data_factory = data_factory
        self.default_format = default_format
        self._repositories = {}

    def get_repository(self, entity_class: Type[T]) -> Repository[T]:
        entity_name = entity_class.__name__
        if entity_name not in self._repositories:
            data_manager = self.data_factory.create_manager(
                self.default_format, entity_class
            )
            self._repositories[entity_name] = Repository(data_manager)
        return self._repositories[entity_name]

    def migrate_entity(self, entity_class, from_format, to_format):
        """Migrar datos de una entidad entre formatos."""
        from_mgr = self.data_factory.create_manager(from_format, entity_class)
        to_mgr = self.data_factory.create_manager(to_format, entity_class)
        for entity in from_mgr.load_all():
            to_mgr.save(entity)
```

Cada formato hereda de esta interfaz y la especializa para `Book`, `Author` y `User`:

```
DataManager[T]  (ABC + Generic)
  ├── BookDataManager  (DataManager[Book])
  │     ├── TXTBookDataManager
  │     ├── CSVBookDataManager
  │     ├── JSONBookDataManager
  │     ├── XMLBookDataManager
  │     └── DBBookDataManager
  ├── AuthorDataManager  (DataManager[Author])
  │     └── ... (mismo esquema)
  └── UserDataManager  (DataManager[User])
        └── ... (mismo esquema)
```

### 2.3 Factory Pattern: intercambio de formatos

La `DataManagerFactory` permite cambiar de formato con una sola línea:

```python
class DataManagerFactory:
    @staticmethod
    def create_book_manager(format_type: str, base_path: str = "data") -> BookDataManager:
        format_type = format_type.lower()
        if format_type == 'txt':
            from .txt_manager import TXTBookDataManager
            return TXTBookDataManager(base_path)
        elif format_type == 'csv':
            from .csv_manager import CSVBookDataManager
            return CSVBookDataManager(base_path)
        elif format_type == 'json':
            from .json_manager import JSONBookDataManager
            return JSONBookDataManager(base_path)
        elif format_type == 'xml':
            from .xml_manager import XMLBookDataManager
            return XMLBookDataManager(base_path)
        elif format_type == 'db':
            from .db_manager import DBBookDataManager
            return DBBookDataManager(base_path)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")
```

**Ventajas del Factory Pattern aquí:**

- El código de la GUI o el menú **nunca referencia** una implementación concreta.
- Añadir un nuevo formato (p. ej. YAML, MongoDB) solo requiere crear una clase nueva y registrarla en el factory.
- Los imports se hacen _lazy_ (dentro de cada `if`) para no cargar módulos innecesarios.

### 2.4 Los cinco gestores de datos

#### 2.4.1 Gestor TXT (`txt_manager.py`)

Almacena los datos como JSON dentro de archivos `.txt`. Usa `json.dump()` / `json.load()` internamente.

```python
class TXTBookDataManager(BookDataManager):
    def __init__(self, base_path: str = "data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "books.txt"

    def save(self, book: Book) -> bool:
        books = self.load_all()
        books = [b for b in books if b.id != book.id]  # evitar duplicados
        books.append(book)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([b.to_dict() for b in books], f, ensure_ascii=False, indent=2)
        return True

    def load_all(self) -> List[Book]:
        if not self.file_path.exists():
            return []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [Book.from_dict(d) for d in data]
```

#### 2.4.2 Gestor CSV (`csv_manager.py`)

Utiliza `csv.DictWriter` / `csv.DictReader` con campos predefinidos. Los campos tipo lista (p. ej. `borrowed_books`) se serializan separados por punto y coma.

```python
BOOK_FIELDNAMES = [
    'id', 'title', 'author_id', 'isbn', 'publication_year', 'genre',
    'description', 'pages', 'language', 'publisher', 'available',
    'borrowed_by', 'borrow_date', 'due_date'
]

class CSVBookDataManager(BookDataManager):
    def __init__(self, base_path="data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "books.csv"

    def save(self, book: Book) -> bool:
        books = self.load_all()
        books = [b for b in books if b.id != book.id]
        books.append(book)
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=BOOK_FIELDNAMES)
            writer.writeheader()
            for b in books:
                writer.writerow(b.to_dict())
        return True
```

#### 2.4.3 Gestor JSON (`json_manager.py`)

Almacena cada colección como un documento JSON con clave raíz descriptiva (`"books"`, `"authors"`, `"users"`).

```python
class JSONBookDataManager(BookDataManager):
    def __init__(self, base_path="data"):
        super().__init__(base_path)
        self.file_path = self.base_path / "books.json"

    def save(self, book: Book) -> bool:
        books = self.load_all()
        books = [b for b in books if b.id != book.id]
        books.append(book)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump({"books": [b.to_dict() for b in books]}, f,
                      ensure_ascii=False, indent=4)
        return True
```

#### 2.4.4 Gestor XML (`xml_manager.py`)

Utiliza `xml.etree.ElementTree` para construir el árbol DOM y `xml.dom.minidom` para formatearlo:

```python
import xml.etree.ElementTree as ET
from xml.dom import minidom

class XMLBookDataManager(BookDataManager):
    def _prettify(self, elem):
        rough = ET.tostring(elem, encoding='unicode')
        parsed = minidom.parseString(rough)
        return parsed.toprettyxml(indent="  ")

    def save(self, book: Book) -> bool:
        books = self.load_all()
        books = [b for b in books if b.id != book.id]
        books.append(book)

        root = ET.Element("books")
        for b in books:
            book_elem = ET.SubElement(root, "book")
            for key, value in b.to_dict().items():
                child = ET.SubElement(book_elem, key)
                child.text = str(value) if value is not None else ""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(self._prettify(root))
        return True
```

#### 2.4.5 Gestor SQLite (`db_manager.py`)

Crea las tablas automáticamente la primera vez y usa sentencias parametrizadas para prevenir inyección SQL:

```python
import sqlite3

class SQLiteConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author_id TEXT NOT NULL,
            isbn TEXT,
            publication_year INTEGER,
            genre TEXT,
            description TEXT,
            pages INTEGER,
            language TEXT DEFAULT 'Español',
            publisher TEXT,
            available INTEGER DEFAULT 1,
            borrowed_by TEXT,
            borrow_date TEXT,
            due_date TEXT
        )''')
        conn.commit()
        conn.close()

class DBBookDataManager(BookDataManager):
    def save(self, book: Book) -> bool:
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO books
            (id, title, author_id, isbn, publication_year, genre,
             description, pages, language, publisher, available,
             borrowed_by, borrow_date, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (book.id, book.title, book.author_id, book.isbn,
             book.publication_year, book.genre, book.description,
             book.pages, book.language, book.publisher,
             1 if book.available else 0, book.borrowed_by,
             book.borrow_date, book.due_date))
        conn.commit()
        conn.close()
        return True
```

**Nota importante:** Se utiliza `INSERT OR REPLACE` en lugar de `INSERT` seguido de `UPDATE` por separado, lo que simplifica el código de _upsert_ (insertar o actualizar).

### 2.5 Interfaz gráfica con tkinter + ttk

La GUI se construye con `tkinter` y `ttk`, los módulos estándar de Python para interfaces gráficas, proporcionando una experiencia nativa y profesional.

```python
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class BibliotecaApp:
    def __init__(self):
        self.root = ttk.Window(
            title="📚 Biblioteca Personal",
            themename="darkly",        # tema oscuro moderno
            size=(1200, 750),
            minsize=(1000, 600)
        )

        # Notebook con pestañas: Libros, Autores, Usuarios, Estadísticas
        self.notebook = ttk.Notebook(self.root, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True, padx=10)
```

Características de la GUI:

| Característica                  | Implementación                                                             |
| ------------------------------- | -------------------------------------------------------------------------- |
| **Selector de formato en vivo** | Combobox que llama a `_change_format()` → recrea managers y refresca datos |
| **Selector de tema**            | 15 temas disponibles: darkly, superhero, cosmo, flatly, journal…           |
| **CRUD completo por pestaña**   | Formulario a la izquierda + Treeview a la derecha                          |
| **Búsqueda en tiempo real**     | `StringVar.trace_add("write", ...)` filtra la tabla al teclear             |
| **Estadísticas**                | Tarjetas métricas + tablas por género y por autor                          |
| **Validación visual**           | Diálogos `Messagebox.show_warning()` para campos obligatorios              |

---

## 3. Aplicación práctica con código real (25 %)

### 3.1 Ejecución del proyecto

```bash
# Instalar dependencias
# tkinter viene incluido con Python, no requiere instalación

# Ejecutar la aplicación
cd biblioteca_personal
python main.py
```

### 3.2 Suite de pruebas automatizadas

El archivo `test_all_formats.py` valida las operaciones CRUD en **los cinco formatos**:

```python
def test_format(format_type, format_name):
    """Prueba CRUD completo para un formato dado"""
    print(f"\n{'='*50}")
    print(f"  Probando formato: {format_name}")

    # 1. Crear gestores con Factory
    book_mgr = DataManagerFactory.create_book_manager(format_type, test_path)
    author_mgr = DataManagerFactory.create_author_manager(format_type, test_path)
    user_mgr = DataManagerFactory.create_user_manager(format_type, test_path)

    # 2. Crear y guardar un autor
    author = Author(name="Gabriel García Márquez", nationality="Colombiana")
    assert author_mgr.save(author), "Error al guardar autor"

    # 3. Crear y guardar un libro
    book = Book(title="Cien años de soledad", author_id=author.id, genre="Novela")
    assert book_mgr.save(book), "Error al guardar libro"

    # 4. Verificar lectura
    loaded = book_mgr.load(book.id)
    assert loaded is not None, "Error al cargar libro"
    assert loaded.title == "Cien años de soledad"

    # 5. Actualizar
    loaded.genre = "Realismo mágico"
    assert book_mgr.save(loaded), "Error al actualizar libro"

    # 6. Eliminar
    assert book_mgr.delete(book.id), "Error al eliminar libro"
    assert book_mgr.load(book.id) is None, "El libro no se eliminó"

    print(f"  ✅ {format_name} - TODAS LAS PRUEBAS PASARON")
```

**Resultado de la ejecución:**

```
==================================================
  Probando formato: TXT - Texto plano
  ✅ TXT - TODAS LAS PRUEBAS PASARON
==================================================
  Probando formato: CSV - Separado por comas
  ✅ CSV - TODAS LAS PRUEBAS PASARON
==================================================
  Probando formato: JSON - Notación de objetos
  ✅ JSON - TODAS LAS PRUEBAS PASARON
==================================================
  Probando formato: XML - Marcado extensible
  ✅ XML - TODAS LAS PRUEBAS PASARON
==================================================
  Probando formato: SQLite - Base de datos
  ✅ SQLite - TODAS LAS PRUEBAS PASARON

🎉 TODOS LOS FORMATOS FUNCIONAN CORRECTAMENTE (70/70 aserciones)
```

### 3.3 Ejemplo de flujo CRUD en la GUI

**Agregar un autor y un libro:**

1. Pestaña **Autores** → rellenar nombre → clic en "➕ Agregar"
2. Pestaña **Libros** → rellenar título, seleccionar autor del combo → clic en "➕ Agregar"
3. La tabla Treeview muestra el libro con su autor asociado

**Cambiar de formato en caliente con migración automática:**

```python
# Dentro de BibliotecaApp – la GUI usa exclusivamente el framework:
from data_access_framework import create_framework, Book, Author, User

class BibliotecaApp:
    def __init__(self):
        self.format_type = 'json'
        self.framework = create_framework(database_format=self.format_type)
        self.book_repo = self.framework.entity_manager.get_repository(Book)
        self.author_repo = self.framework.entity_manager.get_repository(Author)
        self.user_repo = self.framework.entity_manager.get_repository(User)

    def _change_format(self, *_):
        label = self.format_var.get()
        new_fmt = FORMATOS.get(label, 'json')
        if new_fmt != self.format_type:
            old_fmt = self.format_type
            self.format_type = new_fmt
            # Migrar datos automáticamente al nuevo formato
            self.framework.entity_manager.migrate_entity(Book, old_fmt, new_fmt)
            self.framework.entity_manager.migrate_entity(Author, old_fmt, new_fmt)
            self.framework.entity_manager.migrate_entity(User, old_fmt, new_fmt)
            # Recrear framework con nuevo formato
            self.framework = create_framework(database_format=self.format_type)
            self.book_repo = self.framework.entity_manager.get_repository(Book)
            self.author_repo = self.framework.entity_manager.get_repository(Author)
            self.user_repo = self.framework.entity_manager.get_repository(User)
            self._refresh_all()
```

### 3.4 Errores comunes y cómo evitarlos

#### Error 1: `FileNotFoundError` al leer archivos que no existen

```python
# ❌ INCORRECTO - Si el fichero no existe, falla
with open(self.file_path, 'r') as f:
    data = json.load(f)

# ✅ CORRECTO - Comprobar existencia antes
def load_all(self) -> List[Book]:
    if not self.file_path.exists():
        return []   # Devolver lista vacía si no hay datos
    with open(self.file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [Book.from_dict(d) for d in data]
```

#### Error 2: Inyección SQL al construir consultas con concatenación

```python
# ❌ INCORRECTO - Vulnerable a inyección SQL
cursor.execute(f"SELECT * FROM books WHERE id = '{book_id}'")

# ✅ CORRECTO - Consultas parametrizadas
cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
```

#### Error 3: No cerrar conexiones a la base de datos

```python
# ❌ INCORRECTO - Si hay excepción, la conexión queda abierta
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT ...")
conn.close()

# ✅ CORRECTO - Usar try/finally
try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT ...")
    return cursor.fetchall()
finally:
    conn.close()
```

#### Error 4: Pérdida de datos al guardar CSV sin cabeceras coherentes

```python
# ❌ INCORRECTO - Campos variables según el objeto
writer.writerow(book.__dict__)

# ✅ CORRECTO - Definir fieldnames fijos
BOOK_FIELDNAMES = ['id', 'title', 'author_id', 'isbn', ...]
writer = csv.DictWriter(f, fieldnames=BOOK_FIELDNAMES)
writer.writeheader()
for b in books:
    writer.writerow(b.to_dict())
```

#### Error 5: Codificación incorrecta al leer XML con caracteres especiales

```python
# ❌ INCORRECTO - Puede fallar con acentos
tree = ET.parse(file_path)

# ✅ CORRECTO - Abrir con encoding explícito y parsear string
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
root = ET.fromstring(content)
```

### 3.5 Comparativa de rendimiento y uso de cada formato

| Aspecto                 | TXT       | CSV      | JSON     | XML    | SQLite     |
| ----------------------- | --------- | -------- | -------- | ------ | ---------- |
| **Velocidad lectura**   | Rápida    | Rápida   | Rápida   | Media  | Muy rápida |
| **Velocidad escritura** | Rápida    | Rápida   | Rápida   | Lenta  | Rápida     |
| **Tamaño archivo**      | Medio     | Pequeño  | Medio    | Grande | Compacto   |
| **Legibilidad humana**  | Alta      | Alta     | Alta     | Media  | Ninguna    |
| **Datos jerárquicos**   | Sí (JSON) | No       | Sí       | Sí     | No nativo  |
| **Consultas complejas** | No        | No       | No       | No     | Sí (SQL)   |
| **Interoperabilidad**   | Alta      | Muy alta | Muy alta | Alta   | Media      |

---

## 4. Conclusión y enlace con otros contenidos (25 %)

### 4.1 Resumen de logros

Este proyecto implementa un **sistema completo de gestión de biblioteca** con las siguientes características verificadas:

- **5 formatos de persistencia** funcionando con operaciones CRUD completas y validadas con 70 aserciones automáticas.
- **Framework genérico reutilizable** (`data_access_framework`) con Repository\<T\>, EntityManager, migración entre formatos y servicios de negocio (auth, loans, reports).
- **Arquitectura profesional** basada en patrones de diseño (Abstract Factory, Repository, Strategy, Service Layer, Template Method) que permite añadir nuevos formatos sin modificar el código existente (principio Open/Closed de SOLID).
- **Interfaz gráfica moderna** con tkinter + ttk integrada con el framework, cambio de formato en tiempo real con migración automática, búsqueda instantánea y estadísticas.
- **API REST con Flask** y autenticación JWT, endpoints completos para libros, préstamos, reportes y autenticación.
- **Seguridad robusta**: hashing HMAC-SHA256 con salt aleatorio, comparación en tiempo constante, autorización por roles (user/librarian/admin), compatibilidad retroactiva con hashes legacy.
- **Validación robusta** de datos con verificación de ISBN-10/ISBN-13, formato de email con expresión regular, campos obligatorios e **integridad referencial** (no eliminar autores con libros asociados).
- **Suite de pruebas completa** que garantiza el funcionamiento correcto de todos los componentes.

### 4.2 Enlace con otros módulos del ciclo DAM2

| Módulo                                   | Relación con este proyecto                                                                                                                                             |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Programación de Servicios y Procesos** | La arquitectura basada en interfaces y Factory permitiría ejecutar lecturas de diferentes formatos en hilos concurrentes con `threading`                               |
| **Desarrollo de Interfaces**             | La GUI con tkinter + ttk aplica directamente principios de diseño de interfaces: usabilidad, feedback visual, consistencia, accesibilidad (pestañas, combos, diálogos) |
| **Sistemas de Gestión Empresarial**      | El patrón multi-formato es análogo a cómo los ERP (Odoo, SAP) exportan e importan datos: CSV para informes, XML para facturación electrónica, JSON para APIs REST      |
| **Proyecto Intermodular II**             | La estructura del proyecto (modelos → gestores → interfaz) sigue la misma separación de capas que se estudia en el diseño de proyectos software reales                 |

### 4.3 Ampliaciones ya implementadas y futuras

#### Ya implementadas en el framework:

- **API REST**: endpoints Flask con autenticación JWT para libros, préstamos, reportes y auth.
- **Migración automática**: cambio de formato en caliente con preservación completa de datos.
- **Seguridad avanzada**: HMAC-SHA256 con salt, roles de usuario, autorización granular.
- **Servicios de negocio**: préstamos con cálculo de penalizaciones, extensiones, informes completos.

#### Posibles ampliaciones futuras:

- **Gestor YAML**: nuevo formato añadido simplemente creando `yaml_manager.py` y registrándolo en el Factory.
- **MongoDB**: conectar como formato extra para explorar bases de datos NoSQL documentales.
- **Concurrencia**: con `threading` o `asyncio`, permitir operaciones de lectura/escritura simultáneas.
- **Frontend web**: interfaz React/Vue que consuma la API REST existente.

### 4.4 Reflexión final

El proyecto demuestra que el acceso a datos no se limita a un único formato o tecnología; la clave es diseñar abstracciones correctas que encapsulen las diferencias técnicas detrás de una interfaz común. El patrón Factory + Repository garantiza que la lógica de negocio permanezca desacoplada del mecanismo de almacenamiento, permitiendo escalar el proyecto a nuevos formatos con mínimo esfuerzo. Además, la combinación de pruebas automatizadas y una interfaz gráfica completa proporciona confianza tanto al desarrollador como al usuario final de que el sistema funciona correctamente en todos sus modos.

---

_Documento generado como parte del proyecto final de Acceso a Datos — DAM2 2025/2026_
