# =========================================================
# ================= ANTI CHEAT ENGINE =====================
# ================= PRODUCTION VERSION ====================
# =========================================================

from datetime import datetime, timedelta

from extensions import (
    db,
    socketio
)

from models.user import User
from models.table import Table
from models.player_card import PlayerCard

# =========================================================
# ================= CONFIG ================================
# =========================================================

MAX_MULTI_LOGIN = 1

MAX_FAST_ACTION_SECONDS = 1

MAX_SUSPICIOUS_PACK = 5

AUTO_BAN_ENABLED = True

CHEAT_ALERT_ROOM = "super_admin"

# =========================================================
# ================= TRACK MEMORY ==========================
# =========================================================

SUSPICIOUS_ACTIVITY = {}

# =========================================================
# ================= GET USER ==============================
# =========================================================

def get_user(user_id):

    return User.query.get(user_id)

# =========================================================
# ================= INIT USER TRACK =======================
# =========================================================

def init_user_tracking(user_id):

    if user_id not in \
       SUSPICIOUS_ACTIVITY:

        SUSPICIOUS_ACTIVITY[user_id] = {

            "fast_actions": 0,

            "pack_spam": 0,

            "suspicious_score": 0,

            "last_action_time": None,

            "last_ip": None,

            "multi_login": 0
        }

# =========================================================
# ================= ADD SCORE =============================
# =========================================================

def add_suspicious_score(
    user_id,
    points,
    reason
):

    init_user_tracking(user_id)

    SUSPICIOUS_ACTIVITY[user_id][
        "suspicious_score"
    ] += points

    # ================= SOCKET ALERT =================

    socketio.emit(

        "cheat_alert",

        {

            "user_id":
                user_id,

            "reason":
                reason,

            "score":
                SUSPICIOUS_ACTIVITY[user_id][
                    "suspicious_score"
                ]
        },

        room=CHEAT_ALERT_ROOM
    )

# =========================================================
# ================= MULTI LOGIN CHECK =====================
# =========================================================

def detect_multi_login(
    user_id,
    socket_id
):

    try:

        user = get_user(user_id)

        if not user:

            return False

        init_user_tracking(user_id)

        if user.socket_id and \
           user.socket_id != socket_id:

            SUSPICIOUS_ACTIVITY[user_id][
                "multi_login"
            ] += 1

            add_suspicious_score(

                user_id,

                20,

                "Multiple login detected"
            )

            return True

        return False

    except Exception as e:

        print(
            f"MULTI LOGIN ERROR: {str(e)}"
        )

        return False

# =========================================================
# ================= FAST ACTION CHECK =====================
# =========================================================

def detect_fast_action(
    user_id
):

    try:

        init_user_tracking(user_id)

        now = datetime.utcnow()

        last_action = \
            SUSPICIOUS_ACTIVITY[user_id][
                "last_action_time"
            ]

        if last_action:

            diff = (
                now - last_action
            ).total_seconds()

            if diff <= \
               MAX_FAST_ACTION_SECONDS:

                SUSPICIOUS_ACTIVITY[user_id][
                    "fast_actions"
                ] += 1

                add_suspicious_score(

                    user_id,

                    5,

                    "Fast action spam"
                )

                return True

        SUSPICIOUS_ACTIVITY[user_id][
            "last_action_time"
        ] = now

        return False

    except Exception as e:

        print(
            f"FAST ACTION ERROR: {str(e)}"
        )

        return False

# =========================================================
# ================= PACK SPAM CHECK =======================
# =========================================================

def detect_pack_spam(
    user_id
):

    try:

        init_user_tracking(user_id)

        SUSPICIOUS_ACTIVITY[user_id][
            "pack_spam"
        ] += 1

        total = \
            SUSPICIOUS_ACTIVITY[user_id][
                "pack_spam"
            ]

        if total >= \
           MAX_SUSPICIOUS_PACK:

            add_suspicious_score(

                user_id,

                10,

                "Repeated pack abuse"
            )

            return True

        return False

    except Exception as e:

        print(
            f"PACK SPAM ERROR: {str(e)}"
        )

        return False

# =========================================================
# ================= DUPLICATE CARD CHECK ==================
# =========================================================

def detect_duplicate_cards(
    table_id
):

    try:

        cards = PlayerCard.query.filter_by(
            table_id=table_id
        ).all()

        used_cards = []

        for player in cards:

            player_cards = [

                player.card_1,
                player.card_2,
                player.card_3
            ]

            for card in player_cards:

                if card in used_cards:

                    socketio.emit(

                        "critical_cheat_alert",

                        {

                            "table_id":
                                table_id,

                            "card":
                                card,

                            "message":
                                "Duplicate card detected"
                        },

                        room=CHEAT_ALERT_ROOM
                    )

                    return True

                used_cards.append(card)

        return False

    except Exception as e:

        print(
            f"DUPLICATE CARD ERROR: {str(e)}"
        )

        return False

# =========================================================
# ================= AUTO BAN ==============================
# =========================================================

def auto_ban_user(user_id):

    try:

        user = get_user(user_id)

        if not user:

            return False

        user.is_banned = True

        user.updated_at = \
            datetime.utcnow()

        db.session.commit()

        socketio.emit(

            "user_auto_banned",

            {

                "user_id":
                    user.id,

                "username":
                    user.username
            },

            room=CHEAT_ALERT_ROOM
        )

        return True

    except Exception as e:

        db.session.rollback()

        print(
            f"AUTO BAN ERROR: {str(e)}"
        )

        return False

# =========================================================
# ================= SECURITY SCORE ========================
# =========================================================

def evaluate_user_security(
    user_id
):

    try:

        init_user_tracking(user_id)

        score = \
            SUSPICIOUS_ACTIVITY[user_id][
                "suspicious_score"
            ]

        status = "safe"

        if score >= 20:

            status = "suspicious"

        if score >= 50:

            status = "danger"

        if score >= 100:

            status = "cheater"

            if AUTO_BAN_ENABLED:

                auto_ban_user(user_id)

        return {

            "user_id":
                user_id,

            "score":
                score,

            "status":
                status
        }

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= TABLE SECURITY ========================
# =========================================================

def validate_table_security(
    table_id
):

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        duplicate_cards = \
            detect_duplicate_cards(
                table.id
            )

        return {

            "table_id":
                table.id,

            "duplicate_cards":
                duplicate_cards,

            "secure":
                not duplicate_cards
        }

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= RESET TRACK ===========================
# =========================================================

def reset_user_tracking(user_id):

    if user_id in \
       SUSPICIOUS_ACTIVITY:

        del SUSPICIOUS_ACTIVITY[
            user_id
        ]

# =========================================================
# ================= SECURITY STATUS =======================
# =========================================================

def anti_cheat_status():

    return {

        "tracked_users":
            len(SUSPICIOUS_ACTIVITY),

        "auto_ban":
            AUTO_BAN_ENABLED,

        "max_fast_action_seconds":
            MAX_FAST_ACTION_SECONDS,

        "max_pack_spam":
            MAX_SUSPICIOUS_PACK
  }
