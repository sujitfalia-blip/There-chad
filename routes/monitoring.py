from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from models.table import Table
from models.user import User
from models.game_history import GameHistory

monitoring_bp = Blueprint(
    "monitoring",
    __name__
)

# =====================================================
# ================= LIVE TABLES =======================
# =====================================================

@monitoring_bp.route(
    "/monitor/live-tables",
    methods=["GET"]
)
@jwt_required()
def live_tables():

    try:

        tables = Table.query.filter_by(
            status="running"
        ).all()

        data = []

        for table in tables:

            data.append({

                "table_id":
                    table.id,

                "boot_amount":
                    table.boot_amount,

                "players":
                    table.current_players,

                "pot":
                    float(table.current_pot),

                "status":
                    table.status
            })

        return jsonify({

            "success": True,

            "tables": data
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)
        }), 500

# =====================================================
# ================= ONLINE PLAYERS ====================
# =====================================================

@monitoring_bp.route(
    "/monitor/online-users",
    methods=["GET"]
)
@jwt_required()
def online_users():

    try:

        users = User.query.filter_by(
            is_online=True
        ).all()

        data = []

        for user in users:

            data.append({

                "user_id":
                    user.id,

                "name":
                    user.name,

                "coins":
                    float(user.coins)
            })

        return jsonify({

            "success": True,

            "online_users": data
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)
        }), 500

# =====================================================
# ================= RECENT GAMES ======================
# =====================================================

@monitoring_bp.route(
    "/monitor/recent-games",
    methods=["GET"]
)
@jwt_required()
def recent_games():

    try:

        games = GameHistory.query.order_by(
            GameHistory.id.desc()
        ).limit(50).all()

        data = []

        for game in games:

            data.append({

                "table_id":
                    game.table_id,

                "winner_id":
                    game.winner_user_id,

                "pot_amount":
                    float(game.pot_amount),

                "winner_amount":
                    float(game.winner_amount),

                "created_at":
                    str(game.created_at)
            })

        return jsonify({

            "success": True,

            "games": data
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)
        }), 500
