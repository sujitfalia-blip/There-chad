# =========================================================
# ================= ADMIN WITHDRAW ROUTES =================
# ================= PRODUCTION VERSION ====================
# =========================================================

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from sqlalchemy.exc import SQLAlchemyError

from extensions import db

from models.user import User
from models.transaction import Transaction
from models.withdrawal import Withdrawal


admin_withdraw_bp = Blueprint(
    "admin_withdraw",
    __name__
)


# =========================================================
# ================= SAFE GET USER ==========================
# =========================================================

def get_user(user_id):

    return db.session.query(User).filter_by(
        id=user_id
    ).with_for_update().first()


# =========================================================
# ================= ADMIN CHECK ============================
# =========================================================

def is_admin(user):

    return user.role in [
        "admin",
        "super_admin"
    ]


# =========================================================
# ================= APPROVE WITHDRAW ======================
# =========================================================

@admin_withdraw_bp.route(
    "/admin/withdraw/<int:withdraw_id>/approve",
    methods=["POST"]
)
@jwt_required()
def approve_withdraw(withdraw_id):

    try:

        admin_id = get_jwt_identity()

        admin = get_user(admin_id)

        if not admin or not is_admin(admin):

            return jsonify({

                "success": False,
                "message": "Unauthorized"

            }), 403

        withdrawal = db.session.query(
            Withdrawal
        ).filter_by(
            id=withdraw_id
        ).with_for_update().first()

        if not withdrawal:

            return jsonify({

                "success": False,
                "message": "Withdrawal not found"

            }), 404

        if withdrawal.status != "pending":

            return jsonify({

                "success": False,
                "message":
                    "Withdrawal already processed"

            }), 400

        withdrawal.status = "approved"

        withdrawal.updated_at = datetime.utcnow()

        transaction = Transaction.query.filter_by(
            reference_id=str(withdrawal.id),
            transaction_type="withdraw"
        ).first()

        if transaction:

            transaction.status = "completed"

        db.session.commit()

        return jsonify({

            "success": True,
            "message": "Withdrawal approved"

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
# ================= REJECT WITHDRAW =======================
# =========================================================

@admin_withdraw_bp.route(
    "/admin/withdraw/<int:withdraw_id>/reject",
    methods=["POST"]
)
@jwt_required()
def reject_withdraw(withdraw_id):

    try:

        data = request.get_json() or {}

        note = (
            data.get("note") or ""
        ).strip()

        admin_id = get_jwt_identity()

        admin = get_user(admin_id)

        if not admin or not is_admin(admin):

            return jsonify({

                "success": False,
                "message": "Unauthorized"

            }), 403

        # =================================================
        # ================= LOCK WITHDRAW =================
        # =================================================

        withdrawal = db.session.query(
            Withdrawal
        ).filter_by(
            id=withdraw_id
        ).with_for_update().first()

        if not withdrawal:

            return jsonify({

                "success": False,
                "message": "Withdrawal not found"

            }), 404

        if withdrawal.status != "pending":

            return jsonify({

                "success": False,
                "message":
                    "Withdrawal already processed"

            }), 400

        # =================================================
        # ================= REFUND USER ===================
        # =================================================

        user = get_user(
            withdrawal.user_id
        )

        before_balance = user.coins

        user.coins += withdrawal.amount

        after_balance = user.coins

        user.updated_at = datetime.utcnow()

        # =================================================
        # ================= UPDATE WITHDRAW ===============
        # =================================================

        withdrawal.status = "rejected"

        withdrawal.admin_note = note

        withdrawal.updated_at = datetime.utcnow()

        # =================================================
        # ================= UPDATE TRANSACTION ============
        # =================================================

        transaction = Transaction.query.filter_by(
            reference_id=str(withdrawal.id),
            transaction_type="withdraw"
        ).first()

        if transaction:

            transaction.status = "cancelled"

        # =================================================
        # ================= REFUND TRANSACTION ============
        # =================================================

        refund_transaction = Transaction(

            user_id=user.id,

            transaction_type="refund",

            amount=withdrawal.amount,

            before_balance=before_balance,

            after_balance=after_balance,

            reference_id=str(withdrawal.id),

            status="completed",

            remark="Withdraw rejected refund"
        )

        db.session.add(
            refund_transaction
        )

        db.session.commit()

        return jsonify({

            "success": True,
            "message":
                "Withdrawal rejected and refunded"

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
