from flask import Blueprint, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from sqlalchemy.exc import SQLAlchemyError

from models.transaction import Transaction


transaction_bp = Blueprint(
    "transaction",
    __name__
)


# =====================================================
# ================= USER TRANSACTIONS =================
# =====================================================

@transaction_bp.route(
    "/transactions",
    methods=["GET"]
)
@jwt_required()
def transaction_history():

    try:

        user_id = get_jwt_identity()

        # ================= FETCH TRANSACTIONS =================

        transactions = Transaction.query.filter_by(
            user_id=user_id
        ).order_by(
            Transaction.id.desc()
        ).limit(100).all()

        # ================= FORMAT RESPONSE =================

        data = []

        for tx in transactions:

            data.append({

                "id": tx.id,

                "type": tx.transaction_type,

                "amount": str(tx.amount),

                "balance_before":
                    str(tx.balance_before),

                "balance_after":
                    str(tx.balance_after),

                "reference_id":
                    tx.reference_id,

                "status":
                    tx.status,

                "created_at":
                    tx.created_at.isoformat()
                    if tx.created_at else None
            })

        return jsonify({

            "success": True,

            "count": len(data),

            "transactions": data
        })

    except SQLAlchemyError:

        return jsonify({

            "success": False,

            "message": "Database error"

        }), 500

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500
