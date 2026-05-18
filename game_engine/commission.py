# =========================================================
# ================= COMMISSION ENGINE =====================
# ================= ENTERPRISE PRODUCTION =================
# =========================================================

from decimal import Decimal, ROUND_DOWN
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from extensions import db, socketio

from models.user import User
from models.table import Table
from models.transaction import Transaction

# =========================================================
# ================= CONFIG ================================
# =========================================================

DEFAULT_COMMISSION_PERCENT = Decimal("5.00")

MIN_COMMISSION = Decimal("0.00")

MAX_COMMISSION = Decimal("99999999.99")

ROUNDING = ROUND_DOWN

# =========================================================
# ================= DECIMAL SAFE ==========================
# =========================================================

def to_decimal(value):

    try:

        return Decimal(str(value))

    except Exception:

        raise Exception(
            "Invalid decimal amount"
        )

# =========================================================
# ================= VALIDATE ==============================
# =========================================================

def validate_amount(amount):

    amount = to_decimal(amount)

    if amount <= 0:

        raise Exception(
            "Amount must be greater than 0"
        )

    return amount

# =========================================================
# ================= CALCULATE COMMISSION ==================
# =========================================================

def calculate_commission(
    amount,
    percent=DEFAULT_COMMISSION_PERCENT
):

    """
    Calculate admin rake
    """

    amount = validate_amount(amount)

    percent = validate_amount(percent)

    commission = (

        amount * percent

    ) / Decimal("100")

    commission = commission.quantize(

        Decimal("0.01"),

        rounding=ROUNDING
    )

    if commission < MIN_COMMISSION:

        commission = MIN_COMMISSION

    if commission > MAX_COMMISSION:

        commission = MAX_COMMISSION

    return commission

# =========================================================
# ================= FINAL PAYOUT ==========================
# =========================================================

def calculate_payout(
    pot_amount,
    percent=DEFAULT_COMMISSION_PERCENT
):

    """
    Winner payout after commission
    """

    pot_amount = validate_amount(
        pot_amount
    )

    commission = calculate_commission(

        pot_amount,
        percent
    )

    winner_amount = (

        pot_amount - commission

    ).quantize(

        Decimal("0.01"),

        rounding=ROUNDING
    )

    return {

        "pot_amount":
            float(pot_amount),

        "commission":
            float(commission),

        "winner_amount":
            float(winner_amount)
    }

# =========================================================
# ================= GET ADMIN =============================
# =========================================================

def get_admin_user():

    admin = User.query.filter(

        User.role.in_([
            "super_admin",
            "owner",
            "admin"
        ])

    ).order_by(

        User.id.asc()

    ).first()

    if not admin:

        raise Exception(
            "Admin account not found"
        )

    return admin

# =========================================================
# ================= SAVE TRANSACTION ======================
# =========================================================

def create_transaction(

    user_id,
    amount,
    transaction_type,
    description
):

    transaction = Transaction(

        user_id=user_id,

        amount=float(amount),

        transaction_type=
            transaction_type,

        description=description,

        created_at=
            datetime.utcnow()
    )

    db.session.add(transaction)

# =========================================================
# ================= CREDIT ADMIN ==========================
# =========================================================

def credit_admin_commission(

    admin_user,
    amount,
    table_id=None
):

    try:

        amount = validate_amount(amount)

        admin_user.coins += float(amount)

        admin_user.updated_at = \
            datetime.utcnow()

        # ================= TRANSACTION =================

        create_transaction(

            admin_user.id,

            amount,

            "commission_credit",

            f"Commission from table {table_id}"
        )

        return {

            "success": True,

            "admin_id":
                admin_user.id,

            "commission":
                float(amount),

            "admin_balance":
                float(admin_user.coins)
        }

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= DISTRIBUTE POT ========================
# =========================================================

