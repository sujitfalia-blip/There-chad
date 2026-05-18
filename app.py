import os

from flask import Flask, jsonify

from flask_cors import CORS

from extensions import db, jwt, migrate, socketio


# ================= IMPORT ROUTES =================

from backend.routes.auth import auth_bp
from backend.routes.game import game_bp
from backend.routes.admin import admin_bp
from backend.routes.wallet import wallet_bp


# ================= CREATE APP =================

app = Flask(__name__)


# ================= CONFIG =================

app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY',
    'super-secret-key'
)

# 🔥 FIXED: SQLite for Pydroid (NO POSTGRES)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///teenpatti.db'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.getenv(
    'JWT_SECRET_KEY',
    'jwt-secret'
)


# ================= CORS =================

CORS(app, resources={r"/*": {"origins": "*"}})


# ================= INIT EXTENSIONS =================

db.init_app(app)

jwt.init_app(app)

migrate.init_app(app, db)

socketio.init_app(
    app,
    cors_allowed_origins="*",
    async_mode="threading"   # 🔥 FIX for Pydroid (eventlet avoid)
)


# ================= REGISTER BLUEPRINTS =================

app.register_blueprint(auth_bp, url_prefix='/api/auth')

app.register_blueprint(game_bp, url_prefix='/api/game')

app.register_blueprint(admin_bp, url_prefix='/api/admin')

app.register_blueprint(wallet_bp, url_prefix='/api/wallet')


# ================= HEALTH CHECK =================

@app.route('/')
def home():

    return jsonify({
        "status": "running",
        "app": "Teen Patti Pro"
    })


# ================= ERROR HANDLERS =================

@app.errorhandler(404)
def not_found(e):

    return jsonify({
        "error": "Route not found"
    }), 404


@app.errorhandler(500)
def internal_error(e):

    return jsonify({
        "error": "Internal server error"
    }), 500


# ================= CREATE DB =================

with app.app_context():
    db.create_all()


# ================= MAIN =================

if __name__ == '__main__':

    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True
    )
