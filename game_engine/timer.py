# =========================================================
# ================= TIMER ENGINE ==========================
# ================= PRODUCTION VERSION ====================
# =========================================================

import time
import threading

from datetime import datetime

from extensions import (
    db,
    socketio
)

from models.table import Table
from models.player_card import PlayerCard

# =========================================================
# ================= CONFIG ================================
# =========================================================

TURN_TIME_SECONDS = 50

WARNING_TIME_LEFT = 20

AUTO_PACK_ENABLED = True

# =========================================================
# ================= ACTIVE TIMERS =========================
# =========================================================

ACTIVE_TIMERS = {}

# =========================================================
# ================= GET PLAYER ============================
# =========================================================

def get_player(
    table_id,
    player_id
):

    return PlayerCard.query.filter_by(

        table_id=table_id,
        player_id=player_id

    ).first()

# =========================================================
# ================= STOP TIMER ============================
# =========================================================

def stop_timer(table_id):

    timer_data = ACTIVE_TIMERS.get(table_id)

    if not timer_data:

        return

    timer_data["running"] = False

    ACTIVE_TIMERS.pop(table_id, None)

# =========================================================
# ================= AUTO PACK =============================
# =========================================================

def auto_pack_player(
    table_id,
    player_id
):

    try:

        player = get_player(
            table_id,
            player_id
        )

        table = Table.query.get(table_id)

        if not player or not table:

            return

        if player.is_packed:

            return

        # ================= PACK =================

        player.is_packed = True

        player.last_action = \
            "timeout_auto_pack"

        player.updated_at = \
            datetime.utcnow()

        table.active_players -= 1

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "player_auto_packed",

            {

                "table_id":
                    table.id,

                "player_id":
                    player.player_id
            },

            room=f"table_{table.id}"
        )

    except Exception as e:

        db.session.rollback()

        print(
            f"AUTO PACK ERROR: {str(e)}"
        )

# =========================================================
# ================= TIMER THREAD ==========================
# =========================================================

def timer_thread(
    table_id,
    player_id
):

    try:

        start_time = time.time()

        warning_sent = False

        ACTIVE_TIMERS[table_id] = {

            "running": True,

            "player_id":
                player_id
        }

        while True:

            timer_data = ACTIVE_TIMERS.get(
                table_id
            )

            if not timer_data:

                break

            if not timer_data["running"]:

                break

            elapsed = int(
                time.time() - start_time
            )

            remaining = \
                TURN_TIME_SECONDS - elapsed

            # ================= TIMER FINISH =================

            if remaining <= 0:

                socketio.emit(

                    "turn_timeout",

                    {

                        "table_id":
                            table_id,

                        "player_id":
                            player_id
                    },

                    room=f"table_{table_id}"
                )

                if AUTO_PACK_ENABLED:

                    auto_pack_player(

                        table_id,
                        player_id
                    )

                stop_timer(table_id)

                break

            # ================= WARNING =================

            if remaining <= \
               WARNING_TIME_LEFT \
               and not warning_sent:

                warning_sent = True

                socketio.emit(

                    "turn_warning",

                    {

                        "table_id":
                            table_id,

                        "player_id":
                            player_id,

                        "seconds_left":
                            remaining
                    },

                    room=f"table_{table_id}"
                )

            # ================= LIVE TIMER =================

            socketio.emit(

                "turn_timer",

                {

                    "table_id":
                        table_id,

                    "player_id":
                        player_id,

                    "remaining":
                        remaining
                },

                room=f"table_{table_id}"
            )

            time.sleep(1)

    except Exception as e:

        print(
            f"TIMER THREAD ERROR: {str(e)}"
        )

# =========================================================
# ================= START TIMER ===========================
# =========================================================

def start_turn_timer(
    table_id,
    player_id
):

    try:

        # ================= STOP OLD =================

        stop_timer(table_id)

        # ================= THREAD =================

        thread = threading.Thread(

            target=timer_thread,

            args=(

                table_id,
                player_id
            )
        )

        thread.daemon = True

        thread.start()

        return {

            "success": True,

            "message":
                "Turn timer started",

            "table_id":
                table_id,

            "player_id":
                player_id,

            "duration":
                TURN_TIME_SECONDS
        }

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= RESET TIMER ===========================
# =========================================================

def reset_turn_timer(
    table_id,
    player_id
):

    try:

        stop_timer(table_id)

        return start_turn_timer(

            table_id,
            player_id
        )

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= TIMER STATUS ==========================
# =========================================================

def timer_status(table_id):

    timer_data = ACTIVE_TIMERS.get(
        table_id
    )

    if not timer_data:

        return {

            "running": False
        }

    return {

        "running": True,

        "player_id":
            timer_data["player_id"]
    }

# =========================================================
# ================= FORCE STOP ============================
# =========================================================

def force_stop_timer(table_id):

    try:

        stop_timer(table_id)

        socketio.emit(

            "timer_stopped",

            {
                "table_id":
                    table_id
            },

            room=f"table_{table_id}"
        )

        return {

            "success": True,

            "message":
                "Timer force stopped"
        }

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= CLEANUP ===============================
# =========================================================

def cleanup_finished_timers():

    try:

        remove_tables = []

        for table_id, timer_data in \
            ACTIVE_TIMERS.items():

            if not timer_data["running"]:

                remove_tables.append(
                    table_id
                )

        for table_id in remove_tables:

            ACTIVE_TIMERS.pop(
                table_id,
                None
            )

    except Exception as e:

        print(
            f"CLEANUP ERROR: {str(e)}"
      )

# =========================================================
# ================= TIMER STATUS ==========================
# =========================================================

def get_timer_status(table_id=None):

    """
    Current timer configuration
    """

    return {

        "success": True,

        "table_id": table_id,

        "turn_time_seconds": 50,

        "warning_time_seconds": 20,

        "auto_pack_after": 50,

        "warning_after": 30
                }
