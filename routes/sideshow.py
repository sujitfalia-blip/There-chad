# =========================================================
# ================= routes/sideshow.py ====================
# =========================================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from game_engine.sideshow import (
    request_side_show,
    accept_side_show,
    reject_side_show
)

sideshow_bp = Blueprint(
    "sideshow",
    __name__
)

@sideshow_bp.route(
    '/sideshow/request',
    methods=['POST']
)
@jwt_required()
def sideshow_request():

    try:

        requester_id = get_jwt_identity()

        data = request.get_json()

        table_id = data.get("table_id")
        target_player_id = data.get(
            "target_player_id"
        )

        result = request_side_show(
            requester_id,
            target_player_id,
            table_id
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })


@sideshow_bp.route(
    '/sideshow/accept',
    methods=['POST']
)
@jwt_required()
def sideshow_accept():

    try:

        target_id = get_jwt_identity()

        data = request.get_json()

        table_id = data.get("table_id")

        result = accept_side_show(
            target_id,
            table_id
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })


@sideshow_bp.route(
    '/sideshow/reject',
    methods=['POST']
)
@jwt_required()
def sideshow_reject():

    try:

        target_id = get_jwt_identity()

        data = request.get_json()

        table_id = data.get("table_id")

        result = reject_side_show(
            target_id,
            table_id
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })
