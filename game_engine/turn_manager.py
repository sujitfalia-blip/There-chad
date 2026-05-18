# =========================================================
# ================= TURN MANAGER ENGINE ===================
# ================= PRODUCTION VERSION ====================
# =========================================================

from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

from extensions import (
    db,
    socketio
)

from models.table import Table
from models.player_card import PlayerCard
from models.user import User

# =========================================================
# ================= CONFIG ================================
# =========================================================

TURN_TIME_SECONDS = 50

WARNING_TIME_LEFT = 20

AUTO_PACK_AFTER = 50

# =========================================================
# ================= GET ACTIVE PLAYERS ====================
# =========================================================

def get_active_players(table_id):

    """
    Get all active non-packed players
    """

    return PlayerCard.query.filter_by(
        table_id=table_id,
        is_packed=False
    ).order_by(
        PlayerCard.id.asc()
    ).all()


# =========================================================
# ================= GET CURRENT TURN ======================
# =========================================================

def get_current_turn_player(table):

    """
    Current turn player
    """

    if not table.current_turn_player_id:

        return None

    return PlayerCard.query.filter_by(

        table_id=table.id,
        player_id=table.current_turn_player_id

    ).first()


# =========================================================
# ================= START TURN ============================
# =========================================================

def start_turn(
    table_id,
    player_id
):

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        player = PlayerCard.query.filter_by(

            table_id=table.id,
            player_id=player_id

        ).first()

        if not player:

            raise Exception(
                "Player not found"
            )

        # ================= TURN UPDATE =================

        table.current_turn_player_id = \
            player.player_id

        table.turn_started_at = \
            datetime.utcnow()

        table.turn_ends_at = \
            datetime.utcnow() + timedelta(
                seconds=TURN_TIME_SECONDS
            )

        player.is_turn_active = True

        player.last_action = "turn_started"

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "turn_started",

            {

                "table_id":
                    table.id,

                "player_id":
                    player.player_id,

                "turn_time":
                    TURN_TIME_SECONDS,

                "warning_after":
                    TURN_TIME_SECONDS -
                    WARNING_TIME_LEFT
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "player_id":
                player.player_id
        }

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= NEXT TURN =============================
# =========================================================

def move_to_next_turn(table_id):

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        players = get_active_players(
            table.id
        )

        if len(players) <= 1:

            return {

                "success": False,

                "message":
                    "Game ending"
            }

        current_player_id = \
            table.current_turn_player_id

        current_index = 0

        # ================= FIND CURRENT =================

        for index, player in enumerate(players):

            if player.player_id == \
               current_player_id:

                current_index = index
                break

        # ================= NEXT INDEX =================

        next_index = (
            current_index + 1
        ) % len(players)

        next_player = players[next_index]

        # ================= RESET OLD =================

        old_player = PlayerCard.query.filter_by(

            table_id=table.id,
            player_id=current_player_id

        ).first()

        if old_player:

            old_player.is_turn_active = False

        # ================= START NEW =================

        return start_turn(

            table.id,
            next_player.player_id
        )

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= TURN WARNING ==========================
# =========================================================

def send_turn_warning(table_id):

    """
    Send 20 sec remaining warning
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            return

        if not table.current_turn_player_id:

            return

        socketio.emit(

            "turn_warning",

            {

                "table_id":
                    table.id,

                "player_id":
                    table.current_turn_player_id,

                "remaining_time":
                    WARNING_TIME_LEFT
            },

            room=f"table_{table.id}"
        )

    except Exception as e:

        raise Exception(str(e))


# =========================================================
# ================= AUTO PACK PLAYER ======================
# =========================================================

def auto_pack_timeout_player(table_id):

    """
    Auto pack after timeout
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        player_id = \
            table.current_turn_player_id

        if not player_id:

            raise Exception(
                "No active turn"
            )

        player = PlayerCard.query.filter_by(

            table_id=table.id,
            player_id=player_id

        ).first()

        if not player:

            raise Exception(
                "Player not found"
            )

        # ================= PACK =================

        player.is_packed = True

        player.is_turn_active = False

        player.last_action = \
            "timeout_auto_pack"

        player.updated_at = \
            datetime.utcnow()

        table.active_players -= 1

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "auto_packed",

            {

                "table_id":
                    table.id,

                "player_id":
                    player.player_id
            },

            room=f"table_{table.id}"
        )

        # ================= NEXT TURN =================

        return move_to_next_turn(
            table.id
        )

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= CHECK TURN EXPIRED ====================
# =========================================================

def is_turn_expired(table):

    """
    Check timer expired
    """

    if not table.turn_ends_at:

        return False

    return datetime.utcnow() >= \
        table.turn_ends_at


# =========================================================
# ================= FORCE SKIP TURN =======================
# =========================================================

def admin_force_skip_turn(table_id):

    """
    Admin manual skip
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        old_player_id = \
            table.current_turn_player_id

        result = move_to_next_turn(
            table.id
        )

        socketio.emit(

            "turn_skipped",

            {

                "table_id":
                    table.id,

                "old_player_id":
                    old_player_id
            },

            room=f"table_{table.id}"
        )

        return result

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= TURN STATUS ===========================
# =========================================================

def turn_status(table_id):

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        remaining = 0

        if table.turn_ends_at:

            remaining = max(

                0,

                int(
                    (
                        table.turn_ends_at -
                        datetime.utcnow()
                    ).total_seconds()
                )
            )

        return {

            "success": True,

            "table_id":
                table.id,

            "current_turn_player_id":
                table.current_turn_player_id,

            "remaining_seconds":
                remaining,

            "turn_started_at":
                str(table.turn_started_at)
                if table.turn_started_at
                else None,

            "turn_ends_at":
                str(table.turn_ends_at)
                if table.turn_ends_at
                else None
        }

    except Exception as e:

        raise Exception(str(e))


# =========================================================
# ================= RESET TURN SYSTEM =====================
# =========================================================

def reset_turn_system(table_id):

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        table.current_turn_player_id = None

        table.turn_started_at = None

        table.turn_ends_at = None

        players = PlayerCard.query.filter_by(
            table_id=table.id
        ).all()

        for player in players:

            player.is_turn_active = False

        db.session.commit()

        socketio.emit(

            "turn_reset",

            {
                "table_id":
                    table.id
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "message":
                "Turn system reset"
        }

    except SQLAlchemyError as e:

        db.session.rollback()

        raise Exception(
            f"Database error: {str(e)}"
        )

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))
