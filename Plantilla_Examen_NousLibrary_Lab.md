# NousLibrary-Lab — Plantilla de Examen

**Alumno:** Luis Rodríguez Cedeño · **DNI:** 53945291X  
**Módulo:** Acceso a Datos · **Curso:** DAM2 2025/26

---

## 1. Introducción

- **Qué es:** Sistema de gestión de biblioteca personal con GUI Tkinter + CLI + API REST + 5 formatos de datos
- **Contexto:** Módulo de Acceso a Datos — GUI desktop con persistencia multi-formato, migración en caliente
- **Objetivos principales:**
  - Interfaz gráfica profesional con tkinter/ttk (pestañas Notebook, Treeview, formularios)
  - CRUD completo de Libros, Autores y Usuarios
  - Migración en caliente entre formatos (selector en UI)
  - CLI interactivo como alternativa a la GUI
  - Reutilización del `data_access_framework` de NousData-Lab
- **Tecnologías clave:**
  - Python 3.11, tkinter/ttk (GUI desktop), dataclasses
  - ABC + Generic[T] (gestores abstractos), Factory pattern
  - JSON, CSV, XML, TXT, SQLite — 5 formatos intercambiables
- **Arquitectura:** `gui_app.py` (950 líneas, ventana principal) → `main.py` (CLI menú) → `data_managers/` (ABC DataManager[T] + Factory + 5 implementaciones) → `data_access_framework/` (Flask API + servicios) → `models/` (Book, Author, User)

---

## 2. Desarrollo de las partes

### 2.1 ABC DataManager con Generics

- `DataManager(ABC, Generic[T])` → interfaz tipada con TypeVar
- Gestores específicos: `BookDataManager(DataManager[Book])`, `AuthorDataManager(DataManager[Author])`
- `DataManagerFactory` con métodos estáticos por entidad

```python
T = TypeVar('T')

class DataManager(ABC, Generic[T]):
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def save(self, entity: T) -> bool: pass
    @abstractmethod
    def load(self, entity_id: str) -> Optional[T]: pass
    @abstractmethod
    def load_all(self) -> List[T]: pass
    @abstractmethod
    def delete(self, entity_id: str) -> bool: pass
    @abstractmethod
    def search(self, criteria: Dict[str, Any]) -> List[T]: pass

class BookDataManager(DataManager[Book]): pass
class AuthorDataManager(DataManager[Author]): pass
class UserDataManager(DataManager[User]): pass
```

> **Explicación:** Se usa `Generic[T]` con `TypeVar` para tipar el gestor según la entidad. ABC obliga a implementar los 5 métodos abstractos. Cada entidad tiene su clase base tipada.

### 2.2 DataManagerFactory — Creación por formato

- Un método estático por entidad: `create_book_manager()`, `create_author_manager()`, `create_user_manager()`
- Importación lazy: solo importa el gestor del formato solicitado

```python
class DataManagerFactory:
    @staticmethod
    def create_book_manager(format_type: str, base_path="data") -> BookDataManager:
        format_type = format_type.lower()
        if format_type == 'json':
            from .json_manager import JSONBookDataManager
            return JSONBookDataManager(base_path)
        elif format_type == 'csv':
            from .csv_manager import CSVBookDataManager
            return CSVBookDataManager(base_path)
        elif format_type == 'xml':
            from .xml_manager import XMLBookDataManager
            return XMLBookDataManager(base_path)
        elif format_type == 'txt':
            from .txt_manager import TXTBookDataManager
            return TXTBookDataManager(base_path)
        elif format_type == 'db':
            from .db_manager import DBBookDataManager
            return DBBookDataManager(base_path)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")
```

> **Explicación:** Factory con importación lazy — solo carga el módulo del formato necesario. Soporta 5 formatos. Patrón repetido para cada entidad (Author, User).

### 2.3 GUI Tkinter — Ventana principal con Notebook

- `BibliotecaApp`: clase principal con Tk root, Notebook (4 pestañas), Treeview para tablas
- Variables de estado: `selected_book_id`, `format_var`, repositorios
- Barra superior con selector de formato (Combobox) para migración en caliente

