# =========================================================
# ================= TEEN PATTI BETTING ENGINE ==============
# ================= PRODUCTION VERSION ====================
# =========================================================

from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from extensions import (
    db,
    socketio
)

from models.user import User
from models.table import Table
from models.player_card import PlayerCard

from game_engine.rules import compare_hands

# =========================================================
# ================= GAME CONFIG ============================
# =========================================================

TURN_TIME_SECONDS = 50

WARNING_TIME_SECONDS = 20

SIDE_SHOW_MIN_PLAYERS = 2

COMMISSION_PERCENT = 5

BLIND_MULTIPLIER = 1

SEEN_MULTIPLIER = 2

# =========================================================
# ================= GET PLAYER =============================
# =========================================================

def get_player(table_id, player_id):

    return PlayerCard.query.filter_by(
        table_id=table_id,
        player_id=player_id
    ).first()


# =========================================================
# ================= VALIDATE BET ===========================
# =========================================================

def validate_bet_amount(
    amount,
    boot_amount,
    is_seen
):

    if amount <= 0:
        return False

    minimum = (
        boot_amount * SEEN_MULTIPLIER
        if is_seen
        else boot_amount * BLIND_MULTIPLIER
    )

    return amount >= minimum


# =========================================================
# ================= PLACE BET ==============================
# =========================================================

def place_bet(
    user_id,
    table_id,
    amount,
    is_seen=False
):

    try:

        # ================= USER =================

        user = User.query.filter_by(
            id=user_id
        ).with_for_update().first()

        if not user:

            raise Exception(
                "User not found"
            )

        # ================= TABLE =================

        table = Table.query.filter_by(
            id=table_id
        ).with_for_update().first()

        if not table:

            raise Exception(
                "Table not found"
            )

        # ================= PLAYER =================

        player = get_player(
            table.id,
            user.id
        )

        if not player:

            raise Exception(
                "Player not found"
            )

        # ================= PACK CHECK =================

        if player.is_packed:

            raise Exception(
                "Packed player cannot bet"
            )

        # ================= VALIDATE BET =================

        if not validate_bet_amount(
            amount,
            table.boot_amount,
            is_seen
        ):

            raise Exception(
                "Invalid betting amount"
            )

        # ================= BALANCE =================

        if user.coins < amount:

            raise Exception(
                "Insufficient balance"
            )

        # ================= DEDUCT =================

        user.coins -= amount

        # ================= UPDATE TABLE =================

        table.current_pot += amount

        # ================= UPDATE PLAYER =================

        player.total_bet_amount += amount

        player.last_action = "bet"

        player.is_seen = is_seen

        player.updated_at = datetime.utcnow()

        db.session.commit()

        # ================= SOCKET EVENT =================

        socketio.emit(

            "player_bet",

            {
                "player_id": user.id,
                "table_id": table.id,
                "amount": amount,
                "pot": table.current_pot
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "message": "Bet placed",

            "pot": table.current_pot,

            "balance": user.coins
        }

    except SQLAlchemyError as e:

        db.session.rollback()

        raise Exception(
            f"Database error: {str(e)}"
        )

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= PACK PLAYER ============================
# =========================================================

def pack_player(
    user_id,
    table_id
):

    try:

        player = get_player(
            table_id,
            user_id
        )

        if not player:

            raise Exception(
                "Player not found"
            )

        if player.is_packed:

            raise Exception(
                "Already packed"
            )

        table = Table.query.get(table_id)

        player.is_packed = True

        player.last_action = "packed"

        table.active_players -= 1

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "player_packed",

            {
                "player_id": user_id,
                "table_id": table_id
            },

            room=f"table_{table_id}"
        )

        return {

            "success": True,

            "message": "Player packed"
        }

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= SIDE SHOW REQUEST ======================
# =========================================================

