"""
Loans API Routes - Endpoints de gestión de préstamos

Maneja operaciones CRUD para préstamos de libros.

Autor: DAM2526
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from ..app import token_required

bp = Blueprint('loans', __name__, url_prefix='/api/loans')


@bp.route('', methods=['GET'])
def get_loans():
    """Obtener lista de préstamos con filtros opcionales."""
    try:
        # Parámetros de consulta
        user_id = request.args.get('user_id')
        book_id = request.args.get('book_id')
        status = request.args.get('status')  # active, returned, overdue
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        loan_service = request.current_app.framework.get_service('loan')

        # Obtener préstamos según filtros
        if user_id:
            loans = loan_service.get_user_loans(user_id, status=status)
        elif book_id:
            loans = loan_service.get_book_loans(book_id, status=status)
        else:
            loans = loan_service.get_all_loans(status=status)

        # Paginación
        start = (page - 1) * per_page
        end = start + per_page
        paginated_loans = loans[start:end]

        # Convertir a diccionarios
        result = []
        for loan in paginated_loans:
            result.append({
                "id": loan.id,
                "user_id": loan.user_id,
                "book_id": loan.book_id,
                "loan_date": loan.loan_date.isoformat(),
                "due_date": loan.due_date.isoformat(),
                "return_date": loan.return_date.isoformat() if loan.return_date else None,
                "status": loan.status,
                "fine_amount": loan.fine_amount,
                "notes": loan.notes,
                "book_title": loan.book.title if loan.book else None,
                "user_name": loan.user.full_name if loan.user else None
            })

        return jsonify({
            "loans": result,
            "total": len(loans),
            "page": page,
            "per_page": per_page,
            "pages": (len(loans) + per_page - 1) // per_page
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/<loan_id>', methods=['GET'])
def get_loan(loan_id):
    """Obtener detalles de un préstamo específico."""
    try:
        loan_service = request.current_app.framework.get_service('loan')
        loan = loan_service.get_loan_by_id(loan_id)

        if not loan:
            return jsonify({"error": "Préstamo no encontrado"}), 404

        return jsonify({
            "id": loan.id,
            "user_id": loan.user_id,
            "book_id": loan.book_id,
            "loan_date": loan.loan_date.isoformat(),
            "due_date": loan.due_date.isoformat(),
            "return_date": loan.return_date.isoformat() if loan.return_date else None,
            "status": loan.status,
            "fine_amount": loan.fine_amount,
            "notes": loan.notes,
            "book": {
                "id": loan.book.id,
                "title": loan.book.title,
                "author": loan.book.author.full_name if loan.book.author else None,
                "isbn": loan.book.isbn
            } if loan.book else None,
            "user": {
                "id": loan.user.id,
                "name": loan.user.full_name,
                "email": loan.user.email
            } if loan.user else None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('', methods=['POST'])
@token_required
def create_loan():
    """Crear un nuevo préstamo."""
    try:
        data = request.get_json()

        required_fields = ['user_id', 'book_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400

        user_id = data['user_id']
        book_id = data['book_id']
        loan_days = data.get('loan_days', 14)  # Por defecto 14 días
        notes = data.get('notes', '')

        loan_service = request.current_app.framework.get_service('loan')

        # Crear préstamo
        loan = loan_service.create_loan(
            user_id=user_id,
            book_id=book_id,
            loan_days=loan_days,
            notes=notes
        )

        return jsonify({
            "message": "Préstamo creado exitosamente",
            "loan": {
                "id": loan.id,
                "user_id": loan.user_id,
                "book_id": loan.book_id,
                "loan_date": loan.loan_date.isoformat(),
                "due_date": loan.due_date.isoformat(),
                "status": loan.status,
                "notes": loan.notes
            }
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/<loan_id>/return', methods=['POST'])
@token_required
def return_loan(loan_id):
    """Devolver un préstamo."""
    try:
        data = request.get_json() or {}
        notes = data.get('notes', '')

        loan_service = request.current_app.framework.get_service('loan')

        # Devolver préstamo
        result = loan_service.return_loan(loan_id, notes=notes)

        return jsonify({
            "message": "Préstamo devuelto exitosamente",
            "loan": {
                "id": result['loan'].id,
                "return_date": result['loan'].return_date.isoformat(),
                "status": result['loan'].status,
                "fine_amount": result['loan'].fine_amount,
                "days_overdue": result.get('days_overdue', 0),
                "fine_calculated": result.get('fine_calculated', 0.0)
            }
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/<loan_id>/extend', methods=['POST'])
@token_required
def extend_loan(loan_id):
    """Extender la fecha de devolución de un préstamo."""
    try:
        data = request.get_json() or {}
        extra_days = data.get('extra_days', 7)  # Por defecto 7 días más

        loan_service = request.current_app.framework.get_service('loan')

        # Extender préstamo
        loan = loan_service.extend_loan(loan_id, extra_days)

        return jsonify({
            "message": "Préstamo extendido exitosamente",
            "loan": {
                "id": loan.id,
                "due_date": loan.due_date.isoformat(),
                "status": loan.status
            }
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/overdue', methods=['GET'])
def get_overdue_loans():
    """Obtener préstamos vencidos."""
    try:
        loan_service = request.current_app.framework.get_service('loan')
        overdue_loans = loan_service.get_overdue_loans()

        result = []
        for loan in overdue_loans:
            days_overdue = (datetime.now() - loan.due_date).days
            result.append({
                "id": loan.id,
                "user_id": loan.user_id,
                "book_id": loan.book_id,
                "due_date": loan.due_date.isoformat(),
                "days_overdue": days_overdue,
                "fine_amount": loan.fine_amount,
                "book_title": loan.book.title if loan.book else None,
                "user_name": loan.user.full_name if loan.user else None,
                "user_email": loan.user.email if loan.user else None
            })

        return jsonify({
            "overdue_loans": result,
            "total": len(result)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/statistics', methods=['GET'])
def get_loan_statistics():
    """Obtener estadísticas de préstamos."""
    try:
        loan_service = request.current_app.framework.get_service('loan')
        stats = loan_service.get_loan_statistics()

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/user/<user_id>/active', methods=['GET'])
def get_user_active_loans(user_id):
    """Obtener préstamos activos de un usuario."""
    try:
        loan_service = request.current_app.framework.get_service('loan')
        active_loans = loan_service.get_user_active_loans(user_id)

        result = []
        for loan in active_loans:
            result.append({
                "id": loan.id,
                "book_id": loan.book_id,
                "loan_date": loan.loan_date.isoformat(),
                "due_date": loan.due_date.isoformat(),
                "book_title": loan.book.title if loan.book else None,
                "book_author": loan.book.author.full_name if loan.book and loan.book.author else None
            })

        return jsonify({
            "active_loans": result,
            "count": len(result)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500