# =========================================================
# ================= routes/betting.py =====================
# =========================================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.user import User
from models.table import Table

from game_engine.betting import (
    place_bet,
    pack_player
)

betting_bp = Blueprint(
    "betting",
    __name__
)

@betting_bp.route('/bet/place', methods=['POST'])
@jwt_required()
def bet_place():

    try:

        user_id = get_jwt_identity()

        data = request.get_json()

        table_id = data.get("table_id")
        amount = data.get("amount")
        is_seen = data.get("is_seen", False)

        user = User.query.get(user_id)
        table = Table.query.get(table_id)

        result = place_bet(
            user,
            table,
            amount,
            is_seen
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@betting_bp.route('/bet/pack', methods=['POST'])
@jwt_required()
def bet_pack():

    try:

        user_id = get_jwt_identity()

        data = request.get_json()

        table_id = data.get("table_id")

        user = User.query.get(user_id)
        table = Table.query.get(table_id)

        result = pack_player(
            user,
            table
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
