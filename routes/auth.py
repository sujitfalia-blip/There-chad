from datetime import datetime

from flask import (
    Blueprint,
    request,
    jsonify
)

from flask_jwt_extended import (
    create_access_token
)

from werkzeug.security import (
    check_password_hash
)

from extensions import db

from models.user import User

# ================= BLUEPRINT =================

auth_bp = Blueprint(
    'auth',
    __name__
)

# ================= LOGIN =================

@auth_bp.route(
    '/login',
    methods=['POST']
)
def login():

    try:

        # ================= REQUEST DATA =================

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message": "Invalid request"
            }), 400

        phone = data.get('phone')

        password = data.get('password')

        # ================= VALIDATION =================

        if not phone or not password:

            return jsonify({

                "success": False,

                "message":
                    "Phone and password required"
            }), 400

        # ================= USER =================

        user = User.query.filter_by(
            phone=phone
        ).first()

        if not user:

            return jsonify({

                "success": False,

                "message": "User not found"
            }), 404

        # ================= ACCOUNT STATUS =================

        if user.is_banned:

            return jsonify({

                "success": False,

                "message":
                    "Account banned"
            }), 403

        if not user.is_active:

            return jsonify({

                "success": False,

                "message":
                    "Account inactive"
            }), 403

        # ================= PASSWORD CHECK =================

        if not check_password_hash(
            user.password_hash,
            password
        ):

            return jsonify({

                "success": False,

                "message":
                    "Invalid credentials"
            }), 401

        # ================= UPDATE LOGIN =================

        user.last_login = datetime.utcnow()

        user.is_online = True

        db.session.commit()

        # ================= JWT TOKEN =================

        access_token = create_access_token(

            identity=str(user.id)
        )

        # ================= RESPONSE =================

        return jsonify({

            "success": True,

            "message":
                "Login successful",

            "token": access_token,

            "user": {

                "id": user.id,

                "name": user.name,

                "username":
                    user.username,

                "phone":
                    user.phone,

                "coins":
                    user.coins,

                "role":
                    user.role,

                "profile_photo":
                    user.profile_photo,

                "is_verified":
                    user.is_verified
            }
        })

    # ================= ERROR =================

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": "Server error",

            "error": str(e)

        }), 500

# ================= REGISTER =================

@auth_bp.route(
    '/register',
    methods=['POST']
)
def register():

    try:

        # ================= DATA =================

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message": "Invalid request"
            }), 400

        name = data.get('name')

        phone = data.get('phone')

        password = data.get('password')

        # ================= VALIDATION =================

        if not all([

            name,
            phone,
            password
        ]):

            return jsonify({

                "success": False,

                "message":
                    "All fields required"
            }), 400

        # ================= EXISTING USER =================

        existing_user = User.query.filter_by(
            phone=phone
        ).first()

        if existing_user:

            return jsonify({

                "success": False,

                "message":
                    "Phone already exists"
            }), 400

        # ================= CREATE USER =================

        user = User(

            name=name,

            phone=phone,

            username=f"user_{phone[-4:]}"
        )

        user.set_password(password)

        db.session.add(user)

        db.session.commit()

        # ================= TOKEN =================

        access_token = create_access_token(

            identity=str(user.id)
        )

        # ================= RESPONSE =================

        return jsonify({

            "success": True,

            "message":
                "Registration successful",

            "token": access_token,

            "user": {

                "id": user.id,

                "name": user.name,

                "phone": user.phone,

                "coins": user.coins
            }
        })

    # ================= ERROR =================

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": "Server error",

            "error": str(e)

        }), 500

# ================= PROFILE =================

@auth_bp.route(
    '/profile',
    methods=['GET']
)
def profile():

    return jsonify({

        "success": True,

        "message":
            "Profile API ready"
    })

# ================= LOGOUT =================

@auth_bp.route(
    '/logout',
    methods=['POST']
)
def logout():

    return jsonify({

        "success": True,

        "message":
            "Logout successful"
    })
