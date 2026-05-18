import uuid

from datetime import datetime

from extensions import db


class PlayerCard(db.Model):

    __tablename__ = "player_cards"

    # =========================================================
    # ================= PRIMARY ===============================
    # =========================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    uuid = db.Column(
        db.String(120),
        unique=True,
        default=lambda: str(uuid.uuid4())
    )

    # =========================================================
    # ================= RELATIONS =============================
    # =========================================================

    table_id = db.Column(
        db.Integer,
        db.ForeignKey('tables.id'),
        nullable=False,
        index=True
    )

    player_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )

    # =========================================================
    # ================= CARD DATA =============================
    # =========================================================

    card_1 = db.Column(
        db.String(10),
        nullable=False
    )

    card_2 = db.Column(
        db.String(10),
        nullable=False
    )

    card_3 = db.Column(
        db.String(10),
        nullable=False
    )

    # =========================================================
    # ================= GAME STATUS ===========================
    # =========================================================

    is_seen = db.Column(
        db.Boolean,
        default=False
    )

    is_packed = db.Column(
        db.Boolean,
        default=False
    )

    is_winner = db.Column(
        db.Boolean,
        default=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    has_folded = db.Column(
        db.Boolean,
        default=False
    )

    # =========================================================
    # ================= BETTING ===============================
    # =========================================================

    blind_count = db.Column(
        db.Integer,
        default=0
    )

    current_blind_amount = db.Column(
        db.BigInteger,
        default=0
    )

    current_seen_amount = db.Column(
        db.BigInteger,
        default=0
    )

    total_bet_amount = db.Column(
        db.BigInteger,
        default=0
    )

    total_win_amount = db.Column(
        db.BigInteger,
        default=0
    )

    # =========================================================
    # ================= GAMEPLAY ==============================
    # =========================================================

    seat_position = db.Column(
        db.Integer
    )

    turn_number = db.Column(
        db.Integer,
        default=0
    )

    action_count = db.Column(
        db.Integer,
        default=0
    )

    last_action = db.Column(
        db.String(100)
    )

    action_time = db.Column(
        db.DateTime
    )

    # =========================================================
    # ================= SIDE SHOW =============================
    # =========================================================

    side_show_requested = db.Column(
        db.Boolean,
        default=False
    )

    side_show_target = db.Column(
        db.Integer
    )

    side_show_accepted = db.Column(
        db.Boolean,
        default=False
    )

    # =========================================================
    # ================= HAND RANK =============================
    # =========================================================

    hand_rank = db.Column(
        db.String(100)
    )

    # trail
    # pure_sequence
    # sequence
    # color
    # pair
    # high_card

    hand_points = db.Column(
        db.Integer,
        default=0
    )

    # =========================================================
    # ================= ADMIN CONTROL =========================
    # =========================================================

    admin_visible = db.Column(
        db.Boolean,
        default=True
    )

    suspicious_activity = db.Column(
        db.Boolean,
        default=False
    )

    cheat_flag = db.Column(
        db.Boolean,
        default=False
    )

    force_pack = db.Column(
        db.Boolean,
        default=False
    )

    # =========================================================
    # ================= REALTIME ==============================
    # =========================================================

    socket_id = db.Column(
        db.String(255)
    )

    device_id = db.Column(
        db.String(255)
    )

    ip_address = db.Column(
        db.String(255)
    )

    # =========================================================
    # ================= TIMERS ================================
    # =========================================================

    turn_expires_at = db.Column(
        db.DateTime
    )

    auto_packed = db.Column(
        db.Boolean,
        default=False
    )

    # =========================================================
    # ================= ANALYTICS =============================
    # =========================================================

    total_games = db.Column(
        db.Integer,
        default=0
    )

    total_wins = db.Column(
        db.Integer,
        default=0
    )

    win_rate = db.Column(
        db.Float,
        default=0
    )

    # =========================================================
    # ================= TIMESTAMPS ============================
    # =========================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =========================================================
    # ================= SERIALIZER ============================
    # =========================================================

    def to_dict(self):

        return {

            "id": self.id,

            "uuid": self.uuid,

            "table_id": self.table_id,

            "player_id": self.player_id,

            "cards": [

                self.card_1,
                self.card_2,
                self.card_3
            ],

            "is_seen": self.is_seen,

            "is_packed": self.is_packed,

            "is_winner": self.is_winner,

            "blind_count": self.blind_count,

            "total_bet_amount":
                self.total_bet_amount,

            "seat_position":
                self.seat_position,

            "last_action":
                self.last_action,

            "hand_rank":
                self.hand_rank
        }

    # =========================================================
    # ================= CARD LIST =============================
    # =========================================================

    def get_cards(self):

        return [

            self.card_1,

            self.card_2,

            self.card_3
        ]

    # =========================================================
    # ================= PLAYER ACTIVE =========================
    # =========================================================

    def is_player_active(self):

        return (
            self.is_active and
            not self.is_packed and
            not self.has_folded
        )

    # =========================================================
    # ================= UPDATE ACTION =========================
    # =========================================================

    def update_action(
        self,
        action
    ):

        self.last_action = action

        self.action_time = datetime.utcnow()

        self.action_count += 1