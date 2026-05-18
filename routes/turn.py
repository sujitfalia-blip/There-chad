# =========================================================
# ================= routes/turn.py ========================
# =========================================================

from flask import Blueprint, jsonify

from game_engine.turn_manager import (
    get_current_turn
)

turn_bp = Blueprint(
    "turn",
    __name__
)

@turn_bp.route(
    '/turn/current/<int:table_id>',
    methods=['GET']
)
def current_turn(table_id):

    try:

        result = get_current_turn(
            table_id
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })
