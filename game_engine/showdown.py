# =========================================================
# ================= SHOWDOWN ENGINE =======================
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

from game_engine.rules import (
    compare_hands,
    hand_name,
    get_hand_strength
)

# =========================================================
# ================= CONFIG ================================
# =========================================================

SHOWDOWN_MIN_PLAYERS = 2

# =========================================================
# ================= GET ACTIVE PLAYERS ====================
# =========================================================

def get_active_players(table_id):

    return PlayerCard.query.filter_by(
        table_id=table_id,
        is_packed=False
    ).all()


# =========================================================
# ================= PLAYER CARDS ==========================
# =========================================================

def player_cards(player):

    return [

        player.card_1,
        player.card_2,
        player.card_3
    ]


# =========================================================
# ================= VALIDATE SHOWDOWN =====================
# =========================================================

def validate_showdown(table):

    """
    Showdown allowed only if:
    - game running
    - minimum 2 players active
    """

    if not table:

        raise Exception(
            "Table not found"
        )

    if table.status != "running":

        raise Exception(
            "Game not running"
        )

    active_players = get_active_players(
        table.id
    )

    if len(active_players) < \
       SHOWDOWN_MIN_PLAYERS:

        raise Exception(
            "Not enough players"
        )

    return True


# =========================================================
# ================= COMPARE ALL PLAYERS ===================
# =========================================================

def compare_all_players(players):

    """
    Find strongest hand
    """

    winner = players[0]

    for challenger in players[1:]:

        result = compare_hands(

            player_cards(winner),

            player_cards(challenger)
        )

        if result == 2:

            winner = challenger

    return winner


# =========================================================
# ================= START SHOWDOWN ========================
# =========================================================

def start_showdown(table_id):

    try:

        # ================= TABLE =================

        table = Table.query.filter_by(
            id=table_id
        ).with_for_update().first()

        if not table:

            raise Exception(
                "Table not found"
            )

        # ================= VALIDATE =================

        validate_showdown(table)

        # ================= PLAYERS =================

        active_players = get_active_players(
            table.id
        )

        # ================= WINNER =================

        winner_player = compare_all_players(
            active_players
        )

        winner_user = User.query.get(
            winner_player.player_id
        )

        if not winner_user:

            raise Exception(
                "Winner user not found"
            )

        # ================= UPDATE WINNER =================

        winner_player.is_winner = True

        winner_player.win_amount = \
            table.current_pot

        winner_player.updated_at = \
            datetime.utcnow()

        # ================= TABLE UPDATE =================

        table.status = "showdown"

        table.winner_user_id = \
            winner_user.id

        table.finished_at = \
            datetime.utcnow()

        # ================= RESULT =================

        showdown_players = []

        for player in active_players:

            user = User.query.get(
                player.player_id
            )

            cards = player_cards(player)

            showdown_players.append({

                "player_id":
                    player.player_id,

                "player_name":
                    user.name if user
                    else None,

                "cards":
                    cards,

                "hand":
                    hand_name(cards),

                "strength":
                    get_hand_strength(cards),

                "is_winner":
                    player.player_id ==
                    winner_player.player_id
            })

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "showdown_started",

            {

                "table_id":
                    table.id,

                "winner_id":
                    winner_user.id,

                "winner_name":
                    winner_user.name,

                "pot_amount":
                    table.current_pot,

                "players":
                    showdown_players
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "winner_id":
                winner_user.id,

            "winner_name":
                winner_user.name,

            "showdown_players":
                showdown_players
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
# ================= MANUAL SHOWDOWN =======================
# =========================================================

def manual_showdown(
    requester_id,
    table_id
):

    """
    Player requested showdown
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        requester = PlayerCard.query.filter_by(

            table_id=table.id,
            player_id=requester_id

        ).first()

        if not requester:

            raise Exception(
                "Requester not found"
            )

        if requester.is_packed:

            raise Exception(
                "Packed player cannot showdown"
            )

        requester.last_action = \
            "manual_showdown"

        requester.updated_at = \
            datetime.utcnow()

        db.session.commit()

        return start_showdown(
            table.id
        )

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= AUTO SHOWDOWN =========================
# =========================================================

def auto_showdown_if_needed(table_id):

    """
    Auto showdown if only 2 players left
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            return {

                "auto_showdown": False
            }

        active_players = get_active_players(
            table.id
        )

        if len(active_players) == 2:

            result = start_showdown(
                table.id
            )

            return {

                "auto_showdown": True,

                "result":
                    result
            }

        return {

            "auto_showdown": False
        }

    except Exception as e:

        raise Exception(str(e))


# =========================================================
# ================= SHOWDOWN STATUS =======================
# =========================================================

def showdown_status(table_id):

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        return {

            "table_id":
                table.id,

            "status":
                table.status,

            "winner_user_id":
                table.winner_user_id,

            "pot_amount":
                table.current_pot,

            "finished_at":
                str(table.finished_at)
                if table.finished_at
                else None
        }

    except Exception as e:

        raise Exception(str(e))


# =========================================================
# ================= RESET SHOWDOWN ========================
# =========================================================

def reset_showdown(table_id):

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        players = PlayerCard.query.filter_by(
            table_id=table.id
        ).all()

        # ================= RESET PLAYERS =================

        for player in players:

            player.is_winner = False

            player.win_amount = 0

            player.updated_at = \
                datetime.utcnow()

        # ================= RESET TABLE =================

        table.status = "waiting"

        table.winner_user_id = None

        table.finished_at = None

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "showdown_reset",

            {
                "table_id":
                    table.id
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "message":
                "Showdown reset complete"
        }

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))
