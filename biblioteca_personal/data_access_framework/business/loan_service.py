"""
Loan Service - Servicio de gestión de préstamos

Implementa la lógica de negocio para préstamos de libros,
incluyendo validaciones, cálculos de fechas y penalizaciones.

Autor: DAM2526
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ..core.entity_manager import EntityManager
from ..models import Loan, Book, User


class LoanService:
    """
    Servicio que maneja toda la lógica de negocio relacionada
    con préstamos de libros.
    """

    def __init__(self, entity_manager: EntityManager, config: Dict[str, Any] = None):
        """
        Inicializar servicio de préstamos.

        Args:
            entity_manager: Gestor de entidades
            config: Configuración del servicio
        """
        self.entity_manager = entity_manager
        self.config = config or {
            "default_loan_days": 14,
            "max_loans_per_user": 3,
            "fine_per_day": 0.50
        }

    def create_loan(self, book_id: str, user_id: str, days: int = None) -> Loan:
        """
        Crear un nuevo préstamo con validaciones completas.

        Args:
            book_id: ID del libro a prestar
            user_id: ID del usuario que solicita el préstamo
            days: Días de préstamo (usa configuración por defecto si None)

        Returns:
            Loan: Instancia del préstamo creado

        Raises:
            ValueError: Si las validaciones fallan
        """
        # Validar que el libro existe y está disponible
        book_repo = self.entity_manager.get_repository(Book)
        book = book_repo.load(book_id)
        if not book:
            raise ValueError(f"Libro no encontrado: {book_id}")

        if not book.available:
            raise ValueError(f"Libro no disponible: {book.title}")

        # Validar que el usuario existe y está activo
        user_repo = self.entity_manager.get_repository(User)
        user = user_repo.load(user_id)
        if not user:
            raise ValueError(f"Usuario no encontrado: {user_id}")

        if not user.active:
            raise ValueError(f"Usuario inactivo: {user.full_name}")

        # Verificar límite de préstamos por usuario
        active_loans = self.get_active_loans_by_user(user_id)
        if len(active_loans) >= self.config["max_loans_per_user"]:
            raise ValueError(f"Usuario ha alcanzado el límite de préstamos ({self.config['max_loans_per_user']})")

        # Verificar que el usuario no tenga ya este libro prestado
        for loan in active_loans:
            if loan.book_id == book_id:
                raise ValueError(f"Usuario ya tiene prestado este libro: {book.title}")

        # Calcular fechas
        loan_date = datetime.now()
        loan_days = days or self.config["default_loan_days"]
        due_date = loan_date + timedelta(days=loan_days)

        # Crear préstamo
        loan = Loan(
            book_id=book_id,
            user_id=user_id,
            loan_date=loan_date,
            due_date=due_date,
            status="active"
        )

        # Guardar préstamo
        loan_repo = self.entity_manager.get_repository(Loan)
        success = loan_repo.save(loan)
        if not success:
            raise RuntimeError("Error al guardar el préstamo")

        # Marcar libro como no disponible
        book.available = False
        book_repo.save(book)

        return loan

    def return_loan(self, loan_id: str, return_date: datetime = None) -> Dict[str, Any]:
        """
        Procesar la devolución de un préstamo.

        Args:
            loan_id: ID del préstamo a devolver
            return_date: Fecha de devolución (ahora si None)

        Returns:
            Dict con información de la devolución incluyendo penalizaciones
        """
        loan_repo = self.entity_manager.get_repository(Loan)
        loan = loan_repo.load(loan_id)

        if not loan:
            raise ValueError(f"Préstamo no encontrado: {loan_id}")

        if loan.status != "active":
            raise ValueError(f"Préstamo ya devuelto: {loan_id}")

        # Procesar devolución
        return_date = return_date or datetime.now()
        loan.return_book(return_date)

        # Calcular penalizaciones
        fine = 0.0
        if loan.is_overdue:
            days_overdue = loan.days_overdue
            fine = days_overdue * self.config["fine_per_day"]

        # Guardar cambios
        loan_repo.save(loan)

        # Marcar libro como disponible
        book_repo = self.entity_manager.get_repository(Book)
        book = book_repo.load(loan.book_id)
        if book:
            book.available = True
            book_repo.save(book)

        return {
            "loan_id": loan_id,
            "return_date": return_date.isoformat(),
            "days_overdue": max(0, loan.days_overdue),
            "fine_amount": fine,
            "status": "returned"
        }

    def get_active_loans(self) -> List[Loan]:
        """
        Obtener todos los préstamos activos.

        Returns:
            Lista de préstamos activos
        """
        loan_repo = self.entity_manager.get_repository(Loan)
        all_loans = loan_repo.load_all()
        return [loan for loan in all_loans if loan.status == "active"]

    def get_overdue_loans(self) -> List[Loan]:
        """
        Obtener préstamos vencidos.

        Returns:
            Lista de préstamos vencidos
        """
        active_loans = self.get_active_loans()
        return [loan for loan in active_loans if loan.is_overdue]

    def get_active_loans_by_user(self, user_id: str) -> List[Loan]:
        """
        Obtener préstamos activos de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de préstamos activos del usuario
        """
        loan_repo = self.entity_manager.get_repository(Loan)
        user_loans = loan_repo.find_by(user_id=user_id)
        return [loan for loan in user_loans if loan.status == "active"]

    def get_loan_history(self, user_id: str = None, book_id: str = None) -> List[Loan]:
        """
        Obtener historial de préstamos con filtros opcionales.

        Args:
            user_id: Filtrar por usuario
            book_id: Filtrar por libro

        Returns:
            Lista de préstamos que cumplen los criterios
        """
        loan_repo = self.entity_manager.get_repository(Loan)
        all_loans = loan_repo.load_all()

        filtered_loans = all_loans

        if user_id:
            filtered_loans = [loan for loan in filtered_loans if loan.user_id == user_id]

        if book_id:
            filtered_loans = [loan for loan in filtered_loans if loan.book_id == book_id]

        return filtered_loans

    def extend_loan(self, loan_id: str, additional_days: int = 7) -> Loan:
        """
        Extender la fecha de vencimiento de un préstamo.

        Args:
            loan_id: ID del préstamo
            additional_days: Días adicionales

        Returns:
            Loan actualizado
        """
        loan_repo = self.entity_manager.get_repository(Loan)
        loan = loan_repo.load(loan_id)

        if not loan:
            raise ValueError(f"Préstamo no encontrado: {loan_id}")

        if loan.status != "active":
            raise ValueError(f"No se puede extender un préstamo {loan.status}")

        # Extender fecha de vencimiento
        loan.due_date = loan.due_date + timedelta(days=additional_days)
        loan.updated_at = datetime.now()

        loan_repo.save(loan)
        return loan

    def calculate_fines(self, user_id: str) -> Dict[str, Any]:
        """
        Calcular penalizaciones pendientes de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Dict con información de penalizaciones
        """
        overdue_loans = []
        total_fine = 0.0

        user_loans = self.get_active_loans_by_user(user_id)
        for loan in user_loans:
            if loan.is_overdue:
                days_overdue = loan.days_overdue
                fine = days_overdue * self.config["fine_per_day"]
                total_fine += fine

                overdue_loans.append({
                    "loan_id": loan.id,
                    "book_id": loan.book_id,
                    "days_overdue": days_overdue,
                    "fine": fine,
                    "due_date": loan.due_date.isoformat()
                })

        return {
            "user_id": user_id,
            "total_fine": total_fine,
            "overdue_loans": overdue_loans,
            "fine_per_day": self.config["fine_per_day"]
        }

    def get_loan_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de préstamos.

        Returns:
            Dict con estadísticas
        """
        loan_repo = self.entity_manager.get_repository(Loan)
        all_loans = loan_repo.load_all()

        active_loans = [l for l in all_loans if l.status == "active"]
        returned_loans = [l for l in all_loans if l.status == "returned"]
        overdue_loans = [l for l in active_loans if l.is_overdue]

        return {
            "total_loans": len(all_loans),
            "active_loans": len(active_loans),
            "returned_loans": len(returned_loans),
            "overdue_loans": len(overdue_loans),
            "overdue_percentage": (len(overdue_loans) / len(active_loans) * 100) if active_loans else 0
        }