"""
Auth API Routes - Endpoints de autenticación

Maneja login, registro y gestión de usuarios.

Autor: DAM2526
"""

from flask import Blueprint, request, jsonify
from ..app import generate_token, token_required

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/login', methods=['POST'])
def login():
    """Iniciar sesión y obtener token JWT."""
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email y contraseña requeridos"}), 400

        email = data['email']
        password = data['password']

        # Autenticar usuario
        auth_service = request.current_app.framework.get_service('auth')
        user = auth_service.authenticate(email, password)

        if not user:
            return jsonify({"error": "Credenciales inválidas"}), 401

        # Generar token
        token = generate_token(user.id, request.current_app)

        return jsonify({
            "message": "Login exitoso",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
                "role": user.role
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario."""
    try:
        data = request.get_json()

        required_fields = ['name', 'last_name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400

        # Registrar usuario
        auth_service = request.current_app.framework.get_service('auth')
        user = auth_service.register_user(
            name=data['name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'user')
        )

        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user_id": user.id
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Obtener perfil del usuario actual (requiere token)."""
    try:
        # El token_required ya verificó el usuario
        user = request.current_user

        return jsonify({
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "role": user.role,
            "active": user.active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Actualizar perfil del usuario actual."""
    try:
        user = request.current_user
        data = request.get_json()

        # Campos permitidos para actualización propia
        allowed_fields = ['name', 'last_name']

        updates = {}
        for field in allowed_fields:
            if field in data:
                updates[field] = data[field]

        if not updates:
            return jsonify({"error": "No hay campos válidos para actualizar"}), 400

        # Actualizar
        auth_service = request.current_app.framework.get_service('auth')
        success = auth_service.update_user_profile(user.id, updates)

        if not success:
            return jsonify({"error": "Error al actualizar perfil"}), 500

        return jsonify({"message": "Perfil actualizado exitosamente"})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Cambiar contraseña del usuario actual."""
    try:
        user = request.current_user
        data = request.get_json()

        if 'old_password' not in data or 'new_password' not in data:
            return jsonify({"error": "Contraseña actual y nueva requeridas"}), 400

        # Cambiar contraseña
        auth_service = request.current_app.framework.get_service('auth')
        success = auth_service.change_password(
            user.id,
            data['old_password'],
            data['new_password']
        )

        if not success:
            return jsonify({"error": "Error al cambiar contraseña"}), 500

        return jsonify({"message": "Contraseña cambiada exitosamente"})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/users', methods=['GET'])
@token_required
def list_users():
    """Listar usuarios (solo admin)."""
    try:
        user = request.current_user

        # Verificar permisos de admin
        auth_service = request.current_app.framework.get_service('auth')
        if not auth_service.authorize(user, 'admin'):
            return jsonify({"error": "Permisos insuficientes"}), 403

        # Listar usuarios
        users = auth_service.list_users(active_only=False)

        result = []
        for u in users:
            result.append({
                "id": u.id,
                "name": u.full_name,
                "email": u.email,
                "role": u.role,
                "active": u.active,
                "created_at": u.created_at.isoformat() if u.created_at else None
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/users/<user_id>/deactivate', methods=['POST'])
@token_required
def deactivate_user(user_id):
    """Desactivar usuario (solo admin)."""
    try:
        admin = request.current_user

        # Verificar permisos de admin
        auth_service = request.current_app.framework.get_service('auth')
        if not auth_service.authorize(admin, 'admin'):
            return jsonify({"error": "Permisos insuficientes"}), 403

        # Desactivar usuario
        success = auth_service.deactivate_user(user_id, admin.id)

        if not success:
            return jsonify({"error": "Error al desactivar usuario"}), 500

        return jsonify({"message": "Usuario desactivado exitosamente"})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/permissions', methods=['GET'])
@token_required
def get_permissions():
    """Obtener permisos del usuario actual."""
    try:
        user = request.current_user

        auth_service = request.current_app.framework.get_service('auth')
        permissions = auth_service.get_user_permissions(user)

        return jsonify(permissions)

    except Exception as e:
        return jsonify({"error": str(e)}), 500