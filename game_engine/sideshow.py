# =========================================================
# ================= TEEN PATTI SIDE SHOW ENGINE ===========
# ================= ENTERPRISE PRODUCTION VERSION =========
# =========================================================

from datetime import datetime, timedelta

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
    hand_name
)

# =========================================================
# ================= CONFIG ================================
# =========================================================

SIDE_SHOW_TIMEOUT_SECONDS = 15

SIDE_SHOW_COOLDOWN_SECONDS = 5

# =========================================================
# ================= SAFE PLAYER FETCH =====================
# =========================================================

def get_player(table_id, player_id):

    return PlayerCard.query.filter_by(
        table_id=table_id,
        player_id=player_id
    ).with_for_update().first()


# =========================================================
# ================= VALIDATE SIDE SHOW ====================
# =========================================================

def validate_side_show(
    requester,
    target,
    table
):

    if not requester:
        raise Exception(
            "Requester not found"
        )

    if not target:
        raise Exception(
            "Target player not found"
        )

    if requester.is_packed:
        raise Exception(
            "Packed player cannot request"
        )

    if target.is_packed:
        raise Exception(
            "Target already packed"
        )

    if not requester.is_seen:
        raise Exception(
            "Blind player cannot request side show"
        )

    if requester.player_id == target.player_id:
        raise Exception(
            "Invalid target player"
        )

    if table.side_show_pending:
        raise Exception(
            "Another side show already active"
        )

    # ================= COOLDOWN =================

    if requester.last_side_show_at:

        cooldown_end = (
            requester.last_side_show_at +
            timedelta(
                seconds=SIDE_SHOW_COOLDOWN_SECONDS
            )
        )

        if datetime.utcnow() < cooldown_end:

            raise Exception(
                "Please wait before next side show"
            )

    return True


# =========================================================
# ================= REQUEST SIDE SHOW =====================
# =========================================================

def request_side_show(
    requester_id,
    target_player_id,
    table_id
):

    try:

        # ================= TABLE =================

        table = Table.query.filter_by(
            id=table_id
        ).with_for_update().first()

        if not table:

            raise Exception(
                "Table not found"
            )

        # ================= PLAYER FETCH =================

        requester = get_player(
            table.id,
            requester_id
        )

        target = get_player(
            table.id,
            target_player_id
        )

        # ================= VALIDATION =================

        validate_side_show(
            requester,
            target,
            table
        )

        # ================= UPDATE =================

        table.side_show_pending = True

        table.side_show_requested_by = \
            requester.player_id

        table.side_show_requested_to = \
            target.player_id

        requester.side_show_with_player_id = \
            target.player_id

        requester.last_action = \
            "side_show_requested"

        requester.last_side_show_at = \
            datetime.utcnow()

        requester.updated_at = \
            datetime.utcnow()

        # ================= SAVE =================

        db.session.commit()

        # ================= USERS =================

        requester_user = User.query.get(
            requester.player_id
        )

        target_user = User.query.get(
            target.player_id
        )

        # ================= SOCKET =================

        socketio.emit(

            "side_show_requested",

            {

                "table_id":
                    table.id,

                "requester_id":
                    requester.player_id,

                "requester_name":
                    requester_user.name
                    if requester_user else None,

                "target_player_id":
                    target.player_id,

                "target_name":
                    target_user.name
                    if target_user else None,

                "timeout":
                    SIDE_SHOW_TIMEOUT_SECONDS
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "message":
                "Side show request sent"
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
# ================= REJECT SIDE SHOW ======================
# =========================================================

def reject_side_show(
    target_player_id,
    table_id
):

    try:

        # ================= TABLE =================

        table = Table.query.filter_by(
            id=table_id
        ).with_for_update().first()

        if not table:

            raise Exception(
                "Table not found"
            )

        # ================= REQUESTER =================

        requester = PlayerCard.query.filter_by(
            table_id=table.id
        ).filter(
            PlayerCard.side_show_with_player_id ==
            target_player_id
        ).first()

        if not requester:

            raise Exception(
                "No pending side show"
            )

        # ================= RESET =================

        requester.side_show_with_player_id = None

        requester.last_action = \
            "side_show_rejected"

        requester.updated_at = \
            datetime.utcnow()

        table.side_show_pending = False

        table.side_show_requested_by = None

        table.side_show_requested_to = None

        # ================= SAVE =================

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "side_show_rejected",

            {

                "table_id":
                    table.id,

                "requester_id":
                    requester.player_id,

                "target_player_id":
                    target_player_id
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "message":
                "Side show rejected"
        }

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))


