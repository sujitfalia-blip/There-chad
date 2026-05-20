from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.user import User


wallet_bp = Blueprint(
    'wallet',
    __name__
)


# =========================================================
# ================= VALIDATE AMOUNT ========================
# =========================================================

def validate_amount(amount):

    try:

        amount = Decimal(str(amount))

        if amount <= 0:
            return None

        return amount.quantize(Decimal("0.01"))

    except (InvalidOperation, TypeError):
        return None


# =========================================================
# ================= SAFE GET USER ==========================
# =========================================================

def get_user(user_id):

    return db.session.query(User).filter_by(
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

        user = db.session.get(User, user_id)

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        return jsonify({

            "success": True,

            "balance": str(user.coins),

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

        data = request.get_json() or {}

        amount = validate_amount(
            data.get('amount')
        )

        target_user_id = data.get('user_id')

        if not amount:

            return jsonify({
                "success": False,
                "message": "Invalid amount"
            }), 400

        if not target_user_id:

            return jsonify({
                "success": False,
                "message": "Target user required"
            }), 400

        admin_id = get_jwt_identity()

        # ================= ADMIN LOCK =================

        admin = get_user(admin_id)

        if not admin:

            return jsonify({
                "success": False,
                "message": "Admin not found"
            }), 404

        # ================= ADMIN CHECK =================

        if admin.role not in ["admin", "super_admin"]:

            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 403

        # ================= TARGET USER =================

        user = get_user(target_user_id)

        if not user:

            return jsonify({
                "success": False,
                "message": "Target user not found"
            }), 404

        # ================= ADD COINS =================

        user.coins += amount

        user.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "Coins added successfully",

            "balance": str(user.coins)
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
# ================= DEDUCT COINS ===========================
# =========================================================

@wallet_bp.route(
    '/wallet/deduct',
    methods=['POST']
)
@jwt_required()
def deduct_coins():

    try:

        data = request.get_json() or {}

        amount = validate_amount(
            data.get('amount')
        )

        if not amount:

            return jsonify({
                "success": False,
                "message": "Invalid amount"
            }), 400

        user_id = get_jwt_identity()

        # ================= LOCK USER =================

        user = get_user(user_id)

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

            "message": "Coins deducted successfully",

            "balance": str(user.coins)
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
# ================= TRANSFER COINS =========================
# =========================================================

@wallet_bp.route(
    '/wallet/transfer',
    methods=['POST']
)
@jwt_required()
def transfer():

    try:

        data = request.get_json() or {}

        receiver_id = data.get('receiver_id')

        amount = validate_amount(
            data.get('amount')
        )

        if not receiver_id:

            return jsonify({
                "success": False,
                "message": "Receiver required"
            }), 400

        if not amount:

            return jsonify({
                "success": False,
                "message": "Invalid amount"
            }), 400

        sender_id = get_jwt_identity()

        if int(sender_id) == int(receiver_id):

            return jsonify({
                "success": False,
                "message": "Self transfer not allowed"
            }), 400

        # =================================================
        # =========== DEADLOCK SAFE LOCKING ===============
        # =================================================

        user_ids = sorted([
            int(sender_id),
            int(receiver_id)
        ])

        users = db.session.query(User).filter(
            User.id.in_(user_ids)
        ).order_by(
            User.id
        ).with_for_update().all()

        if len(users) != 2:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        sender = next(
            (u for u in users if u.id == int(sender_id)),
            None
        )

        receiver = next(
            (u for u in users if u.id == int(receiver_id)),
            None
        )

        if not sender or not receiver:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        # ================= BALANCE CHECK =================

        if sender.coins < amount:

            return jsonify({
                "success": False,
                "message": "Insufficient balance"
            }), 400

        # ================= TRANSFER =================

        sender.coins -= amount
        receiver.coins += amount

        now = datetime.utcnow()

        sender.updated_at = now
        receiver.updated_at = now

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "Transfer successful",

            "sender_balance": str(sender.coins),

            "receiver_balance": str(receiver.coins)
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
