# =========================================================
# ================= SIDE SHOW LOG MODEL ===================
# =========================================================

from datetime import datetime

from extensions import db


class SideShowLog(db.Model):

    __tablename__ = "side_show_logs"

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

    round_id = db.Column(
        db.Integer,
        db.ForeignKey("game_rounds.id"),
        nullable=True
    )

    # ================= PLAYERS =================

    requester_player_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    target_player_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    loser_player_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    # ================= RESULT =================

    requester_hand = db.Column(
        db.String(100),
        nullable=True
    )

    target_hand = db.Column(
        db.String(100),
        nullable=True
    )

    result = db.Column(
        db.String(50),
        nullable=True
    )

    # ================= STATUS =================

    status = db.Column(
        db.String(30),
        default="requested"
    )

    # requested
    # accepted
    # rejected
    # timeout

    # ================= TIMER =================

    request_time = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    response_time = db.Column(
        db.DateTime,
        nullable=True
    )

    # ================= SECURITY =================

    suspicious = db.Column(
        db.Boolean,
        default=False
    )

    ip_address = db.Column(
        db.String(100),
        nullable=True
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

            "table_id":
                self.table_id,

            "round_id":
                self.round_id,

            "requester_player_id":
                self.requester_player_id,

            "target_player_id":
                self.target_player_id,

            "loser_player_id":
                self.loser_player_id,

            "requester_hand":
                self.requester_hand,

            "target_hand":
                self.target_hand,

            "result":
                self.result,

            "status":
                self.status
  }
