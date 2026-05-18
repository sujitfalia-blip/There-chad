# =========================================================
# ================= routes/showdown.py ====================
# =========================================================

from flask import Blueprint, jsonify

from game_engine.showdown import (
    showdown_result
)

showdown_bp = Blueprint(
    "showdown",
    __name__
)

@showdown_bp.route(
    '/showdown/result/<int:table_id>',
    methods=['GET']
)
def showdown(table_id):

    try:

        result = showdown_result(
            table_id
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })
