# =========================================================
# ================= routes/timer.py =======================
# =========================================================

from flask import Blueprint, jsonify

from game_engine.timer import (
    get_timer_status
)

timer_bp = Blueprint(
    "timer",
    __name__
)

@timer_bp.route(
    '/timer/status/<int:table_id>',
    methods=['GET']
)
def timer_status(table_id):

    try:

        result = get_timer_status(
            table_id
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })
