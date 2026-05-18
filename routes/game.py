from flask import (
    Blueprint,
    request,
    jsonify
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from sqlalchemy.exc import SQLAlchemyError

from extensions import (
    db,
    socketio
)

from models.user import User
from models.table import Table
from models.player_card import PlayerCard

from game_engine.auto_table import (
    find_or_create_table
)

from game_engine.deck import (
    DeckManager
)

# ================= BLUEPRINT =================

game_bp = Blueprint(
    'game',
    __name__
)

# ================= JOIN TABLE =================

@game_bp.route(
    '/join-table',
    methods=['POST']
)
@jwt_required()
def join_table():

    try:

        # ================= GET USER =================

        user_id = get_jwt_identity()

        user = User.query.get(user_id)

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        # ================= USER STATUS =================

        if user.is_banned:

            return jsonify({
                "success": False,
                "message": "User banned"
            }), 403

        if not user.is_active:

            return jsonify({
                "success": False,
                "message": "Account inactive"
            }), 403

        # ================= REQUEST DATA =================

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "Invalid request"
            }), 400

        boot_amount = data.get("boot")

        if not boot_amount:

            return jsonify({
                "success": False,
                "message": "Boot amount required"
            }), 400

        # ================= VALID BOOT =================

        allowed_boots = [
            1, 2, 5, 10,
            20, 50, 100
        ]

        if boot_amount not in allowed_boots:

            return jsonify({
                "success": False,
                "message": "Invalid table limit"
            }), 400

        # ================= WALLET CHECK =================

        if user.coins < boot_amount:

            return jsonify({
                "success": False,
                "message": "Insufficient balance"
            }), 400

        # ================= ALREADY IN TABLE =================

        if user.current_table_id:

            return jsonify({
                "success": False,
                "message": "Already in active table"
            }), 400

        # ================= FIND TABLE =================

        table = find_or_create_table(
            boot_amount
        )

        if not table:

            return jsonify({
                "success": False,
                "message": "Table unavailable"
            }), 500

        # ================= TABLE CHECK =================

        if table.is_locked:

            return jsonify({
                "success": False,
                "message": "Table locked"
            }), 403

        if table.current_players >= table.max_players:

            return jsonify({
                "success": False,
                "message": "Table full"
            }), 400

        # ================= UPDATE TABLE =================

        table.current_players += 1

        table.active_players += 1

        # ================= USER UPDATE =================

        user.current_table_id = table.id

        # ================= DEAL CARDS =================

        deck = DeckManager()

        cards = deck.deal_cards(
            player_id=user.id
        )

        # ================= SAVE PLAYER CARDS =================

        player_cards = PlayerCard(

            table_id=table.id,

            player_id=user.id,

            card_1=cards[0],

            card_2=cards[1],

            card_3=cards[2]
        )

        db.session.add(player_cards)

        # ================= SAVE =================

        db.session.commit()

        # ================= REALTIME UPDATE =================

        socketio.emit(

            'player_joined',

            {
                "user_id": user.id,
                "table_id": table.id,
                "players": table.current_players
            },

            room=f"table_{table.id}"
        )

        # ================= AUTO START =================

        if table.current_players >= 2:

            table.status = "running"

            db.session.commit()

            socketio.emit(

                'game_started',

                {
                    "table_id": table.id
                },

                room=f"table_{table.id}"
            )

        # ================= RESPONSE =================

        return jsonify({

            "success": True,

            "message": "Joined successfully",

            "table": {

                "id": table.id,

                "boot_amount": table.boot_amount,

                "players": table.current_players,

                "status": table.status
            },

            "cards": cards
        })

    # ================= DATABASE ERROR =================

    except SQLAlchemyError as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Database error",
            "error": str(e)
        }), 500

    # ================= GENERAL ERROR =================

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Server error",
            "error": str(e)
        }), 500
