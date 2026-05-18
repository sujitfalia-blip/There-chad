# =========================================================
# ================= routes/winner.py ======================
# =========================================================

from flask import Blueprint, request, jsonify

from game_engine.winner import (
    distribute_winning_amount
)

winner_bp = Blueprint(
    "winner",
    __name__
)

@winner_bp.route(
    '/winner/distribute',
    methods=['POST']
)
def winner_distribute():

    try:

        data = request.get_json()

        table_id = data.get("table_id")
        admin_user_id = data.get(
            "admin_user_id"
        )

        result = distribute_winning_amount(
            table_id,
            admin_user_id
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })
