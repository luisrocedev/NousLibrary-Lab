# 📚 NousLibrary-Lab

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-Data%20Access-purple)
![Storage](https://img.shields.io/badge/Formatos-TXT%20|%20CSV%20|%20JSON%20|%20XML%20|%20SQLite-green)
![Flask](https://img.shields.io/badge/API-Flask%20REST-red?logo=flask)
![License](https://img.shields.io/badge/Licencia-Educativo-informational)

**Framework de acceso a datos multiformato con GUI integrada y API REST**

*Sistema completo de gestión de biblioteca personal que demuestra patrones de diseño avanzados: Abstract Factory, Repository, Strategy y Service Layer.*

</div>

---

## 🎯 Descripción

**NousLibrary-Lab** es un framework genérico de acceso a datos que implementa un sistema de gestión de biblioteca personal como caso de uso principal. Soporta **5 formatos de almacenamiento** intercambiables en caliente, con migración automática de datos entre formatos.

### Características principales

| Funcionalidad | Descripción |
|---|---|
| 📁 **5 Formatos** | TXT (JSON-lines), CSV, JSON, XML y SQLite |
| 🔄 **Migración** | Cambio de formato en caliente con migración automática |
| 🖥️ **GUI completa** | Interfaz tkinter con pestañas para Libros, Autores, Usuarios y Estadísticas |
| 🌐 **API REST** | Endpoints Flask con autenticación JWT |
| 🔐 **Seguridad** | Hashing HMAC-SHA256 con salt, autorización por roles |
| 📊 **Estadísticas** | Dashboard en tiempo real con métricas y gráficos |
| 📖 **Préstamos** | Sistema completo con penalizaciones y extensiones |
| 🔍 **Búsqueda** | Filtrado en tiempo real por múltiples campos |

---

## 🏗️ Arquitectura

```
NousLibrary-Lab/
├── biblioteca_personal/
│   ├── main.py                    # Punto de entrada CLI
│   ├── gui_app.py                 # Interfaz gráfica (tkinter)
│   │
│   ├── models/                    # Modelos originales (Book, Author, User)
│   │   └── __init__.py
│   │
│   ├── data_managers/             # Gestores específicos por entidad
│   │   ├── __init__.py            # ABC DataManager + Factory
│   │   ├── json_manager.py
│   │   ├── xml_manager.py
│   │   ├── csv_manager.py
│   │   ├── txt_manager.py
│   │   └── db_manager.py
│   │
│   ├── data_access_framework/     # Framework genérico reutilizable
│   │   ├── __init__.py            # create_framework()
│   │   │
│   │   ├── core/
│   │   │   ├── data_access_framework.py   # Orquestador principal
│   │   │   ├── entity_manager.py          # Repository<T> + EntityManager
│   │   │   ├── config_manager.py          # Configuración con deep merge
│   │   │   └── migration_manager.py       # Migración entre formatos
│   │   │
│   │   ├── models/
│   │   │   └── __init__.py        # BaseEntity + 5 modelos con validación
│   │   │
│   │   ├── data_managers/         # Gestores genéricos (1 por formato)
│   │   │   ├── json_manager.py
│   │   │   ├── xml_manager.py
│   │   │   ├── csv_manager.py
│   │   │   ├── txt_manager.py
│   │   │   └── db_manager.py
│   │   │
│   │   ├── business/              # Servicios de negocio
│   │   │   ├── auth_service.py    # Autenticación HMAC-SHA256 + JWT
│   │   │   ├── loan_service.py    # Préstamos con penalizaciones
│   │   │   └── report_service.py  # Informes y estadísticas
│   │   │
│   │   └── api/                   # API REST Flask
│   │       ├── app.py             # Factory de la app Flask
│   │       └── routes/
│   │           ├── auth.py
│   │           ├── books.py
│   │           ├── loans.py
│   │           └── reports.py
│   │
│   ├── ui/                        # Menú CLI legacy
│   │   └── menu_principal.py
│   │
│   └── utils/
│       └── logger.py              # Logger + ProgressLogger
│
├── Actividad_BibliotecaPersonal_53945291X.md
└── README.md
```

---

## 🚀 Inicio Rápido

### Requisitos

- **Python 3.10+**
- Dependencias: `pip install -r biblioteca_personal/requirements.txt`

### Ejecutar la GUI

```bash
cd biblioteca_personal
python main.py
```

### Usar el framework en código

```python
from biblioteca_personal.data_access_framework import create_framework, Book, Author

# Crear framework con formato JSON (también: csv, txt, xml, sqlite)
fw = create_framework(database_format="json")

# Obtener repositorios
book_repo = fw.entity_manager.get_repository(Book)
author_repo = fw.entity_manager.get_repository(Author)

# Crear un autor
author = Author(name="Gabriel García Márquez", nationality="Colombiana")
author_repo.save(author)

# Crear un libro
book = Book(
    title="Cien años de soledad",
    author_id=author.id,
    genre="Novela",
    publication_year=1967,
    pages=471
)
book_repo.save(book)

# Buscar libros
all_books = book_repo.load_all()
novels = book_repo.find_by(genre="Novela")
```

### Migrar entre formatos

```python
# Migrar de JSON a SQLite
fw.entity_manager.migrate_entity(Book, "json", "sqlite")
fw.entity_manager.migrate_entity(Author, "json", "sqlite")
```

### Iniciar la API REST

```python
fw = create_framework(database_format="sqlite")
fw.start_api(host="0.0.0.0", port=5000)
```

---

## 🔐 Seguridad

| Componente | Implementación |
|---|---|
| **Hashing** | HMAC-SHA256 con salt aleatorio de 16 bytes |
| **Autenticación API** | JWT con expiración configurable |
| **Autorización** | Roles: `user`, `librarian`, `admin` |
| **Compatibilidad** | Migración transparente desde SHA-256 legacy |

```python
# Registro seguro de usuarios
auth = fw.auth_service
user = auth.register_user(
    name="Ana", last_name="López",
    email="ana@email.com", password="secret123"
)

# Autenticación
authenticated = auth.authenticate("ana@email.com", "secret123")
```

---

## 📊 Formatos de Almacenamiento

### TXT (JSON-lines)
```
{"id": "uuid", "title": "Cien años de soledad", "genre": "Novela", ...}
{"id": "uuid", "title": "El Quijote", "genre": "Novela", ...}
```

### CSV
```csv
id,title,author_id,genre,publication_year,pages,available
uuid,Cien años de soledad,author-uuid,Novela,1967,471,True
```

### JSON
```json
[
  {"id": "uuid", "title": "Cien años de soledad", "author_id": "author-uuid"}
]
```

### XML
```xml
<books>
  <book id="uuid">
    <title>Cien años de soledad</title>
    <genre>Novela</genre>
  </book>
</books>
```

### SQLite
Base de datos relacional con tablas auto-generadas por entidad.

---

## 🧪 Tests

```bash
cd biblioteca_personal
python -m pytest test_basic.py test_crud.py test_all_formats.py test_delete.py -v
```

---

## 📐 Patrones de Diseño

| Patrón | Uso |
|---|---|
| **Abstract Factory** | `DataManagerFactory` crea gestores según formato |
| **Repository** | `Repository<T>` abstrae CRUD sobre cualquier entidad |
| **Strategy** | Formatos de almacenamiento intercambiables |
| **Service Layer** | `LoanService`, `AuthService`, `ReportService` |
| **Template Method** | `BaseEntity.from_dict()` / `to_dict()` en herencia |

---

## 👨‍💻 Autor

**DAM2526** — Desarrollo de Aplicaciones Multiplataforma  
DNI: 53945291X

---

<div align="center">
<sub>Parte del ecosistema <strong>Nous Suite</strong> — Herramientas educativas de software avanzado</sub>
</div>