def distribute_pot(

    winner_user,
    table,
    commission_percent=
    DEFAULT_COMMISSION_PERCENT
):

    """
    Final production payout
    """

    try:

        # ================= VALIDATION =================

        if not winner_user:

            raise Exception(
                "Winner user not found"
            )

        if not table:

            raise Exception(
                "Table not found"
            )

        # ================= LOCK TABLE =================

        locked_table = Table.query.filter_by(

            id=table.id

        ).with_for_update().first()

        if not locked_table:

            raise Exception(
                "Unable to lock table"
            )

        # ================= ADMIN =================

        admin_user = get_admin_user()

        # ================= POT =================

        total_pot = validate_amount(
            locked_table.current_pot
        )

        if total_pot <= 0:

            raise Exception(
                "Pot amount invalid"
            )

        # ================= PAYOUT =================

        payout = calculate_payout(

            total_pot,
            commission_percent
        )

        commission = to_decimal(
            payout["commission"]
        )

        winner_amount = to_decimal(
            payout["winner_amount"]
        )

        # ================= CREDIT WINNER =================

        winner_user.coins += \
            float(winner_amount)

        winner_user.updated_at = \
            datetime.utcnow()

        # ================= CREDIT ADMIN =================

        admin_user.coins += \
            float(commission)

        admin_user.updated_at = \
            datetime.utcnow()

        # ================= TABLE UPDATE =================

        locked_table.status = \
            "finished"

        locked_table.current_pot = 0

        locked_table.finished_at = \
            datetime.utcnow()

        locked_table.winner_user_id = \
            winner_user.id

        # ================= TRANSACTIONS =================

        create_transaction(

            winner_user.id,

            winner_amount,

            "game_win",

            f"Winner payout table {table.id}"
        )

        create_transaction(

            admin_user.id,

            commission,

            "table_commission",

            f"Commission earned table {table.id}"
        )

        # ================= SAVE =================

        db.session.commit()

        # ================= SOCKET =================

        socketio.emit(

            "commission_distributed",

            {

                "table_id":
                    locked_table.id,

                "winner_id":
                    winner_user.id,

                "winner_amount":
                    float(winner_amount),

                "commission":
                    float(commission)
            },

            room=f"table_{locked_table.id}"
        )

        return {

            "success": True,

            "winner_id":
                winner_user.id,

            "winner_amount":
                float(winner_amount),

            "commission":
                float(commission),

            "total_pot":
                float(total_pot)
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
# ================= ESTIMATE ==============================
# =========================================================

def estimate_table_commission(

    boot_amount,
    players,
    percent=
    DEFAULT_COMMISSION_PERCENT
):

    try:

        boot_amount = validate_amount(
            boot_amount
        )

        if players <= 0:

            raise Exception(
                "Invalid player count"
            )

        estimated_pot = \
            boot_amount * players

        commission = calculate_commission(

            estimated_pot,
            percent
        )

        winner_amount = \
            estimated_pot - commission

        return {

            "players":
                players,

            "estimated_pot":
                float(estimated_pot),

            "commission":
                float(commission),

            "winner_amount":
                float(winner_amount)
        }

    except Exception as e:

        raise Exception(str(e))

# =========================================================
# ================= EMERGENCY REFUND ======================
# =========================================================

def emergency_refund(table):

    try:

        if not table:

            raise Exception(
                "Table not found"
            )

        active_users = User.query.filter_by(

            current_table_id=table.id

        ).all()

        if not active_users:

            raise Exception(
                "No active users"
            )

        total_players = len(active_users)

        refund_amount = (

            to_decimal(table.current_pot)

            / Decimal(str(total_players))

        ).quantize(

            Decimal("0.01"),

            rounding=ROUNDING
        )

        for user in active_users:

            user.coins += \
                float(refund_amount)

            user.updated_at = \
                datetime.utcnow()

            create_transaction(

                user.id,

                refund_amount,

                "refund",

                f"Refund table {table.id}"
            )

        table.current_pot = 0

        table.status = "cancelled"

        table.finished_at = \
            datetime.utcnow()

        db.session.commit()

        socketio.emit(

            "table_refunded",

            {

                "table_id":
                    table.id,

                "refund_amount":
                    float(refund_amount)
            },

            room=f"table_{table.id}"
        )

        return {

            "success": True,

            "refund_amount":
                float(refund_amount)
        }

    except Exception as e:

        db.session.rollback()

        raise Exception(str(e))

# =========================================================
# ================= ADMIN REPORT ==========================
# =========================================================

def admin_commission_report(admin_user):

    try:

        if not admin_user:

            raise Exception(
                "Admin not found"
            )

        total = db.session.query(

            db.func.sum(
                Transaction.amount
            )

        ).filter(

            and_(

                Transaction.user_id ==
                admin_user.id,

                Transaction.transaction_type ==
                "table_commission"
            )

        ).scalar()

        return {

            "admin_id":
                admin_user.id,

            "total_commission":
                float(total or 0),

            "wallet_balance":
                float(admin_user.coins)
        }

    except Exception as e:

        raise Exception(str(e))
