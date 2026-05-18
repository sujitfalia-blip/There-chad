# =========================================================
# ================= TABLE CLEANUP ENGINE ==================
# ================= ENTERPRISE VERSION ====================
# =========================================================

import time

from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

from extensions import (
    db,
    socketio
)

from models.table import Table
from models.player_card import PlayerCard
from models.user import User

from game_engine.logger import (
    log_game_event,
    log_error
)

# =========================================================
# ================= CONFIG ================================
# =========================================================

WAITING_TABLE_EXPIRE_MINUTES = 15

FINISHED_TABLE_EXPIRE_MINUTES = 5

OFFLINE_PLAYER_TIMEOUT_SECONDS = 120

# =========================================================
# ================= DELETE PLAYER DATA ====================
# =========================================================

def remove_table_players(table_id):

    """
    Remove all player cards
    """

    try:

        PlayerCard.query.filter_by(
            table_id=table_id
        ).delete()

        db.session.flush()

        return True

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= RESET USER TABLE ======================
# =========================================================

def reset_users_from_table(table_id):

    """
    Remove current_table_id
    """

    try:

        users = User.query.filter_by(
            current_table_id=table_id
        ).all()

        for user in users:

            user.current_table_id = None

            user.updated_at = datetime.utcnow()

        db.session.flush()

        return True

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= CLEAN FINISHED TABLE ==================
# =========================================================

def cleanup_finished_tables():

    """
    Delete finished tables
    """

    try:

        expire_time = datetime.utcnow() - timedelta(
            minutes=FINISHED_TABLE_EXPIRE_MINUTES
        )

        tables = Table.query.filter(

            Table.status == "finished",

            Table.finished_at != None,

            Table.finished_at <= expire_time

        ).all()

        cleaned = 0

        for table in tables:

            remove_table_players(
                table.id
            )

            reset_users_from_table(
                table.id
            )

            db.session.delete(table)

            cleaned += 1

            log_game_event(

                "FINISHED_TABLE_REMOVED",

                {
                    "table_id": table.id
                }
            )

        db.session.commit()

        return {

            "success": True,

            "cleaned_tables": cleaned
        }

    except SQLAlchemyError as e:

        db.session.rollback()

        log_error(
            f"Cleanup DB Error: {str(e)}"
        )

        raise Exception(str(e))

# =========================================================
# ================= CLEAN WAITING TABLE ===================
# =========================================================

def cleanup_waiting_tables():

    """
    Remove old waiting tables
    """

    try:

        expire_time = datetime.utcnow() - timedelta(
            minutes=WAITING_TABLE_EXPIRE_MINUTES
        )

        tables = Table.query.filter(

            Table.status == "waiting",

            Table.current_players == 0,

            Table.created_at <= expire_time

        ).all()

        cleaned = 0

        for table in tables:

            db.session.delete(table)

            cleaned += 1

            log_game_event(

                "WAITING_TABLE_REMOVED",

                {
                    "table_id": table.id
                }
            )

        db.session.commit()

        return {

            "success": True,

            "cleaned_tables": cleaned
        }

    except Exception as e:

        db.session.rollback()

        log_error(
            f"Waiting Cleanup Error: {str(e)}"
        )

        raise Exception(str(e))

# =========================================================
# ================= REMOVE OFFLINE PLAYERS ================
# =========================================================

def cleanup_offline_players():

    """
    Auto remove offline users
    """

    try:

        expire_time = datetime.utcnow() - timedelta(
            seconds=OFFLINE_PLAYER_TIMEOUT_SECONDS
        )

        users = User.query.filter(

            User.is_online == False,

            User.current_table_id != None,

            User.updated_at <= expire_time

        ).all()

        removed = 0

        for user in users:

            table = Table.query.get(
                user.current_table_id
            )

            if table:

                player = PlayerCard.query.filter_by(

                    table_id=table.id,
                    player_id=user.id

                ).first()

                if player:

                    player.is_packed = True

                    player.last_action = \
                        "offline_removed"

                    table.active_players -= 1

                    socketio.emit(

                        "player_auto_removed",

                        {

                            "table_id":
                                table.id,

                            "player_id":
                                user.id
                        },

                        room=f"table_{table.id}"
                    )

            user.current_table_id = None

            removed += 1

        db.session.commit()

        return {

            "success": True,

            "removed_players": removed
        }

    except Exception as e:

        db.session.rollback()

        log_error(
            f"Offline Cleanup Error: {str(e)}"
        )

        raise Exception(str(e))

# =========================================================
# ================= FORCE TABLE RESET =====================
# =========================================================

def force_reset_table(table_id):

    """
    Emergency admin reset
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        # ================= RESET USERS =================

        reset_users_from_table(
            table.id
        )

        # ================= DELETE PLAYER DATA =================

        remove_table_players(
            table.id
        )

        # ================= RESET TABLE =================

        table.current_players = 0

        table.active_players = 0

        table.current_pot = 0

        table.status = "waiting"

        table.side_show_pending = False

        table.updated_at = datetime.utcnow()

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "table_force_reset",

            {
                "table_id": table.id
            },

            room=f"table_{table.id}"
        )

        log_game_event(

            "TABLE_FORCE_RESET",

            {
                "table_id": table.id
            }
        )

        return {

            "success": True,

            "message":
                "Table reset complete"
        }

    except Exception as e:

        db.session.rollback()

        log_error(
            f"Force Reset Error: {str(e)}"
        )

        raise Exception(str(e))

# =========================================================
# ================= FULL CLEANUP ==========================
# =========================================================

def run_full_cleanup():

    """
    Run all cleanup tasks
    """

    try:

        waiting = cleanup_waiting_tables()

        finished = cleanup_finished_tables()

        offline = cleanup_offline_players()

        return {

            "success": True,

            "waiting_tables":
                waiting["cleaned_tables"],

            "finished_tables":
                finished["cleaned_tables"],

            "offline_players":
                offline["removed_players"]
        }

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= CLEANUP LOOP ==========================
# =========================================================

def start_cleanup_scheduler():

    """
    Background cleanup loop
    """

    while True:

        try:

            run_full_cleanup()

        except Exception as e:

            log_error(
                f"Cleanup Scheduler Error: {str(e)}"
            )

        # ================= WAIT =================

        time.sleep(60)

# =========================================================
# ================= TABLE HEALTH ==========================
# =========================================================

def table_health_status(table_id):

    """
    Table monitoring info
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        players = PlayerCard.query.filter_by(
            table_id=table.id
        ).count()

        return {

            "table_id":
                table.id,

            "status":
                table.status,

            "players":
                players,

            "active_players":
                table.active_players,

            "pot":
                table.current_pot,

            "created_at":
                str(table.created_at),

            "updated_at":
                str(table.updated_at)
        }

    except Exception as e:

        raise Exception(str(e))
