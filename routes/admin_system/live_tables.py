from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from sqlalchemy.orm import joinedload

from extensions import db

from models.user import User
from models.table import Table
from models.player_card import PlayerCard

# ================= BLUEPRINT =================

admin_bp = Blueprint(
    'admin',
    __name__
)

# ================= LIVE CARD MONITOR =================

@admin_bp.route(
    '/live-cards/<int:table_id>',
    methods=['GET']
)
@jwt_required()
def live_cards(table_id):

    try:

        # ================= CURRENT USER =================

        current_user_id = get_jwt_identity()

        admin = User.query.get(
            current_user_id
        )

        # ================= ADMIN CHECK =================

        if not admin:

            return jsonify({
                "success": False,
                "message": "Admin not found"
            }), 404

        # ================= ROLE CHECK =================

        allowed_roles = [
            "super_admin",
            "admin"
        ]

        if admin.role not in allowed_roles:

            return jsonify({
                "success": False,
                "message": "Unauthorized access"
            }), 403

        # ================= TABLE =================

        table = Table.query.get(table_id)

        if not table:

            return jsonify({
                "success": False,
                "message": "Table not found"
            }), 404

        # ================= ADMIN MONITOR ENABLE =================

        if not table.admin_monitoring:

            return jsonify({
                "success": False,
                "message": "Monitoring disabled"
            }), 403

        # ================= GET PLAYERS =================

        cards = PlayerCard.query.options(

            joinedload('*')

        ).filter_by(

            table_id=table_id

        ).all()

        # ================= RESPONSE DATA =================

        players = []

        for c in cards:

            user = User.query.get(
                c.player_id
            )

            players.append({

                # ================= PLAYER =================

                "player_id": c.player_id,

                "username": user.username
                if user else None,

                "name": user.name
                if user else None,

                "profile_photo": user.profile_photo
                if user else None,

                # ================= CARDS =================

                "cards": [

                    c.card_1,
                    c.card_2,
                    c.card_3
                ],

                # ================= GAME STATUS =================

                "is_seen": c.is_seen,

                "is_packed": c.is_packed,

                "is_winner": c.is_winner,

                "is_active": c.is_active,

                # ================= BETTING =================

                "blind_count": c.blind_count,

                "current_blind_amount":
                    c.current_blind_amount,

                "current_seen_amount":
                    c.current_seen_amount,

                "total_bet_amount":
                    c.total_bet_amount,

                # ================= GAMEPLAY =================

                "seat_position":
                    c.seat_position,

                "turn_number":
                    c.turn_number,

                "side_show_requested":
                    c.side_show_requested,

                "last_action":
                    c.last_action,

                # ================= SECURITY =================

                "suspicious_activity":
                    c.suspicious_activity,

                # ================= TIMESTAMPS =================

                "updated_at":
                    str(c.updated_at)
            })

        # ================= TABLE DATA =================

        table_data = {

            "table_id": table.id,

            "table_name": table.table_name,

            "boot_amount": table.boot_amount,

            "current_pot": table.current_pot,

            "status": table.status,

            "current_players":
                table.current_players,

            "active_players":
                table.active_players,

            "current_turn":
                table.current_turn,

            "dealer_position":
                table.dealer_position,

            "game_round":
                table.game_round,

            "voice_enabled":
                table.voice_enabled,

            "is_locked":
                table.is_locked
        }

        # ================= FINAL RESPONSE =================

        return jsonify({

            "success": True,

            "message":
                "Live cards fetched successfully",

            "table": table_data,

            "players": players
        })

    # ================= ERROR =================

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": "Server error",

            "error": str(e)

        }), 500
