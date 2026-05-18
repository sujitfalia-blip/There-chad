from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from models.admin_earning import AdminEarning

commission_bp = Blueprint(
    "commission",
    __name__
)

# =====================================================
# ================= ADMIN COMMISSION ==================
# =====================================================

@commission_bp.route(
    "/commission/history",
    methods=["GET"]
)
@jwt_required()
def commission_history():

    try:

        earnings = AdminEarning.query.order_by(
            AdminEarning.id.desc()
        ).limit(100).all()

        data = []

        for item in earnings:

            data.append({

                "table_id":
                    item.table_id,

                "amount":
                    float(item.amount),

                "commission_percent":
                    item.commission_percent,

                "created_at":
                    str(item.created_at)
            })

        return jsonify({

            "success": True,

            "commission_history": data
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)
        }), 500
