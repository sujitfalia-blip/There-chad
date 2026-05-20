# =========================================================
# ================= WITHDRAWAL MODEL ======================
# ================= PRODUCTION VERSION ====================
# =========================================================

from datetime import datetime
from decimal import Decimal

from extensions import db


class Withdrawal(db.Model):

    __tablename__ = "withdrawals"

    # =====================================================
    # ================= PRIMARY ============================
    # =====================================================

    id = db.Column(
        db.BigInteger,
        primary_key=True
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
    # ================= PAYMENT ============================
    # =====================================================

    amount = db.Column(
        db.Numeric(18, 2),
        nullable=False
    )

    payment_method = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    account_number = db.Column(
        db.String(120),
        nullable=False
    )

    account_name = db.Column(
        db.String(120),
        nullable=True
    )

    # =====================================================
    # ================= STATUS =============================
    # =====================================================

    status = db.Column(
        db.String(20),
        default="pending",
        nullable=False,
        index=True
    )

    """
    pending
    approved
    paid
    rejected
    cancelled
    """

    admin_note = db.Column(
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
            "withdrawals",
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

            "user_id":
                self.user_id,

            "amount":
                str(self.amount),

            "payment_method":
                self.payment_method,

            "account_number":
                self.account_number,

            "account_name":
                self.account_name,

            "status":
                self.status,

            "admin_note":
                self.admin_note,

            "created_at":
                self.created_at.isoformat(),

            "updated_at":
                self.updated_at.isoformat()
  }
