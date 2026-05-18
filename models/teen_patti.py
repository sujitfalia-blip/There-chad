import uuid

from datetime import datetime

from extensions import db


class PlayerCard(db.Model):

    __tablename__ = "player_cards"

    # ================= PRIMARY =================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    uuid = db.Column(
        db.String(120),
        unique=True,
        default=lambda: str(uuid.uuid4())
    )

    # ================= RELATIONS =================

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

    # ================= CARDS =================

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

    # ================= CARD STATUS =================

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

    # ================= BLIND SYSTEM =================

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

    # ================= GAMEPLAY =================

    seat_position = db.Column(
        db.Integer
    )

    turn_number = db.Column(
        db.Integer,
        default=0
    )

    side_show_requested = db.Column(
        db.Boolean,
        default=False
    )

    side_show_with = db.Column(
        db.Integer
    )

    has_played_turn = db.Column(
        db.Boolean,
        default=False
    )

    # ================= WINNING =================

    winning_amount = db.Column(
        db.BigInteger,
        default=0
    )

    hand_rank = db.Column(
        db.String(100)
    )

    # trail
    # pure_sequence
    # sequence
    # color
    # pair
    # high_card

    # ================= ADMIN =================

    admin_visible = db.Column(
        db.Boolean,
        default=True
    )

    suspicious_activity = db.Column(
        db.Boolean,
        default=False
    )

    # ================= REALTIME =================

    socket_session = db.Column(
        db.String(255)
    )

    last_action = db.Column(
        db.String(100)
    )

    action_time = db.Column(
        db.DateTime
    )

    # ================= TIMESTAMPS =================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ================= SERIALIZER =================

    def to_dict(self):

        return {

            "id": self.id,

            "table_id": self.table_id,

            "player_id": self.player_id,

            "is_seen": self.is_seen,

            "is_packed": self.is_packed,

            "blind_count": self.blind_count,

            "total_bet_amount": self.total_bet_amount,

            "seat_position": self.seat_position,

            "hand_rank": self.hand_rank
        }

    # ================= CARD LIST =================

    def get_cards(self):

        return [
            self.card_1,
            self.card_2,
            self.card_3
        ]
