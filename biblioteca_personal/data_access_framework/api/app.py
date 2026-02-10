"""
Flask API Application - API REST para el framework

Proporciona endpoints REST para acceder a todas las funcionalidades
del framework de manera remota.

Autor: DAM2526
"""

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os

from ..core.data_access_framework import DataAccessFramework


# Decorador para requerir autenticación
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Token requerido"}), 401

        try:
            # Remover "Bearer " del token
            if token.startswith('Bearer '):
                token = token[7:]

            # Decodificar token
            payload = jwt.decode(token, request.current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = payload['user_id']

            # Verificar que usuario existe
            user_repo = request.current_app.framework.get_repository('User')
            user = user_repo.load(current_user_id)
            if not user or not user.active:
                return jsonify({"error": "Usuario no válido"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        # Agregar usuario al request
        request.current_user = user
        return f(*args, **kwargs)

    return decorated


# Función para generar tokens JWT
def generate_token(user_id: str, app: Flask) -> str:
    """Generar token JWT para usuario."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),  # 24 horas
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def create_app(framework: DataAccessFramework) -> Flask:
    """
    Crear aplicación Flask configurada.

    Args:
        framework: Instancia del framework

    Returns:
        Flask app configurada
    """
    app = Flask(__name__)

    # Configuración
    app.config['SECRET_KEY'] = framework.config_manager.get('api.jwt_secret', 'default_secret')
    app.config['CORS_ENABLED'] = framework.config_manager.get('api.cors_enabled', True)

    if app.config['CORS_ENABLED']:
        CORS(app)

    # Referencia al framework
    app.framework = framework

    # Registrar rutas
    _register_routes(app)

    return app


def _register_routes(app: Flask):
    """Registrar todas las rutas de la API."""

    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint de health check."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        })

    @app.route('/stats', methods=['GET'])
    def get_stats():
        """Obtener estadísticas del sistema."""
        try:
            stats = app.framework.get_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Incluir rutas específicas
    from .routes.books import bp as books_bp
    from .routes.auth import bp as auth_bp
    from .routes.loans import bp as loans_bp
    from .routes.reports import bp as reports_bp

    app.register_blueprint(books_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(loans_bp)
    app.register_blueprint(reports_bp)

    # Middleware de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint no encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Error interno del servidor"}), 500