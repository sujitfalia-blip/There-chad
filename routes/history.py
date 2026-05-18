# =========================================================
# ================= routes/history.py =====================
# =========================================================

from flask import Blueprint, jsonify

from models.game_history import GameHistory

history_bp = Blueprint(
    "history",
    __name__
)

@history_bp.route(
    '/history/games',
    methods=['GET']
)
def game_history():

    try:

        games = GameHistory.query.order_by(
            GameHistory.id.desc()
        ).limit(50).all()

        return jsonify({

            "success": True,

            "games": [

                game.to_dict()
                for game in games
            ]
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })
