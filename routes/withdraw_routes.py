# =========================================================
# ================= WITHDRAW ROUTES =======================
# ================= PRODUCTION VERSION ====================
# =========================================================

from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from sqlalchemy.exc import SQLAlchemyError

from extensions import db

from models.user import User
from models.transaction import Transaction
from models.withdrawal import Withdrawal


withdraw_bp = Blueprint(
    "withdraw",
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

        return amount.quantize(
            Decimal("0.01")
        )

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
# ================= CREATE WITHDRAW ========================
# =========================================================

@withdraw_bp.route(
    "/withdraw/request",
    methods=["POST"]
)
@jwt_required()
def create_withdraw():

    try:

        data = request.get_json() or {}

        amount = validate_amount(
            data.get("amount")
        )

        payment_method = (
            data.get("payment_method") or ""
        ).strip()

        account_number = (
            data.get("account_number") or ""
        ).strip()

        account_name = (
            data.get("account_name") or ""
        ).strip()

        # =================================================
        # ================= VALIDATION ====================
        # =================================================

        if not amount:

            return jsonify({

                "success": False,
                "message": "Invalid amount"

            }), 400

        if amount < Decimal("100.00"):

            return jsonify({

                "success": False,
                "message": "Minimum withdraw is 100"

            }), 400

        if not payment_method:

            return jsonify({

                "success": False,
                "message": "Payment method required"

            }), 400

        if not account_number:

            return jsonify({

                "success": False,
                "message": "Account number required"

            }), 400

        user_id = get_jwt_identity()

        # =================================================
        # ================= LOCK USER =====================
        # =================================================

        user = get_user(user_id)

        if not user:

            return jsonify({

                "success": False,
                "message": "User not found"

            }), 404

        # =================================================
        # ================= BALANCE CHECK =================
        # =================================================

        if user.coins < amount:

            return jsonify({

                "success": False,
                "message": "Insufficient balance"

            }), 400

        # =================================================
        # ================= PENDING CHECK =================
        # =================================================

        pending_count = Withdrawal.query.filter_by(
            user_id=user.id,
            status="pending"
        ).count()

        if pending_count >= 3:

            return jsonify({

                "success": False,
                "message": "Too many pending withdrawals"

            }), 400

        # =================================================
        # ================= DEDUCT BALANCE ================
        # =================================================

        before_balance = user.coins

        user.coins -= amount

        after_balance = user.coins

        user.updated_at = datetime.utcnow()

        # =================================================
        # ================= CREATE WITHDRAW ===============
        # =================================================

        withdrawal = Withdrawal(

            user_id=user.id,

            amount=amount,

            payment_method=payment_method,

            account_number=account_number,

            account_name=account_name,

            status="pending"
        )

        db.session.add(withdrawal)

        db.session.flush()

        # =================================================
        # ================= TRANSACTION LOG ===============
        # =================================================

        transaction = Transaction(

            user_id=user.id,

            transaction_type="withdraw",

            amount=amount,

            before_balance=before_balance,

            after_balance=after_balance,

            reference_id=str(withdrawal.id),

            status="pending",

            remark="Withdraw request created"
        )

        db.session.add(transaction)

        db.session.commit()

        return jsonify({

            "success": True,

            "message":
                "Withdrawal request submitted",

            "withdrawal":
                withdrawal.to_dict()
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
# ================= USER WITHDRAWALS ======================
# =========================================================

@withdraw_bp.route(
    "/withdraw/history",
    methods=["GET"]
)
@jwt_required()
def withdraw_history():

    try:

        user_id = get_jwt_identity()

        withdrawals = Withdrawal.query.filter_by(
            user_id=user_id
        ).order_by(
            Withdrawal.id.desc()
        ).limit(100).all()

        return jsonify({

            "success": True,

            "withdrawals": [

                w.to_dict()

                for w in withdrawals
            ]
        })

    except Exception as e:

        return jsonify({

            "success": False,
            "message": str(e)

        }), 500
