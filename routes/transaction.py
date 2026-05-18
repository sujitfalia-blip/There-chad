from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

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

        transactions = Transaction.query.filter_by(
            user_id=user_id
        ).order_by(
            Transaction.id.desc()
        ).limit(100).all()

        data = []

        for tx in transactions:

            data.append({

                "id": tx.id,

                "type": tx.transaction_type,

                "amount": float(tx.amount),

                "balance_before":
                    float(tx.balance_before),

                "balance_after":
                    float(tx.balance_after),

                "reference_id":
                    tx.reference_id,

                "status":
                    tx.status,

                "created_at":
                    str(tx.created_at)
            })

        return jsonify({

            "success": True,

            "transactions": data
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)
        }), 500