def request_side_show(
    requester_id,
    target_player_id,
    table_id
):

    requester = get_player(
        table_id,
        requester_id
    )

    target = get_player(
        table_id,
        target_player_id
    )

    if not requester or not target:

        raise Exception(
            "Player not found"
        )

    # ================= ONLY SEEN =================

    if not requester.is_seen:

        raise Exception(
            "Blind player cannot request side show"
        )

    # ================= TARGET CHECK =================

    if target.is_packed:

        raise Exception(
            "Target player packed"
        )

    # ================= SOCKET =================

    socketio.emit(

        "side_show_request",

        {
            "requester_id": requester_id,
            "target_id": target_player_id
        },

        room=f"table_{table_id}"
    )

    return {

        "success": True,

        "message": "Side show request sent"
    }


# =========================================================
# ================= ACCEPT SIDE SHOW =======================
# =========================================================

def accept_side_show(
    player1,
    player2,
    table
):

    result = compare_hands(
        [
            player1.card_1,
            player1.card_2,
            player1.card_3
        ],
        [
            player2.card_1,
            player2.card_2,
            player2.card_3
        ]
    )

    # ================= LOSER PACK =================

    if result == 1:

        loser = player2

    elif result == 2:

        loser = player1

    else:

        return {
            "success": True,
            "message": "Tie"
        }

    loser.is_packed = True

    loser.last_action = "side_show_lost"

    table.active_players -= 1

    db.session.commit()

    # ================= SOCKET =================

    socketio.emit(

        "side_show_result",

        {
            "loser_id": loser.player_id
        },

        room=f"table_{table.id}"
    )

    return {

        "success": True,

        "loser_id": loser.player_id
    }


# =========================================================
# ================= AUTO PACK ==============================
# =========================================================

def auto_pack_player(
    user_id,
    table_id
):

    player = get_player(
        table_id,
        user_id
    )

    if not player:

        return

    if player.is_packed:

        return

    table = Table.query.get(table_id)

    player.is_packed = True

    player.last_action = "timeout_pack"

    table.active_players -= 1

    db.session.commit()

    # ================= SOCKET =================

    socketio.emit(

        "auto_pack",

        {
            "player_id": user_id
        },

        room=f"table_{table_id}"
    )


# =========================================================
# ================= NEXT TURN ==============================
# =========================================================

def next_turn(
    current_index,
    total_players
):

    return (
        current_index + 1
    ) % total_players


# =========================================================
# ================= COMMISSION =============================
# =========================================================

def calculate_admin_commission(
    pot_amount
):

    return round(
        (pot_amount * COMMISSION_PERCENT) / 100,
        2
    )


# =========================================================
# ================= DISTRIBUTE WIN =========================
# =========================================================

def distribute_winner_amount(
    winner_user,
    admin_user,
    table
):

    try:

        total_pot = table.current_pot

        commission = calculate_admin_commission(
            total_pot
        )

        winner_amount = total_pot - commission

        # ================= CREDIT =================

        winner_user.coins += winner_amount

        admin_user.coins += commission

        # ================= TABLE RESET =================

        table.current_pot = 0

        table.status = "finished"

        table.winner_user_id = winner_user.id

        table.updated_at = datetime.utcnow()

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "winner_declared",

            {
                "winner_id": winner_user.id,
                "winner_amount": winner_amount
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "winner_amount": winner_amount,

            "commission": commission
        }

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= TURN TIMER =============================
# =========================================================

def get_turn_timer():

    return {

        "turn_time":
            TURN_TIME_SECONDS,

        "warning_after":
            TURN_TIME_SECONDS - WARNING_TIME_SECONDS,

        "auto_pack_after":
            TURN_TIME_SECONDS
    }


# =========================================================
# ================= GAME STATUS ============================
# =========================================================

def game_status(table):

    return {

        "table_id": table.id,

        "table_name":
            table.table_name,

        "boot_amount":
            table.boot_amount,

        "pot_amount":
            table.current_pot,

        "players":
            table.current_players,

        "active_players":
            table.active_players,

        "status":
            table.status,

        "locked":
            table.is_locked
    }
