# =========================================================
# ================= TEEN PATTI WINNER ENGINE ===============
# ================= ENTERPRISE PRODUCTION VERSION ==========
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

from game_engine.betting import (
    calculate_admin_commission
)

# =========================================================
# ================= CONFIG =================================
# =========================================================

AUTO_RESET_TABLE = True

WINNER_EVENT = "winner_declared"

SHOWDOWN_EVENT = "showdown_result"

TABLE_RESET_EVENT = "table_reset"

# =========================================================
# ================= ACTIVE PLAYERS =========================
# =========================================================

def get_active_players(table_id):

    """
    Get all non-packed active players
    """

    return PlayerCard.query.filter_by(
        table_id=table_id,
        is_packed=False
    ).all()


# =========================================================
# ================= PLAYER CARD LIST =======================
# =========================================================

def get_player_cards(player):

    """
    Return player 3 cards
    """

    return [
        player.card_1,
        player.card_2,
        player.card_3
    ]


# =========================================================
# ================= FIND STRONGEST PLAYER ==================
# =========================================================

def find_table_winner(table_id):

    """
    Find strongest hand player
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        players = get_active_players(
            table.id
        )

        if not players:

            raise Exception(
                "No active players found"
            )

        # ================= SINGLE PLAYER =================

        if len(players) == 1:

            winner_player = players[0]

        else:

            winner_player = players[0]

            for challenger in players[1:]:

                result = compare_hands(

                    get_player_cards(
                        winner_player
                    ),

                    get_player_cards(
                        challenger
                    )
                )

                if result == 2:

                    winner_player = challenger

        # ================= WINNER USER =================

        winner_user = User.query.get(
            winner_player.player_id
        )

        if not winner_user:

            raise Exception(
                "Winner user not found"
            )

        # ================= WINNER HAND =================

        cards = get_player_cards(
            winner_player
        )

        return {

            "success": True,

            "winner_player":
                winner_player,

            "winner_user":
                winner_user,

            "cards":
                cards,

            "hand_name":
                hand_name(cards),

            "hand_strength":
                get_hand_strength(cards)
        }

    except Exception as e:

        raise Exception(str(e))


# =========================================================
# ================= WIN DISTRIBUTION =======================
# =========================================================

def distribute_winning_amount(
    table_id,
    admin_user_id
):

    """
    Distribute winner amount
    Add admin commission
    """

    try:

        # ================= LOCK TABLE =================

        table = Table.query.filter_by(
            id=table_id
        ).with_for_update().first()

        if not table:

            raise Exception(
                "Table not found"
            )

        if table.status == "finished":

            raise Exception(
                "Game already finished"
            )

        # ================= FIND WINNER =================

        winner_data = find_table_winner(
            table.id
        )

        winner_user = winner_data[
            "winner_user"
        ]

        winner_player = winner_data[
            "winner_player"
        ]

        # ================= ADMIN =================

        admin_user = User.query.get(
            admin_user_id
        )

        if not admin_user:

            raise Exception(
                "Admin user not found"
            )

        # ================= POT =================

        total_pot = float(
            table.current_pot
        )

        if total_pot <= 0:

            raise Exception(
                "Invalid pot amount"
            )

        # ================= COMMISSION =================

        commission = calculate_admin_commission(
            total_pot
        )

        winner_amount = round(
            total_pot - commission,
            2
        )

        # ================= CREDIT WINNER =================

        winner_user.coins += winner_amount

        # ================= CREDIT ADMIN =================

        admin_user.coins += commission

        # ================= UPDATE PLAYER =================

        winner_player.is_winner = True

        winner_player.win_amount = winner_amount

        winner_player.last_action = "winner"

        winner_player.updated_at = datetime.utcnow()

        # ================= UPDATE TABLE =================

        table.status = "finished"

        table.current_pot = 0

        table.winner_user_id = winner_user.id

        table.finished_at = datetime.utcnow()

        table.updated_at = datetime.utcnow()

        # ================= COMMIT =================

        db.session.commit()

        # ================= SOCKET EVENT =================

        socketio.emit(

            WINNER_EVENT,

            {

                "success": True,

                "table_id":
                    table.id,

                "winner_id":
                    winner_user.id,

                "winner_name":
                    winner_user.name,

                "winner_username":
                    winner_user.username,

                "winner_hand":
                    winner_data["hand_name"],

                "winning_amount":
                    winner_amount,

                "admin_commission":
                    commission,

                "finished_at":
                    str(table.finished_at)
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "table_id":
                table.id,

            "winner_id":
                winner_user.id,

            "winner_name":
                winner_user.name,

            "winner_hand":
                winner_data["hand_name"],

            "winner_amount":
                winner_amount,

            "admin_commission":
                commission
        }

    # ================= DATABASE ERROR =================

    except SQLAlchemyError as e:

        db.session.rollback()

        raise Exception(
            f"Database error: {str(e)}"
        )

    # ================= GENERAL ERROR =================

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= AUTO FINISH ============================
# =========================================================

def auto_finish_game(table_id):

    """
    Auto finish if only one player remains
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        active_players = get_active_players(
            table.id
        )

        # ================= AUTO WIN =================

        if len(active_players) == 1:

            winner = active_players[0]

            return {

                "auto_finished": True,

                "winner_player_id":
                    winner.player_id
            }

        return {

            "auto_finished": False
        }

    except Exception as e:

        raise Exception(str(e))