# =========================================================
# ================= ACCEPT SIDE SHOW ======================
# =========================================================

def accept_side_show(
    target_player_id,
    table_id
):

    try:

        # ================= TABLE =================

        table = Table.query.filter_by(
            id=table_id
        ).with_for_update().first()

        if not table:

            raise Exception(
                "Table not found"
            )

        # ================= REQUESTER =================

        requester = PlayerCard.query.filter_by(
            table_id=table.id
        ).filter(
            PlayerCard.side_show_with_player_id ==
            target_player_id
        ).first()

        if not requester:

            raise Exception(
                "No pending side show"
            )

        # ================= TARGET =================

        target = get_player(
            table.id,
            target_player_id
        )

        if not target:

            raise Exception(
                "Target player missing"
            )

        # ================= VALIDATION =================

        if requester.is_packed:
            raise Exception(
                "Requester already packed"
            )

        if target.is_packed:
            raise Exception(
                "Target already packed"
            )

        # ================= CARDS =================

        requester_cards = [

            requester.card_1,
            requester.card_2,
            requester.card_3
        ]

        target_cards = [

            target.card_1,
            target.card_2,
            target.card_3
        ]

        # ================= COMPARE =================

        result = compare_hands(
            requester_cards,
            target_cards
        )

        # =================================================
        # RESULT:
        # 1 = requester wins
        # 2 = target wins
        # 0 = tie
        # =================================================

        if result == 1:

            loser = target
            winner = requester

        elif result == 2:

            loser = requester
            winner = target

        else:

            loser = target
            winner = requester

        # ================= PACK LOSER =================

        loser.is_packed = True

        loser.last_action = \
            "lost_side_show"

        loser.updated_at = \
            datetime.utcnow()

        # ================= TABLE UPDATE =================

        table.active_players -= 1

        table.side_show_pending = False

        table.side_show_requested_by = None

        table.side_show_requested_to = None

        requester.side_show_with_player_id = None

        # ================= USERS =================

        requester_user = User.query.get(
            requester.player_id
        )

        target_user = User.query.get(
            target.player_id
        )

        loser_user = User.query.get(
            loser.player_id
        )

        winner_user = User.query.get(
            winner.player_id
        )

        # ================= SAVE =================

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "side_show_result",

            {

                "table_id":
                    table.id,

                "winner_player_id":
                    winner.player_id,

                "winner_name":
                    winner_user.name
                    if winner_user else None,

                "loser_player_id":
                    loser.player_id,

                "loser_name":
                    loser_user.name
                    if loser_user else None,

                "requester_hand":
                    hand_name(
                        requester_cards
                    ),

                "target_hand":
                    hand_name(
                        target_cards
                    ),

                "requester_cards":
                    requester_cards,

                "target_cards":
                    target_cards
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "winner_player_id":
                winner.player_id,

            "loser_player_id":
                loser.player_id,

            "message":
                "Side show completed"
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
# ================= AUTO REJECT ===========================
# =========================================================

def auto_reject_side_show(
    table_id,
    target_player_id
):

    try:

        return reject_side_show(
            target_player_id,
            table_id
        )

    except Exception as e:

        raise Exception(str(e))


# =========================================================
# ================= SIDE SHOW STATUS ======================
# =========================================================

def side_show_status(table_id):

    try:

        table = Table.query.get(table_id)

        if not table:

            raise Exception(
                "Table not found"
            )

        return {

            "pending":
                table.side_show_pending,

            "requested_by":
                table.side_show_requested_by,

            "requested_to":
                table.side_show_requested_to
        }

    except Exception as e:

        raise Exception(str(e))
