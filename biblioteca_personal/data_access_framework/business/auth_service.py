"""
Auth Service - Servicio de autenticación y autorización

Maneja login, registro de usuarios y control de permisos.

Autor: DAM2526
"""

import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

from ..core.entity_manager import EntityManager
from ..models import User


class AuthService:
    """
    Servicio que maneja autenticación y autorización de usuarios.
    """

    def __init__(self, entity_manager: EntityManager):
        """
        Inicializar servicio de autenticación.

        Args:
            entity_manager: Gestor de entidades
        """
        self.entity_manager = entity_manager
        self.user_repo = entity_manager.get_repository(User)

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Autenticar usuario con email y contraseña.

        Args:
            email: Email del usuario
            password: Contraseña en texto plano

        Returns:
            User si autenticación exitosa, None si falla
        """
        # Buscar usuario por email
        users = self.user_repo.find_by(email=email)
        if not users:
            return None

        user = users[0]  # Asumimos que email es único

        # Verificar que usuario esté activo
        if not user.active:
            return None

        # Verificar contraseña
        if not self._verify_password(password, user.password_hash):
            return None

        # Actualizar fecha de último acceso
        user.updated_at = datetime.now()
        self.user_repo.save(user)

        return user

    def register_user(self, name: str, last_name: str, email: str,
                     password: str, role: str = "user") -> User:
        """
        Registrar un nuevo usuario.

        Args:
            name: Nombre del usuario
            last_name: Apellidos del usuario
            email: Email único del usuario
            password: Contraseña en texto plano
            role: Rol del usuario (user, admin, librarian)

        Returns:
            User: Usuario creado

        Raises:
            ValueError: Si el email ya existe o datos inválidos
        """
        # Verificar que el email no esté registrado
        existing_users = self.user_repo.find_by(email=email)
        if existing_users:
            raise ValueError(f"Email ya registrado: {email}")

        # Validar rol
        if role not in ["user", "admin", "librarian"]:
            raise ValueError(f"Rol inválido: {role}")

        # Crear usuario
        user = User(
            name=name,
            last_name=last_name,
            email=email,
            role=role,
            active=True
        )

        # Hashear contraseña
        user.set_password(password)

        # Guardar usuario
        success = self.user_repo.save(user)
        if not success:
            raise RuntimeError("Error al guardar el usuario")

        return user

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Cambiar contraseña de un usuario.

        Args:
            user_id: ID del usuario
            old_password: Contraseña actual
            new_password: Nueva contraseña

        Returns:
            bool: True si cambió exitosamente
        """
        user = self.user_repo.load(user_id)
        if not user:
            raise ValueError(f"Usuario no encontrado: {user_id}")

        # Verificar contraseña actual
        if not self._verify_password(old_password, user.password_hash):
            raise ValueError("Contraseña actual incorrecta")

        # Validar nueva contraseña
        if len(new_password) < 6:
            raise ValueError("La nueva contraseña debe tener al menos 6 caracteres")

        # Cambiar contraseña
        user.set_password(new_password)
        user.updated_at = datetime.now()

        return self.user_repo.save(user)

    def deactivate_user(self, user_id: str, admin_user_id: str) -> bool:
        """
        Desactivar cuenta de usuario (solo admin).

        Args:
            user_id: ID del usuario a desactivar
            admin_user_id: ID del admin que realiza la acción

        Returns:
            bool: True si desactivó exitosamente
        """
        # Verificar permisos de admin
        admin = self.user_repo.load(admin_user_id)
        if not admin or admin.role != "admin":
            raise ValueError("Solo administradores pueden desactivar usuarios")

        # No permitir desactivar a sí mismo
        if user_id == admin_user_id:
            raise ValueError("No puedes desactivar tu propia cuenta")

        # Desactivar usuario
        user = self.user_repo.load(user_id)
        if not user:
            raise ValueError(f"Usuario no encontrado: {user_id}")

        user.active = False
        user.updated_at = datetime.now()

        return self.user_repo.save(user)

    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Actualizar perfil de usuario.

        Args:
            user_id: ID del usuario
            updates: Campos a actualizar

        Returns:
            bool: True si actualizó exitosamente
        """
        user = self.user_repo.load(user_id)
        if not user:
            raise ValueError(f"Usuario no encontrado: {user_id}")

        # Campos permitidos para actualización
        allowed_fields = ["name", "last_name", "email"]

        for field, value in updates.items():
            if field in allowed_fields:
                # Verificar email único si se cambia
                if field == "email" and value != user.email:
                    existing = self.user_repo.find_by(email=value)
                    if existing:
                        raise ValueError(f"Email ya en uso: {value}")

                setattr(user, field, value)
            else:
                raise ValueError(f"Campo no permitido para actualización: {field}")

        user.updated_at = datetime.now()
        return self.user_repo.save(user)

    def authorize(self, user: User, action: str, resource: str = None) -> bool:
        """
        Verificar si un usuario tiene permisos para una acción.

        Args:
            user: Usuario a verificar
            action: Acción a realizar (read, write, delete, admin)
            resource: Recurso específico (opcional)

        Returns:
            bool: True si tiene permisos
        """
        if not user or not user.active:
            return False

        # Definir permisos por rol
        permissions = {
            "user": ["read"],
            "librarian": ["read", "write"],
            "admin": ["read", "write", "delete", "admin"]
        }

        user_permissions = permissions.get(user.role, [])

        # Acciones básicas
        if action in user_permissions:
            return True

        # Permisos especiales
        if action == "admin" and user.role == "admin":
            return True

        # Permisos sobre recursos propios
        if resource and resource == user.id:
            return action in ["read", "write"]

        return False

    def get_user_permissions(self, user: User) -> Dict[str, Any]:
        """
        Obtener permisos detallados de un usuario.

        Args:
            user: Usuario

        Returns:
            Dict con permisos
        """
        return {
            "role": user.role,
            "can_read": self.authorize(user, "read"),
            "can_write": self.authorize(user, "write"),
            "can_delete": self.authorize(user, "delete"),
            "is_admin": user.role == "admin",
            "is_librarian": user.role == "librarian"
        }

    def reset_password(self, email: str, new_password: str) -> bool:
        """
        Resetear contraseña (solo para administradores en producción).

        Args:
            email: Email del usuario
            new_password: Nueva contraseña

        Returns:
            bool: True si reseteó exitosamente
        """
        users = self.user_repo.find_by(email=email)
        if not users:
            return False  # No revelar si email existe

        user = users[0]
        user.set_password(new_password)
        user.updated_at = datetime.now()

        return self.user_repo.save(user)

    def _hash_password(self, password: str) -> str:
        """Hashear contraseña usando SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verificar contraseña contra hash."""
        return self._hash_password(password) == hashed

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Obtener usuario por email.

        Args:
            email: Email del usuario

        Returns:
            User o None si no existe
        """
        users = self.user_repo.find_by(email=email)
        return users[0] if users else None

    def list_users(self, active_only: bool = True) -> list:
        """
        Listar usuarios con filtros.

        Args:
            active_only: Solo usuarios activos

        Returns:
            Lista de usuarios
        """
        all_users = self.user_repo.load_all()

        if active_only:
            return [user for user in all_users if user.active]

        return all_users