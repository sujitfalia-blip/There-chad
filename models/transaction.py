# =========================================================
# ================= TRANSACTION MODEL =====================
# ================= PRODUCTION VERSION ====================
# =========================================================

import uuid

from datetime import datetime

from extensions import db

# =========================================================
# ================= TRANSACTION MODEL =====================
# =========================================================

class Transaction(db.Model):

    __tablename__ = "transactions"

    # ================= PRIMARY =================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    transaction_id = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        default=lambda:
            uuid.uuid4().hex
    )

    # ================= USER =================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # ================= TYPE =================

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
    transfer
    """

    # ================= STATUS =================

    status = db.Column(

        db.String(20),

        default="completed",

        index=True
    )

    """
    pending
    completed
    failed
    cancelled
    """

    # ================= MONEY =================

    amount = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    before_balance = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    after_balance = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    # ================= GAME =================

    table_id = db.Column(
        db.Integer,
        db.ForeignKey("tables.id"),
        nullable=True,
        index=True
    )

    reference_id = db.Column(
        db.String(100),
        nullable=True
    )

    # ================= EXTRA =================

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

    # ================= TIME =================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ================= SERIALIZE =================

    def to_dict(self):

        return {

            "id": self.id,

            "transaction_id":
                self.transaction_id,

            "user_id":
                self.user_id,

            "transaction_type":
                self.transaction_type,

            "status":
                self.status,

            "amount":
                self.amount,

            "before_balance":
                self.before_balance,

            "after_balance":
                self.after_balance,

            "table_id":
                self.table_id,

            "reference_id":
                self.reference_id,

            "remark":
                self.remark,

            "created_at":
                str(self.created_at)
  }
