"""
Books API Routes - Endpoints para gestión de libros

Proporciona operaciones CRUD para libros vía API REST.

Autor: DAM2526
"""

from flask import Blueprint, request, jsonify
from ..app import token_required

bp = Blueprint('books', __name__, url_prefix='/api/books')


@bp.route('', methods=['GET'])
def get_books():
    """Obtener lista de libros con filtros opcionales."""
    try:
        # Obtener parámetros de filtro
        genre = request.args.get('genre')
        author = request.args.get('author')
        available = request.args.get('available')
        search = request.args.get('search')

        # Convertir available a boolean
        if available is not None:
            available = available.lower() in ('true', '1', 'yes')

        # Obtener repositorio
        book_repo = request.current_app.framework.get_repository('Book')
        books = book_repo.load_all()

        # Aplicar filtros
        filtered_books = []
        for book in books:
            # Filtro por género
            if genre and book.genre != genre:
                continue

            # Filtro por autor (búsqueda en author_id por ahora)
            if author and author not in book.author_id:
                continue

            # Filtro por disponibilidad
            if available is not None and book.available != available:
                continue

            # Búsqueda por texto
            if search:
                search_lower = search.lower()
                if (search_lower not in book.title.lower() and
                    search_lower not in (book.genre or '').lower()):
                    continue

            filtered_books.append(book)

        # Convertir a dict para JSON
        result = []
        for book in filtered_books:
            book_dict = {
                "id": book.id,
                "title": book.title,
                "author_id": book.author_id,
                "isbn": book.isbn,
                "genre": book.genre,
                "language": book.language,
                "year": book.year,
                "pages": book.pages,
                "available": book.available,
                "created_at": book.created_at.isoformat() if book.created_at else None
            }
            result.append(book_dict)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/<book_id>', methods=['GET'])
def get_book(book_id):
    """Obtener un libro específico."""
    try:
        book_repo = request.current_app.framework.get_repository('Book')
        book = book_repo.load(book_id)

        if not book:
            return jsonify({"error": "Libro no encontrado"}), 404

        book_dict = {
            "id": book.id,
            "title": book.title,
            "author_id": book.author_id,
            "isbn": book.isbn,
            "genre": book.genre,
            "language": book.language,
            "year": book.year,
            "pages": book.pages,
            "available": book.available,
            "created_at": book.created_at.isoformat() if book.created_at else None,
            "updated_at": book.updated_at.isoformat() if book.updated_at else None
        }

        return jsonify(book_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('', methods=['POST'])
@token_required
def create_book():
    """Crear un nuevo libro."""
    try:
        # Verificar permisos
        if not request.current_app.framework.get_service('auth').authorize(
            request.current_user, 'write'
        ):
            return jsonify({"error": "Permisos insuficientes"}), 403

        data = request.get_json()

        # Validar datos requeridos
        required_fields = ['title', 'author_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400

        # Crear libro
        from ..models import Book
        book = Book(
            title=data['title'],
            author_id=data['author_id'],
            isbn=data.get('isbn'),
            genre=data.get('genre'),
            language=data.get('language', 'Español'),
            year=data.get('year', 2024),
            pages=data.get('pages', 0),
            available=data.get('available', True)
        )

        # Guardar
        book_repo = request.current_app.framework.get_repository('Book')
        success = book_repo.save(book)

        if not success:
            return jsonify({"error": "Error al guardar el libro"}), 500

        return jsonify({
            "message": "Libro creado exitosamente",
            "book_id": book.id
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/<book_id>', methods=['PUT'])
@token_required
def update_book(book_id):
    """Actualizar un libro existente."""
    try:
        # Verificar permisos
        if not request.current_app.framework.get_service('auth').authorize(
            request.current_user, 'write'
        ):
            return jsonify({"error": "Permisos insuficientes"}), 403

        book_repo = request.current_app.framework.get_repository('Book')
        book = book_repo.load(book_id)

        if not book:
            return jsonify({"error": "Libro no encontrado"}), 404

        data = request.get_json()

        # Actualizar campos permitidos
        allowed_fields = ['title', 'author_id', 'isbn', 'genre', 'language', 'year', 'pages', 'available']
        for field in allowed_fields:
            if field in data:
                setattr(book, field, data[field])

        # Guardar cambios
        success = book_repo.save(book)

        if not success:
            return jsonify({"error": "Error al actualizar el libro"}), 500

        return jsonify({"message": "Libro actualizado exitosamente"})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/<book_id>', methods=['DELETE'])
@token_required
def delete_book(book_id):
    """Eliminar un libro."""
    try:
        # Verificar permisos
        if not request.current_app.framework.get_service('auth').authorize(
            request.current_user, 'delete'
        ):
            return jsonify({"error": "Permisos insuficientes"}), 403

        book_repo = request.current_app.framework.get_repository('Book')
        book = book_repo.load(book_id)

        if not book:
            return jsonify({"error": "Libro no encontrado"}), 404

        # Verificar que no esté prestado
        if not book.available:
            return jsonify({"error": "No se puede eliminar un libro prestado"}), 400

        # Eliminar
        success = book_repo.delete(book_id)

        if not success:
            return jsonify({"error": "Error al eliminar el libro"}), 500

        return jsonify({"message": "Libro eliminado exitosamente"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/genres', methods=['GET'])
def get_genres():
    """Obtener lista de géneros disponibles."""
    try:
        book_repo = request.current_app.framework.get_repository('Book')
        books = book_repo.load_all()

        genres = list(set(book.genre for book in books if book.genre))
        genres.sort()

        return jsonify(genres)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/search', methods=['GET'])
def search_books():
    """Búsqueda avanzada de libros."""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))

        if not query:
            return jsonify({"error": "Parámetro 'q' requerido"}), 400

        book_repo = request.current_app.framework.get_repository('Book')
        books = book_repo.load_all()

        # Búsqueda en título, género y autor
        results = []
        query_lower = query.lower()

        for book in books:
            # Buscar en título
            if query_lower in book.title.lower():
                score = 3  # Alta prioridad
            # Buscar en género
            elif book.genre and query_lower in book.genre.lower():
                score = 2  # Media prioridad
            # Buscar en autor (por ahora solo ID)
            elif query_lower in book.author_id.lower():
                score = 1  # Baja prioridad
            else:
                continue

            results.append({
                "book": {
                    "id": book.id,
                    "title": book.title,
                    "author_id": book.author_id,
                    "genre": book.genre,
                    "available": book.available
                },
                "score": score
            })

        # Ordenar por score y limitar
        results.sort(key=lambda x: x['score'], reverse=True)
        results = results[:limit]

        return jsonify({
            "query": query,
            "total_results": len(results),
            "results": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500