```python
class BibliotecaApp:
    def __init__(self):
        self.format_type = 'json'
        self.framework = create_framework(database_format=self.format_type)
        self.book_repo = self.framework.entity_manager.get_repository(Book)

        self.root = tk.Tk()
        self.root.title("📚 Biblioteca Personal")
        self.root.geometry("1200x750")

        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        # Notebook con pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_books = ttk.Frame(self.notebook)
        self.tab_authors = ttk.Frame(self.notebook)
        self.tab_users = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_books, text="  📖 Libros  ")
        self.notebook.add(self.tab_authors, text="  ✍️ Autores  ")
        self.notebook.add(self.tab_users, text="  👤 Usuarios  ")
        self.notebook.add(self.tab_stats, text="  📊 Estadísticas  ")
```

> **Explicación:** `ttk.Notebook` crea pestañas. Cada pestaña es un `ttk.Frame`. El framework se inicializa con formato por defecto (JSON). La UI se construye en `_build_ui()`.

### 2.4 Migración de formato en caliente

- Combobox con 5 formatos: TXT, CSV, JSON, XML, SQLite
- Al cambiar formato: migrar entidades (Book, Author, User) → recrear framework → refrescar UI
- Rollback si falla la migración

```python
FORMATOS = {
    'TXT - Texto plano': 'txt',
    'CSV - Separado por comas': 'csv',
    'JSON - Notación de objetos': 'json',
    'XML - Marcado extensible': 'xml',
    'SQLite - Base de datos': 'db'
}

def _change_format(self, *_):
    new_fmt = FORMATOS.get(self.format_var.get(), 'json')
    if new_fmt != self.format_type:
        old_fmt = self.format_type
        try:
            self.framework.entity_manager.migrate_entity(Book, old_fmt, new_fmt)
            self.framework.entity_manager.migrate_entity(Author, old_fmt, new_fmt)
            self.framework.entity_manager.migrate_entity(User, old_fmt, new_fmt)
            # Recrear framework con nuevo formato
            self.framework = create_framework(database_format=new_fmt)
            self.format_type = new_fmt
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.format_type = old_fmt  # Rollback
```

> **Explicación:** Cuando el usuario cambia el Combobox, se migran todas las entidades del formato antiguo al nuevo. Si falla, se revierte al formato anterior. Luego se recrea el framework.

### 2.5 Treeview para tablas con Scrollbar

- `ttk.Treeview` → columnas definidas, headers clicables, selección
- Doble clic → cargar datos en formulario para edición
- Botones CRUD debajo de la tabla

```python
# Dentro de _build_books_tab()
cols = ('title', 'isbn', 'genre', 'year', 'pages', 'available')
self.books_tree = ttk.Treeview(frame, columns=cols, show='headings', height=12)

for col in cols:
    self.books_tree.heading(col, text=col.capitalize())
    self.books_tree.column(col, width=120)

scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.books_tree.yview)
self.books_tree.configure(yscrollcommand=scroll.set)

self.books_tree.bind('<<TreeviewSelect>>', self._on_book_select)
```

> **Explicación:** `Treeview` es el widget tabla de ttk. `show='headings'` oculta la columna de iconos. El Scrollbar vertical se enlaza con `yview`. La selección se captura con el evento `<<TreeviewSelect>>`.

---

## 3. Presentación del proyecto

- **Flujo:** Abrir GUI → Seleccionar formato → CRUD en pestañas → Cambiar formato (migración) → Ver estadísticas
- **Puntos fuertes:** Migración en caliente entre 5 formatos, GUI profesional con Treeview, reutilización del framework
- **Demo:** `python gui_app.py` → pestaña Libros → añadir libro → cambiar a SQLite → verificar datos migrados
- **CLI alternativo:** `python main.py` → menú interactivo por consola

---

## 4. Conclusión

- **Competencias:** GUI tkinter/ttk, ABC + Generic[T], Factory, migración de datos, Framework reutilizable
- **Patrones clave:** Factory (gestores), Strategy (formatos intercambiables), Observer (eventos Tkinter)
- **Diferencia con NousData-Lab:** NousLibrary añade GUI Tkinter + CLI + migración en caliente visual
- **Extensibilidad:** Nuevo formato = nuevo manager + entrada en Factory
- **Valoración:** Demuestra persistencia multi-formato con interfaz desktop profesional
