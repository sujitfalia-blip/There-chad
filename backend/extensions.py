from flask_sqlalchemy import SQLAlchemy

from flask_socketio import SocketIO

from flask_jwt_extended import JWTManager

from flask_migrate import Migrate





# ================= DATABASE =================

db = SQLAlchemy()

# ================= SOCKET =================

socketio = SocketIO()

# ================= JWT =================

jwt = JWTManager()

# ================= MIGRATE =================

migrate = Migrate()

# ================= RATE LIMIT ==============
from flask_sqlalchemy import SQLAlchemy

from flask_socketio import SocketIO

from flask_jwt_extended import JWTManager

# ================= DATABASE =================

db = SQLAlchemy()

# ================= SOCKET =================

socketio = SocketIO(
    cors_allowed_origins="*"
)

# ================= JWT =================

jwt = JWTManager()
