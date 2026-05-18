# =========================================================
# ================= ADMIN EARNING MODEL ===================
# =========================================================

from datetime import datetime

from extensions import db


class AdminEarning(db.Model):

    __tablename__ = "admin_earnings"

    # ================= PRIMARY =================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ================= ADMIN =================

    admin_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # ================= TABLE =================

    table_id = db.Column(
        db.Integer,
        db.ForeignKey("tables.id"),
        nullable=True
    )

    round_id = db.Column(
        db.Integer,
        db.ForeignKey("game_rounds.id"),
        nullable=True
    )

    # ================= COMMISSION =================

    commission_percent = db.Column(
        db.Float,
        default=5
    )

    commission_amount = db.Column(
        db.Float,
        nullable=False
    )

    total_pot = db.Column(
        db.Float,
        default=0
    )

    # ================= SOURCE =================

    earning_type = db.Column(
        db.String(50),
        default="game_commission"
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    # ================= STATUS =================

    status = db.Column(
        db.String(20),
        default="credited"
    )

    # ================= TIMESTAMP =================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # ================= SERIALIZE =================

    def to_dict(self):

        return {

            "id": self.id,

            "admin_user_id":
                self.admin_user_id,

            "table_id":
                self.table_id,

            "round_id":
                self.round_id,

            "commission_percent":
                self.commission_percent,

            "commission_amount":
                self.commission_amount,

            "total_pot":
                self.total_pot,

            "earning_type":
                self.earning_type,

            "status":
                self.status
  }