# =========================================================
# ================= SHOWDOWN ===============================
# =========================================================

def showdown_result(table_id):

    """
    Return all players cards and hands
    """

    try:

        players = PlayerCard.query.filter_by(
            table_id=table_id
        ).all()

        showdown_players = []

        for player in players:

            user = User.query.get(
                player.player_id
            )

            cards = get_player_cards(
                player
            )

            showdown_players.append({

                "player_id":
                    player.player_id,

                "player_name":
                    user.name if user else None,

                "cards":
                    cards,

                "hand":
                    hand_name(cards),

                "packed":
                    player.is_packed,

                "winner":
                    player.is_winner
            })

        # ================= SOCKET =================

        socketio.emit(

            SHOWDOWN_EVENT,

            {

                "table_id":
                    table_id,

                "showdown":
                    showdown_players
            },

            room=f"table_{table_id}"
        )

        return {

            "success": True,

            "showdown":
                showdown_players
        }

    except Exception as e:

        raise Exception(str(e))


# =========================================================
# ================= RESET TABLE ============================
# =========================================================

def reset_table(table_id):

    """
    Reset table for next game
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        # ================= RESET USERS =================

        players = PlayerCard.query.filter_by(
            table_id=table.id
        ).all()

        for player in players:

            user = User.query.get(
                player.player_id
            )

            if user:

                user.current_table_id = None

        # ================= DELETE PLAYER DATA =================

        PlayerCard.query.filter_by(
            table_id=table.id
        ).delete()

        # ================= RESET TABLE =================

        table.current_players = 0

        table.active_players = 0

        table.current_pot = 0

        table.status = "waiting"

        table.winner_user_id = None

        table.updated_at = datetime.utcnow()

        # ================= COMMIT =================

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            TABLE_RESET_EVENT,

            {

                "success": True,

                "table_id":
                    table.id
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "message":
                "Table reset successful"
        }

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= FORCE WINNER ===========================
# =========================================================

def force_winner(
    table_id,
    winner_player_id
):

    """
    Admin force winner system
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        player = PlayerCard.query.filter_by(

            table_id=table.id,
            player_id=winner_player_id

        ).first()

        if not player:

            raise Exception(
                "Player not found"
            )

        player.is_winner = True

        table.winner_user_id = winner_player_id

        table.status = "finished"

        table.finished_at = datetime.utcnow()

        db.session.commit()

        socketio.emit(

            WINNER_EVENT,

            {

                "forced": True,

                "table_id":
                    table.id,

                "winner_id":
                    winner_player_id
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "message":
                "Winner forced successfully"
        }

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= CLEANUP TABLE ==========================
# =========================================================

def cleanup_finished_table(table_id):

    """
    Auto cleanup finished tables
    """

    try:

        table = Table.query.get(table_id)

        if not table:

            return

        if table.status != "finished":

            return

        if AUTO_RESET_TABLE:

            reset_table(table.id)

    except Exception as e:

        raise Exception(str(e))
