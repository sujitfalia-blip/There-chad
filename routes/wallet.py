from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy import select, func

from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db

from models.user import User


wallet_bp = Blueprint(
    'wallet',
    __name__
)


# =========================================================
# ================= SAFE GET USER =========================
# =========================================================

def get_user(user_id):

    return User.query.filter_by(
        id=user_id
    ).with_for_update().first()


# =========================================================
# ================= BALANCE ================================
# =========================================================

@wallet_bp.route(
    '/wallet/balance',
    methods=['GET']
)
@jwt_required()
def balance():

    try:

        user_id = get_jwt_identity()

        user = User.query.get(user_id)

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        return jsonify({

            "success": True,

            "balance": float(user.coins),

            "currency": "COIN"
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": "Server error",
            "error": str(e)

        }), 500


# =========================================================
# ================= ADD COINS (ADMIN ONLY) ================
# =========================================================

@wallet_bp.route(
    '/wallet/add',
    methods=['POST']
)
@jwt_required()
def add_coins():

    try:

        data = request.get_json()

        amount = data.get('amount')

        if not amount or amount <= 0:

            return jsonify({
                "success": False,
                "message": "Invalid amount"
            }), 400

        user_id = get_jwt_identity()

        user = get_user(user_id)

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        # ================= ATOMIC UPDATE =================

        user.coins = user.coins + amount

        user.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "Coins added",

            "balance": float(user.coins)
        })

    except SQLAlchemyError:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": "Database error"
        }), 500

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# =========================================================
# ================= DEDUCT COINS (SAFE LOCK) ==============
# =========================================================

@wallet_bp.route(
    '/wallet/deduct',
    methods=['POST']
)
@jwt_required()
def deduct_coins():

    try:

        data = request.get_json()

        amount = data.get('amount')

        if not amount or amount <= 0:

            return jsonify({
                "success": False,
                "message": "Invalid amount"
            }), 400

        user_id = get_jwt_identity()

        # ================= ROW LOCK =================

        user = db.session.query(User).filter_by(
            id=user_id
        ).with_for_update().first()

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        # ================= BALANCE CHECK =================

        if user.coins < amount:

            return jsonify({
                "success": False,
                "message": "Insufficient balance"
            }), 400

        # ================= DEDUCT =================

        user.coins -= amount

        user.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "Coins deducted",

            "balance": float(user.coins)
        })

    except SQLAlchemyError:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": "Transaction failed"
        }), 500

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# =========================================================
# ================= TRANSFER (USER TO USER) ===============
# =========================================================

@wallet_bp.route(
    '/wallet/transfer',
    methods=['POST']
)
@jwt_required()
def transfer():

    try:

        data = request.get_json()

        receiver_id = data.get('receiver_id')

        amount = data.get('amount')

        if not receiver_id or not amount:

            return jsonify({
                "success": False,
                "message": "Invalid request"
            }), 400

        sender_id = get_jwt_identity()

        if sender_id == receiver_id:

            return jsonify({
                "success": False,
                "message": "Self transfer not allowed"
            }), 400

        # ================= LOCK BOTH USERS =================

        sender = db.session.query(User).filter_by(
            id=sender_id
        ).with_for_update().first()

        receiver = db.session.query(User).filter_by(
            id=receiver_id
        ).with_for_update().first()

        if not sender or not receiver:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        if sender.coins < amount:

            return jsonify({
                "success": False,
                "message": "Insufficient balance"
            }), 400

        sender.coins -= amount

        receiver.coins += amount

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "Transfer successful",

            "sender_balance": sender.coins,

            "receiver_balance": receiver.coins
        })

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500
