# =========================================================
# ================= GAME HISTORY MODEL ====================
# ================= PRODUCTION VERSION ====================
# =========================================================

from datetime import datetime

from extensions import db

# =========================================================
# ================= GAME HISTORY ==========================
# =========================================================

class GameHistory(db.Model):

    __tablename__ = "game_history"

    # ================= PRIMARY =================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ================= TABLE =================

    table_id = db.Column(
        db.Integer,
        db.ForeignKey("tables.id"),
        nullable=False,
        index=True
    )

    # ================= WINNER =================

    winner_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    # ================= GAME INFO =================

    total_players = db.Column(
        db.Integer,
        default=0
    )

    total_pot = db.Column(
        db.Float,
        default=0
    )

    admin_commission = db.Column(
        db.Float,
        default=0
    )

    winner_amount = db.Column(
        db.Float,
        default=0
    )

    boot_amount = db.Column(
        db.Float,
        default=0
    )

    # ================= STATUS =================

    game_status = db.Column(

        db.String(30),

        default="finished",

        index=True
    )

    """
    finished
    cancelled
    refunded
    crashed
    """

    # ================= WINNING HAND =================

    winning_hand = db.Column(
        db.String(100),
        nullable=True
    )

    # ================= SECURITY =================

    suspicious_activity = db.Column(
        db.Boolean,
        default=False
    )

    admin_reviewed = db.Column(
        db.Boolean,
        default=False
    )

    # ================= TIME =================

    started_at = db.Column(
        db.DateTime,
        nullable=True
    )

    finished_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # ================= SERIALIZE =================

    def to_dict(self):

        return {

            "id": self.id,

            "table_id":
                self.table_id,

            "winner_user_id":
                self.winner_user_id,

            "total_players":
                self.total_players,

            "total_pot":
                self.total_pot,

            "admin_commission":
                self.admin_commission,

            "winner_amount":
                self.winner_amount,

            "boot_amount":
                self.boot_amount,

            "game_status":
                self.game_status,

            "winning_hand":
                self.winning_hand,

            "finished_at":
                str(self.finished_at)
        }
