"""
Reports API Routes - Endpoints de informes y estadísticas

Proporciona informes avanzados sobre libros, préstamos y usuarios.

Autor: DAM2526
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from ..app import token_required

bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/books/popular', methods=['GET'])
def get_popular_books():
    """Obtener libros más populares (por número de préstamos)."""
    try:
        limit = int(request.args.get('limit', 10))
        period_days = int(request.args.get('period_days', 365))  # Último año por defecto

        report_service = request.current_app.framework.get_service('report')
        popular_books = report_service.get_most_popular_books(limit=limit, period_days=period_days)

        result = []
        for book_data in popular_books:
            result.append({
                "book_id": book_data['book_id'],
                "title": book_data['title'],
                "author": book_data['author'],
                "loan_count": book_data['loan_count'],
                "category": book_data['category']
            })

        return jsonify({
            "popular_books": result,
            "period_days": period_days,
            "limit": limit
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/books/available', methods=['GET'])
def get_available_books():
    """Obtener libros disponibles para préstamo."""
    try:
        category = request.args.get('category')
        author = request.args.get('author')
        search = request.args.get('search')

        report_service = request.current_app.framework.get_service('report')
        available_books = report_service.get_available_books(
            category=category,
            author=author,
            search=search
        )

        result = []
        for book in available_books:
            result.append({
                "id": book.id,
                "title": book.title,
                "author": book.author.full_name if book.author else None,
                "isbn": book.isbn,
                "category": book.category.name if book.category else None,
                "available_copies": book.available_copies
            })

        return jsonify({
            "available_books": result,
            "total": len(result)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/loans/summary', methods=['GET'])
def get_loans_summary():
    """Obtener resumen de préstamos por período."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Si no se especifican fechas, usar último mes
        if not start_date:
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=30)
        else:
            start_date_obj = datetime.fromisoformat(start_date)
            end_date_obj = datetime.fromisoformat(end_date) if end_date else datetime.now()

        report_service = request.current_app.framework.get_service('report')
        summary = report_service.get_loans_summary(start_date_obj, end_date_obj)

        return jsonify({
            "summary": summary,
            "period": {
                "start_date": start_date_obj.isoformat(),
                "end_date": end_date_obj.isoformat()
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/users/activity', methods=['GET'])
def get_user_activity():
    """Obtener actividad de usuarios (préstamos realizados)."""
    try:
        limit = int(request.args.get('limit', 20))
        period_days = int(request.args.get('period_days', 365))

        report_service = request.current_app.framework.get_service('report')
        user_activity = report_service.get_user_activity(limit=limit, period_days=period_days)

        result = []
        for user_data in user_activity:
            result.append({
                "user_id": user_data['user_id'],
                "name": user_data['name'],
                "email": user_data['email'],
                "loan_count": user_data['loan_count'],
                "active_loans": user_data['active_loans'],
                "overdue_loans": user_data['overdue_loans']
            })

        return jsonify({
            "user_activity": result,
            "period_days": period_days,
            "limit": limit
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/fines/summary', methods=['GET'])
def get_fines_summary():
    """Obtener resumen de multas."""
    try:
        report_service = request.current_app.framework.get_service('report')
        fines_summary = report_service.get_fines_summary()

        return jsonify(fines_summary)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/categories/stats', methods=['GET'])
def get_category_statistics():
    """Obtener estadísticas por categoría."""
    try:
        report_service = request.current_app.framework.get_service('report')
        category_stats = report_service.get_category_statistics()

        result = []
        for stat in category_stats:
            result.append({
                "category": stat['category'],
                "book_count": stat['book_count'],
                "loan_count": stat['loan_count'],
                "available_books": stat['available_books']
            })

        return jsonify({
            "category_statistics": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Obtener datos para dashboard principal."""
    try:
        report_service = request.current_app.framework.get_service('report')
        dashboard_data = report_service.get_dashboard_data()

        return jsonify(dashboard_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/books/search', methods=['GET'])
def search_books():
    """Buscar libros con filtros avanzados."""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        author = request.args.get('author')
        available_only = request.args.get('available_only', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        report_service = request.current_app.framework.get_service('report')
        search_results = report_service.search_books(
            query=query,
            category=category,
            author=author,
            available_only=available_only,
            page=page,
            per_page=per_page
        )

        result = []
        for book in search_results['books']:
            result.append({
                "id": book.id,
                "title": book.title,
                "author": book.author.full_name if book.author else None,
                "isbn": book.isbn,
                "category": book.category.name if book.category else None,
                "available_copies": book.available_copies,
                "total_copies": book.total_copies
            })

        return jsonify({
            "books": result,
            "total": search_results['total'],
            "page": page,
            "per_page": per_page,
            "pages": search_results['pages']
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/export/books', methods=['GET'])
def export_books_report():
    """Exportar informe de libros en formato JSON."""
    try:
        format_type = request.args.get('format', 'json')  # json, csv, xml
        include_loans = request.args.get('include_loans', 'false').lower() == 'true'

        report_service = request.current_app.framework.get_service('report')
        export_data = report_service.export_books_report(
            format_type=format_type,
            include_loans=include_loans
        )

        return jsonify({
            "export_data": export_data,
            "format": format_type,
            "include_loans": include_loans
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/export/loans', methods=['GET'])
def export_loans_report():
    """Exportar informe de préstamos en formato JSON."""
    try:
        format_type = request.args.get('format', 'json')  # json, csv, xml
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')  # active, returned, overdue

        # Convertir fechas
        start_date_obj = datetime.fromisoformat(start_date) if start_date else None
        end_date_obj = datetime.fromisoformat(end_date) if end_date else None

        report_service = request.current_app.framework.get_service('report')
        export_data = report_service.export_loans_report(
            format_type=format_type,
            start_date=start_date_obj,
            end_date=end_date_obj,
            status=status
        )

        return jsonify({
            "export_data": export_data,
            "format": format_type,
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "status": status
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/analytics/monthly', methods=['GET'])
def get_monthly_analytics():
    """Obtener análisis mensual de actividad."""
    try:
        months = int(request.args.get('months', 12))  # Últimos 12 meses por defecto

        report_service = request.current_app.framework.get_service('report')
        analytics = report_service.get_monthly_analytics(months=months)

        return jsonify({
            "monthly_analytics": analytics,
            "months": months
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500