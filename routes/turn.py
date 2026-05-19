# =========================================================
# ================= routes/turn.py ========================
# =========================================================

from flask import Blueprint, jsonify

from game_engine.turn_manager import get_current_turn_player

turn_bp = Blueprint("turn", __name__)

# =========================================================
# ================= CURRENT TURN ==========================
# =========================================================

@turn_bp.route('/turn/current/<int:table_id>', methods=['GET'])
def current_turn(table_id):

    try:
        # এখানে Table object লাগবে, তাই আগে table fetch করতে হবে
        from models.table import Table

        table = Table.query.get(table_id)

        if not table:
            return jsonify({
                "success": False,
                "message": "Table not found"
            }), 404

        player = get_current_turn_player(table)

        if not player:
            return jsonify({
                "success": True,
                "current_player": None
            })

        return jsonify({
            "success": True,
            "current_player": {
                "player_id": player.player_id,
                "is_turn_active": player.is_turn_active
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
