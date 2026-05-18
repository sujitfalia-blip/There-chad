# =========================================================
# ================= PLAYER ACTION MODEL ===================
# ================= PRODUCTION VERSION ====================
# =========================================================

from datetime import datetime

from extensions import db

# =========================================================
# ================= PLAYER ACTION =========================
# =========================================================

class PlayerAction(db.Model):

    __tablename__ = "player_actions"

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

    # ================= PLAYER =================

    player_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # ================= ACTION =================

    action = db.Column(

        db.String(50),

        nullable=False,

        index=True
    )

    """
    join
    bet
    blind
    seen
    pack
    show
    sideshow_request
    sideshow_accept
    sideshow_reject
    timeout_pack
    winner
    """

    # ================= BET =================

    amount = db.Column(
        db.Float,
        default=0
    )

    pot_after_action = db.Column(
        db.Float,
        default=0
    )

    # ================= TURN =================

    turn_number = db.Column(
        db.Integer,
        default=0
    )

    round_number = db.Column(
        db.Integer,
        default=1
    )

    # ================= EXTRA =================

    action_status = db.Column(
        db.String(30),
        default="success"
    )

    ip_address = db.Column(
        db.String(100),
        nullable=True
    )

    device_info = db.Column(
        db.String(255),
        nullable=True
    )

    extra_data = db.Column(
        db.JSON,
        nullable=True
    )

    # ================= TIME =================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )

    # ================= SERIALIZE =================

    def to_dict(self):

        return {

            "id": self.id,

            "table_id":
                self.table_id,

            "player_id":
                self.player_id,

            "action":
                self.action,

            "amount":
                self.amount,

            "pot_after_action":
                self.pot_after_action,

            "turn_number":
                self.turn_number,

            "round_number":
                self.round_number,

            "action_status":
                self.action_status,

            "created_at":
                str(self.created_at)
  }
