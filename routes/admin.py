from datetime import datetime

from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from sqlalchemy import desc

from extensions import (
    db,
    socketio
)

from models.user import User
from models.table import Table
from models.player_card import PlayerCard

# ================= BLUEPRINT =================

admin_bp = Blueprint(
    'admin',
    __name__
)

# ================= ADMIN AUTH =================

def admin_access():

    user_id = get_jwt_identity()

    admin = User.query.get(user_id)

    if not admin:

        return None

    allowed_roles = [
        "super_admin",
        "admin",
        "owner"
    ]

    if admin.role not in allowed_roles:

        return None

    return admin

# =========================================================
# ================= DASHBOARD =============================
# =========================================================

@admin_bp.route(
    '/admin/dashboard',
    methods=['GET']
)
@jwt_required()
def dashboard():

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    total_users = User.query.count()

    online_users = User.query.filter_by(
        is_online=True
    ).count()

    total_tables = Table.query.count()

    running_tables = Table.query.filter_by(
        status="running"
    ).count()

    return jsonify({

        "success": True,

        "dashboard": {

            "total_users": total_users,

            "online_users": online_users,

            "total_tables": total_tables,

            "running_tables": running_tables
        }
    })

# =========================================================
# ================= LIVE TABLES ===========================
# =========================================================

@admin_bp.route(
    '/admin/live-tables',
    methods=['GET']
)
@jwt_required()
def live_tables():

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    tables = Table.query.order_by(
        desc(Table.id)
    ).all()

    data = []

    for table in tables:

        data.append({

            "table_id": table.id,

            "table_name": table.table_name,

            "boot_amount": table.boot_amount,

            "status": table.status,

            "players": table.current_players,

            "pot": table.current_pot,

            "locked": table.is_locked
        })

    return jsonify({

        "success": True,

        "tables": data
    })

# =========================================================
# ================= LIVE CARDS ============================
# =========================================================

@admin_bp.route(
    '/admin/live-cards/<int:table_id>',
    methods=['GET']
)
@jwt_required()
def live_cards(table_id):

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    cards = PlayerCard.query.filter_by(
        table_id=table_id
    ).all()

    data = []

    for c in cards:

        user = User.query.get(c.player_id)

        data.append({

            "player_id": c.player_id,

            "username":
                user.username if user else None,

            "cards": [

                c.card_1,
                c.card_2,
                c.card_3
            ],

            "is_seen": c.is_seen,

            "is_packed": c.is_packed,

            "bet_amount":
                c.total_bet_amount
        })

    return jsonify({

        "success": True,

        "cards": data
    })

# =========================================================
# ================= LOCK TABLE ============================
# =========================================================

@admin_bp.route(
    '/admin/lock-table/<int:table_id>',
    methods=['POST']
)
@jwt_required()
def lock_table(table_id):

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    table = Table.query.get(table_id)

    if not table:

        return jsonify({
            "success": False,
            "message": "Table not found"
        }), 404

    table.is_locked = True

    db.session.commit()

    socketio.emit(

        'table_locked',

        {
            "table_id": table.id
        },

        room=f"table_{table.id}"
    )

    return jsonify({

        "success": True,

        "message": "Table locked"
    })

# =========================================================
# ================= UNLOCK TABLE ==========================
# =========================================================

@admin_bp.route(
    '/admin/unlock-table/<int:table_id>',
    methods=['POST']
)
@jwt_required()
def unlock_table(table_id):

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    table = Table.query.get(table_id)

    if not table:

        return jsonify({
            "success": False,
            "message": "Table not found"
        }), 404

    table.is_locked = False

    db.session.commit()

    socketio.emit(

        'table_unlocked',

        {
            "table_id": table.id
        },

        room=f"table_{table.id}"
    )

    return jsonify({

        "success": True,

        "message": "Table unlocked"
    })

# =========================================================
# ================= KICK PLAYER ===========================
# =========================================================

@admin_bp.route(
    '/admin/kick-player',
    methods=['POST']
)
@jwt_required()
def kick_player():

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    player_id = data.get('player_id')

    user = User.query.get(player_id)

    if not user:

        return jsonify({
            "success": False,
            "message": "Player not found"
        }), 404

    table_id = user.current_table_id

    user.current_table_id = None

    db.session.commit()

    socketio.emit(

        'player_kicked',

        {
            "player_id": player_id
        },

        room=f"table_{table_id}"
    )

    return jsonify({

        "success": True,

        "message": "Player kicked"
    })

# =========================================================
# ================= BAN PLAYER ============================
# =========================================================

@admin_bp.route(
    '/admin/ban-player',
    methods=['POST']
)
@jwt_required()
def ban_player():

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    player_id = data.get('player_id')

    user = User.query.get(player_id)

    if not user:

        return jsonify({
            "success": False,
            "message": "Player not found"
        }), 404

    user.is_banned = True

    db.session.commit()

    return jsonify({

        "success": True,

        "message": "Player banned"
    })

# =========================================================
# ================= UNBAN PLAYER ==========================
# =========================================================

@admin_bp.route(
    '/admin/unban-player',
    methods=['POST']
)
@jwt_required()
def unban_player():

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    player_id = data.get('player_id')

    user = User.query.get(player_id)

    if not user:

        return jsonify({
            "success": False,
            "message": "Player not found"
        }), 404

    user.is_banned = False

    db.session.commit()

    return jsonify({

        "success": True,

        "message": "Player unbanned"
    })

# =========================================================
# ================= FORCE WINNER ==========================
# =========================================================

@admin_bp.route(
    '/admin/force-winner',
    methods=['POST']
)
@jwt_required()
def force_winner():

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    table_id = data.get('table_id')

    winner_id = data.get('winner_id')

    table = Table.query.get(table_id)

    if not table:

        return jsonify({
            "success": False,
            "message": "Table not found"
        }), 404

    table.winner_user_id = winner_id

    table.status = "finished"

    db.session.commit()

    socketio.emit(

        'winner_declared',

        {
            "table_id": table.id,
            "winner_id": winner_id
        },

        room=f"table_{table.id}"
    )

    return jsonify({

        "success": True,

        "message": "Winner forced"
    })

# =========================================================
# ================= SERVER STATUS =========================
# =========================================================

@admin_bp.route(
    '/admin/server-status',
    methods=['GET']
)
@jwt_required()
def server_status():

    admin = admin_access()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    return jsonify({

        "success": True,

        "server": {

            "status": "running",

            "time":
                str(datetime.utcnow()),

            "socket": "active",

            "database": "connected"
        }
    })
