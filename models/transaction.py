# =========================================================
# ================= TRANSACTION MODEL =====================
# ================= PRODUCTION VERSION ====================
# =========================================================

import uuid

from datetime import datetime
from decimal import Decimal

from extensions import db


# =========================================================
# ================= TRANSACTION MODEL =====================
# =========================================================

class Transaction(db.Model):

    __tablename__ = "transactions"

    # =====================================================
    # ================= PRIMARY ============================
    # =====================================================

    id = db.Column(
        db.BigInteger,
        primary_key=True
    )

    transaction_id = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: uuid.uuid4().hex
    )

    # =====================================================
    # ================= USER ===============================
    # =====================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # ================= TYPE ===============================
    # =====================================================

    transaction_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    """
    Types:

    deposit
    withdraw
    bet
    win
    commission
    refund
    bonus
    penalty
    transfer_sent
    transfer_received
    """

    # =====================================================
    # ================= STATUS =============================
    # =====================================================

    status = db.Column(
        db.String(20),
        nullable=False,
        default="completed",
        index=True
    )

    """
    pending
    completed
    failed
    cancelled
    """

    # =====================================================
    # ================= MONEY ==============================
    # =====================================================

    amount = db.Column(
        db.Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    before_balance = db.Column(
        db.Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    after_balance = db.Column(
        db.Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    # =====================================================
    # ================= GAME / REFERENCE ===================
    # =====================================================

    table_id = db.Column(
        db.Integer,
        db.ForeignKey("tables.id"),
        nullable=True,
        index=True
    )

    reference_id = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    # =====================================================
    # ================= EXTRA ==============================
    # =====================================================

    remark = db.Column(
        db.String(255),
        nullable=True
    )

    ip_address = db.Column(
        db.String(100),
        nullable=True
    )

    device_info = db.Column(
        db.String(255),
        nullable=True
    )

    # =====================================================
    # ================= TIME ===============================
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =====================================================
    # ================= RELATIONSHIP =======================
    # =====================================================

    user = db.relationship(
        "User",
        backref=db.backref(
            "transactions",
            lazy=True
        )
    )

    # =====================================================
    # ================= SERIALIZER =========================
    # =====================================================

    def to_dict(self):

        return {

            "id":
                self.id,

            "transaction_id":
                self.transaction_id,

            "user_id":
                self.user_id,

            "transaction_type":
                self.transaction_type,

            "status":
                self.status,

            "amount":
                str(self.amount),

            "before_balance":
                str(self.before_balance),

            "after_balance":
                str(self.after_balance),

            "table_id":
                self.table_id,

            "reference_id":
                self.reference_id,

            "remark":
                self.remark,

            "ip_address":
                self.ip_address,

            "device_info":
                self.device_info,

            "created_at":
                self.created_at.isoformat()
                if self.created_at else None,

            "updated_at":
                self.updated_at.isoformat()
                if self.updated_at else None
        }

    # =====================================================
    # ================= DEBUG ==============================
    # =====================================================

    def __repr__(self):

        return (
            f"<Transaction "
            f"{self.transaction_id} "
            f"{self.transaction_type} "
            f"{self.amount}>"
    )
