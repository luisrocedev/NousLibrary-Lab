# Sistema de Gestión de Biblioteca Personal

## Descripción

Este proyecto es una aplicación completa de gestión de biblioteca personal que demuestra el manejo de múltiples formatos de archivo en Python. El sistema permite gestionar libros, autores y usuarios, además de manejar préstamos de libros.

## Estado del Proyecto

### ✅ IMPLEMENTADO

- **Arquitectura base**: Modelos de datos, gestores abstractos, factory pattern
- **Múltiples formatos**: TXT, CSV, JSON, XML y SQLite completamente implementados
- **Modelos de datos**: Book, Author, User con validación completa (ISBN, email, campos obligatorios)
- **Interfaz de usuario**: Menú de consola funcional y **interfaz gráfica completa con tkinter**
- **Sistema de logging**: Seguimiento completo de operaciones
- **Pruebas completas**: Validación de todas las operaciones CRUD
- **Gestión completa**: Libros, autores, usuarios con operaciones CRUD
- **Validación de integridad**: No se pueden eliminar autores con libros asociados
- **Manejo de errores**: Captura completa de excepciones con mensajes informativos

### 🚧 EN DESARROLLO

- **Sistema de préstamos**: Funcionalidad básica implementada, mejoras pendientes
- **Reportes avanzados**: Estadísticas y exportación de datos

### 📋 PENDIENTE

- Funcionalidades adicionales de préstamos
- Reportes más detallados
- Exportación a múltiples formatos

- **Múltiples formatos de almacenamiento**: TXT, CSV, JSON, XML y SQLite
- **Gestión completa de libros**: agregar, buscar, actualizar y eliminar
- **Gestión de autores**: información completa de autores
- **Gestión de usuarios**: registro y seguimiento de usuarios
- **Sistema de préstamos**: prestar y devolver libros
- **Reportes y estadísticas**: análisis de datos de la biblioteca
- **Interfaz de consola**: menú interactivo fácil de usar
- **Logging completo**: seguimiento de todas las operaciones

## Formatos de Archivo Soportados

### 1. Archivos de Texto (.txt)

- Almacenamiento simple y legible
- Estructura básica con separadores
- Fácil de editar manualmente

### 2. Archivos CSV (.csv)

- Formato tabular estándar
- Compatible con Excel y otras herramientas
- Eficiente para datos estructurados

### 3. Archivos JSON (.json)

- Formato moderno y flexible
- Soporte para estructuras anidadas
- Ampliamente usado en APIs web

### 4. Archivos XML (.xml)

- Formato estructurado jerárquico
- Ideal para datos complejos
- Compatible con estándares empresariales

### 5. Base de Datos SQLite (.db)

- Base de datos relacional embebida
- Consultas SQL completas
- Integridad de datos y transacciones

## Requisitos del Sistema

- Python 3.8 o superior
- Librerías especificadas en `requirements.txt`

## Instalación

1. Clona o descarga el proyecto
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Ejecución Básica

```bash
python main.py  # Interfaz de consola
python gui_app.py  # Interfaz gráfica
```

### Selección de Formato

Al iniciar la aplicación, se te pedirá seleccionar el formato de almacenamiento:

1. **TXT**: Archivos de texto plano
2. **CSV**: Archivos separados por comas
3. **JSON**: Notación de objetos JavaScript
4. **XML**: Lenguaje de marcado extensible
5. **DB**: Base de datos SQLite

### Funcionalidades Disponibles

#### Gestión de Libros

- ✅ Agregar nuevos libros con toda su información
- ✅ Buscar libros por ID, título, autor o género
- ✅ Listar todos los libros con filtros
- ✅ Actualizar información de libros existentes
- ✅ Eliminar libros (con validación)

#### Gestión de Autores

- ✅ Agregar información de autores
- ✅ Buscar autores por ID o nombre
- ✅ Listar todos los autores
- ✅ Actualizar datos de autores
- ✅ Eliminar autores (solo si no tienen libros asociados)

#### Gestión de Usuarios

- ✅ Registrar nuevos usuarios
- ✅ Buscar usuarios por ID o nombre
- ✅ Listar todos los usuarios
- ✅ Actualizar información de usuarios
- ✅ Eliminar usuarios

#### Gestión de Préstamos

- 🚧 Prestar libros a usuarios (básico)
- 🚧 Registrar devoluciones (básico)
- 🚧 Ver préstamos activos
- 🚧 Consultar libros prestados por usuario

#### Reportes y Estadísticas

- 🚧 Estadísticas generales de la biblioteca
- 🚧 Libros por género
- 🚧 Libros por autor
- 🚧 Usuarios más activos
- 🚧 Exportación de datos

## Estructura del Proyecto

```
biblioteca_personal/
├── main.py                 # Punto de entrada de la aplicación (consola)
├── gui_app.py              # Interfaz gráfica completa con tkinter
├── models/                 # Modelos de datos
│   └── __init__.py        # Clases Book, Author, User con validación
├── data_managers/         # Gestores de datos por formato
│   ├── __init__.py       # Clases base, factory y todos los gestores
│   ├── txt_manager.py    # Gestor para archivos TXT
│   ├── csv_manager.py    # Gestor para archivos CSV
│   ├── json_manager.py   # Gestor para archivos JSON
│   ├── xml_manager.py    # Gestor para archivos XML
│   └── db_manager.py     # Gestor para base de datos SQLite
├── ui/                    # Interfaz de usuario de consola
│   └── menu_principal.py # Menú principal de consola
├── utils/                 # Utilidades
│   └── logger.py         # Sistema de logging completo
├── data/                  # Directorio de datos (creado automáticamente)
├── logs/                  # Directorio de logs (creado automáticamente)
├── create_test_data.py    # Script para crear datos de prueba
├── test_*.py             # Scripts de prueba para CRUD y formatos
├── requirements.txt       # Dependencias del proyecto
└── README.md             # Este archivo
```

## Arquitectura

El proyecto sigue los principios de arquitectura limpia con:

- **Separación de responsabilidades**: Cada módulo tiene una función específica
- **Abstracción de datos**: Interfaz común para todos los formatos
- **Factory Pattern**: Creación de gestores según el formato seleccionado
- **Repository Pattern**: Abstracción del acceso a datos
- **Logging centralizado**: Seguimiento completo de operaciones

## Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje principal
- **SQLAlchemy**: ORM para bases de datos relacionales
- **SQLite**: Base de datos embebida
- **JSON/XML**: Formatos de serialización nativos
- **CSV**: Formato tabular
- **Logging**: Sistema de logs integrado

## Validación y Pruebas

El proyecto incluye validación de datos en los modelos:

- **ISBN**: Validación de códigos ISBN-10 e ISBN-13
- **Email**: Validación básica de formato de email
- **Campos obligatorios**: Validación de campos requeridos
- **Tipos de datos**: Conversión y validación de tipos

## Manejo de Errores

- Captura de excepciones en todas las operaciones
- Logging detallado de errores
- Mensajes informativos para el usuario
- Recuperación de errores donde es posible

## Extensibilidad

El diseño permite agregar fácilmente:

- Nuevos formatos de archivo
- Nuevas funcionalidades
- Nuevos tipos de entidades
- Integraciones con APIs externas

## Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa tus cambios
4. Agrega tests si es necesario
5. Envía un pull request

## Licencia

Este proyecto es para fines educativos y de demostración.

## Autor

Proyecto desarrollado como parte del curso de Acceso a Datos - DAM2
