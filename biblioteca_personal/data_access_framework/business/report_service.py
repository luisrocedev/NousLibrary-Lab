"""
Report Service - Servicio de generación de reportes

Proporciona funcionalidades para generar reportes y estadísticas
del sistema de biblioteca.

Autor: DAM2526
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import statistics

from ..core.entity_manager import EntityManager
from ..models import Book, Author, User, Loan, Category


class ReportService:
    """
    Servicio que genera reportes y estadísticas del sistema.
    """

    def __init__(self, entity_manager: EntityManager):
        """
        Inicializar servicio de reportes.

        Args:
            entity_manager: Gestor de entidades
        """
        self.entity_manager = entity_manager

    def generate_library_overview(self) -> Dict[str, Any]:
        """
        Generar reporte general de la biblioteca.

        Returns:
            Dict con estadísticas generales
        """
        # Obtener datos básicos
        book_repo = self.entity_manager.get_repository(Book)
        author_repo = self.entity_manager.get_repository(Author)
        user_repo = self.entity_manager.get_repository(User)
        loan_repo = self.entity_manager.get_repository(Loan)

        books = book_repo.load_all()
        authors = author_repo.load_all()
        users = user_repo.load_all()
        loans = loan_repo.load_all()

        # Estadísticas básicas
        total_books = len(books)
        available_books = len([b for b in books if b.available])
        total_authors = len(authors)
        total_users = len(users)
        active_users = len([u for u in users if u.active])

        # Estadísticas de préstamos
        active_loans = len([l for l in loans if l.status == "active"])
        total_loans_ever = len(loans)
        overdue_loans = len([l for l in loans if l.status == "active" and l.is_overdue])

        return {
            "generated_at": datetime.now().isoformat(),
            "books": {
                "total": total_books,
                "available": available_books,
                "loaned": total_books - available_books,
                "availability_rate": (available_books / total_books * 100) if total_books > 0 else 0
            },
            "authors": {
                "total": total_authors
            },
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users
            },
            "loans": {
                "active": active_loans,
                "total_ever": total_loans_ever,
                "overdue": overdue_loans,
                "overdue_rate": (overdue_loans / active_loans * 100) if active_loans > 0 else 0
            }
        }

    def generate_books_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generar reporte detallado de libros.

        Args:
            filters: Filtros opcionales (genre, language, year_from, year_to, available)

        Returns:
            Dict con reporte de libros
        """
        book_repo = self.entity_manager.get_repository(Book)
        books = book_repo.load_all()

        # Aplicar filtros
        if filters:
            filtered_books = []
            for book in books:
                include = True

                if 'genre' in filters and filters['genre']:
                    if book.genre != filters['genre']:
                        include = False

                if 'language' in filters and filters['language']:
                    if book.language != filters['language']:
                        include = False

                if 'year_from' in filters and filters['year_from']:
                    if book.year < filters['year_from']:
                        include = False

                if 'year_to' in filters and filters['year_to']:
                    if book.year > filters['year_to']:
                        include = False

                if 'available' in filters and filters['available'] is not None:
                    if book.available != filters['available']:
                        include = False

                if include:
                    filtered_books.append(book)

            books = filtered_books

        # Estadísticas por género
        genres = Counter(book.genre for book in books if book.genre)

        # Estadísticas por idioma
        languages = Counter(book.language for book in books if book.language)

        # Estadísticas por año
        years = Counter(book.year for book in books if book.year)

        # Libros más antiguos y recientes
        valid_years = [book.year for book in books if book.year > 0]
        oldest_year = min(valid_years) if valid_years else None
        newest_year = max(valid_years) if valid_years else None

        return {
            "generated_at": datetime.now().isoformat(),
            "total_books": len(books),
            "filters_applied": filters or {},
            "by_genre": dict(genres.most_common()),
            "by_language": dict(languages.most_common()),
            "by_year": dict(sorted(years.items())),
            "year_range": {
                "oldest": oldest_year,
                "newest": newest_year
            },
            "top_genres": genres.most_common(5),
            "books_sample": [
                {
                    "id": book.id,
                    "title": book.title,
                    "author_id": book.author_id,
                    "genre": book.genre,
                    "year": book.year,
                    "available": book.available
                }
                for book in books[:10]  # Primeros 10 libros
            ]
        }

    def generate_authors_report(self) -> Dict[str, Any]:
        """
        Generar reporte de autores.

        Returns:
            Dict con estadísticas de autores
        """
        author_repo = self.entity_manager.get_repository(Author)
        book_repo = self.entity_manager.get_repository(Book)

        authors = author_repo.load_all()
        books = book_repo.load_all()

        # Contar libros por autor
        books_by_author = defaultdict(int)
        for book in books:
            books_by_author[book.author_id] += 1

        # Estadísticas de autores
        authors_with_books = []
        authors_without_books = []

        for author in authors:
            book_count = books_by_author.get(author.id, 0)
            author_data = {
                "id": author.id,
                "name": author.full_name,
                "nationality": author.nationality,
                "books_count": book_count
            }

            if book_count > 0:
                authors_with_books.append(author_data)
            else:
                authors_without_books.append(author_data)

        # Autores más prolíficos
        authors_with_books.sort(key=lambda x: x["books_count"], reverse=True)

        # Estadísticas por nacionalidad
        nationalities = Counter(author.nationality for author in authors if author.nationality)

        return {
            "generated_at": datetime.now().isoformat(),
            "total_authors": len(authors),
            "authors_with_books": len(authors_with_books),
            "authors_without_books": len(authors_without_books),
            "by_nationality": dict(nationalities.most_common()),
            "top_authors": authors_with_books[:10],
            "authors_without_books_sample": authors_without_books[:5]
        }

    def generate_loans_report(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """
        Generar reporte de préstamos en un período.

        Args:
            date_from: Fecha desde (ISO format)
            date_to: Fecha hasta (ISO format)

        Returns:
            Dict con estadísticas de préstamos
        """
        loan_repo = self.entity_manager.get_repository(Loan)
        book_repo = self.entity_manager.get_repository(Book)
        user_repo = self.entity_manager.get_repository(User)

        all_loans = loan_repo.load_all()

        # Filtrar por fechas
        if date_from:
            from_date = datetime.fromisoformat(date_from)
            all_loans = [l for l in all_loans if l.created_at >= from_date]

        if date_to:
            to_date = datetime.fromisoformat(date_to)
            all_loans = [l for l in all_loans if l.created_at <= to_date]

        # Estadísticas básicas
        total_loans = len(all_loans)
        active_loans = len([l for l in all_loans if l.status == "active"])
        returned_loans = len([l for l in all_loans if l.status == "returned"])
        overdue_loans = len([l for l in all_loans if l.status == "active" and l.is_overdue])

        # Libros más prestados
        book_loans = Counter(loan.book_id for loan in all_loans)
        top_books = book_loans.most_common(10)

        # Resolver nombres de libros
        books = {book.id: book for book in book_repo.load_all()}
        top_books_named = [
            {
                "book_id": book_id,
                "title": books.get(book_id, Book()).title,
                "loan_count": count
            }
            for book_id, count in top_books
        ]

        # Usuarios más activos
        user_loans = Counter(loan.user_id for loan in all_loans)
        top_users = user_loans.most_common(10)

        # Resolver nombres de usuarios
        users = {user.id: user for user in user_repo.load_all()}
        top_users_named = [
            {
                "user_id": user_id,
                "name": users.get(user_id, User()).full_name,
                "loan_count": count
            }
            for user_id, count in top_users
        ]

        # Duración promedio de préstamos devueltos
        returned_loans_list = [l for l in all_loans if l.status == "returned" and l.return_date]
        if returned_loans_list:
            durations = [(l.return_date - l.loan_date).days for l in returned_loans_list]
            avg_duration = statistics.mean(durations)
            median_duration = statistics.median(durations)
        else:
            avg_duration = 0
            median_duration = 0

        return {
            "generated_at": datetime.now().isoformat(),
            "period": {
                "from": date_from,
                "to": date_to
            },
            "summary": {
                "total_loans": total_loans,
                "active_loans": active_loans,
                "returned_loans": returned_loans,
                "overdue_loans": overdue_loans
            },
            "top_books": top_books_named,
            "top_users": top_users_named,
            "loan_duration": {
                "average_days": round(avg_duration, 1),
                "median_days": round(median_duration, 1)
            }
        }

    def generate_user_activity_report(self, user_id: str) -> Dict[str, Any]:
        """
        Generar reporte de actividad de un usuario específico.

        Args:
            user_id: ID del usuario

        Returns:
            Dict con actividad del usuario
        """
        user_repo = self.entity_manager.get_repository(User)
        loan_repo = self.entity_manager.get_repository(Loan)
        book_repo = self.entity_manager.get_repository(Book)

        user = user_repo.load(user_id)
        if not user:
            raise ValueError(f"Usuario no encontrado: {user_id}")

        # Obtener préstamos del usuario
        user_loans = loan_repo.find_by(user_id=user_id)

        # Estadísticas de préstamos
        total_loans = len(user_loans)
        active_loans = len([l for l in user_loans if l.status == "active"])
        returned_loans = len([l for l in user_loans if l.status == "returned"])
        overdue_loans = len([l for l in user_loans if l.status == "active" and l.is_overdue])

        # Historial de préstamos
        loan_history = []
        books = {book.id: book for book in book_repo.load_all()}

        for loan in sorted(user_loans, key=lambda x: x.created_at, reverse=True):
            book = books.get(loan.book_id, Book())
            loan_history.append({
                "loan_id": loan.id,
                "book_title": book.title,
                "loan_date": loan.loan_date.isoformat(),
                "due_date": loan.due_date.isoformat(),
                "return_date": loan.return_date.isoformat() if loan.return_date else None,
                "status": loan.status,
                "days_overdue": loan.days_overdue if loan.is_overdue else 0
            })

        return {
            "generated_at": datetime.now().isoformat(),
            "user": {
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
                "role": user.role,
                "active": user.active
            },
            "loan_stats": {
                "total_loans": total_loans,
                "active_loans": active_loans,
                "returned_loans": returned_loans,
                "overdue_loans": overdue_loans
            },
            "loan_history": loan_history[:20]  # Últimos 20 préstamos
        }

    def export_report(self, report_data: Dict[str, Any], format_type: str = "json") -> str:
        """
        Exportar reporte en diferentes formatos.

        Args:
            report_data: Datos del reporte
            format_type: Formato de exportación (json, csv, txt)

        Returns:
            String con el reporte exportado
        """
        if format_type == "json":
            import json
            return json.dumps(report_data, indent=2, ensure_ascii=False, default=str)

        elif format_type == "csv":
            # Implementar exportación CSV básica
            lines = ["Report Generated,Value"]
            for key, value in report_data.items():
                if isinstance(value, (int, float, str)):
                    lines.append(f"{key},{value}")
            return "\n".join(lines)

        else:
            # Formato de texto simple
            lines = [f"REPORTE GENERADO: {report_data.get('generated_at', 'N/A')}"]
            lines.append("=" * 50)

            def format_dict(d, prefix=""):
                result = []
                for key, value in d.items():
                    if isinstance(value, dict):
                        result.append(f"{prefix}{key}:")
                        result.extend(format_dict(value, prefix + "  "))
                    elif isinstance(value, list):
                        result.append(f"{prefix}{key}: {len(value)} items")
                    else:
                        result.append(f"{prefix}{key}: {value}")
                return result

            lines.extend(format_dict(report_data))
            return "\n".join(lines)