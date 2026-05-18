# =========================================================
# ================= GAME ROUND MODEL ======================
# =========================================================

from datetime import datetime

from extensions import db


class GameRound(db.Model):

    __tablename__ = "game_rounds"

    # ================= PRIMARY =================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    round_uuid = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        index=True
    )

    # ================= TABLE =================

    table_id = db.Column(
        db.Integer,
        db.ForeignKey("tables.id"),
        nullable=False,
        index=True
    )

    # ================= GAME INFO =================

    boot_amount = db.Column(
        db.Float,
        default=0
    )

    total_pot = db.Column(
        db.Float,
        default=0
    )

    commission_amount = db.Column(
        db.Float,
        default=0
    )

    winner_amount = db.Column(
        db.Float,
        default=0
    )

    # ================= WINNER =================

    winner_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    winner_hand = db.Column(
        db.String(100),
        nullable=True
    )

    # ================= STATUS =================

    status = db.Column(
        db.String(30),
        default="running"
    )

    total_players = db.Column(
        db.Integer,
        default=0
    )

    active_players = db.Column(
        db.Integer,
        default=0
    )

    total_turns = db.Column(
        db.Integer,
        default=0
    )

    # ================= TIMER =================

    started_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    finished_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ================= SECURITY =================

    anti_cheat_checked = db.Column(
        db.Boolean,
        default=False
    )

    suspicious_activity = db.Column(
        db.Boolean,
        default=False
    )

    # ================= ADMIN =================

    admin_notes = db.Column(
        db.Text,
        nullable=True
    )

    # ================= TIMESTAMP =================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
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

            "round_uuid": self.round_uuid,

            "table_id": self.table_id,

            "boot_amount": self.boot_amount,

            "total_pot": self.total_pot,

            "commission_amount":
                self.commission_amount,

            "winner_amount":
                self.winner_amount,

            "winner_user_id":
                self.winner_user_id,

            "winner_hand":
                self.winner_hand,

            "status":
                self.status,

            "total_players":
                self.total_players,

            "active_players":
                self.active_players,

            "total_turns":
                self.total_turns
  }
