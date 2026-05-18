import uuid

from datetime import datetime

from extensions import db


class Table(db.Model):

    __tablename__ = "tables"

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

    # ================= TABLE INFO =================

    table_name = db.Column(
        db.String(120)
    )

    table_code = db.Column(
        db.String(20),
        unique=True
    )

    table_type = db.Column(
        db.String(50),
        default='public'
    )

    # public / private / vip

    # ================= BETTING =================

    boot_amount = db.Column(
        db.Integer,
        nullable=False
    )

    min_blind = db.Column(
        db.Integer,
        default=1
    )

    max_blind = db.Column(
        db.Integer,
        default=1024
    )

    chaal_limit = db.Column(
        db.Integer,
        default=4
    )

    pot_limit = db.Column(
        db.BigInteger,
        default=100000
    )

    current_pot = db.Column(
        db.BigInteger,
        default=0
    )

    # ================= PLAYERS =================

    max_players = db.Column(
        db.Integer,
        default=5
    )

    current_players = db.Column(
        db.Integer,
        default=0
    )

    active_players = db.Column(
        db.Integer,
        default=0
    )

    spectators = db.Column(
        db.Integer,
        default=0
    )

    # ================= GAME STATE =================

    status = db.Column(
        db.String(50),
        default='waiting'
    )

    # waiting
    # running
    # finished
    # paused

    game_round = db.Column(
        db.Integer,
        default=1
    )

    current_turn = db.Column(
        db.Integer
    )

    dealer_position = db.Column(
        db.Integer,
        default=0
    )

    winner_user_id = db.Column(
        db.Integer
    )

    winning_amount = db.Column(
        db.BigInteger,
        default=0
    )

    # ================= AUTO SYSTEM =================

    auto_start = db.Column(
        db.Boolean,
        default=True
    )

    auto_restart = db.Column(
        db.Boolean,
        default=True
    )

    auto_pack_timeout = db.Column(
        db.Integer,
        default=30
    )

    turn_timer = db.Column(
        db.Integer,
        default=20
    )

    # ================= SEEN / BLIND =================

    blind_to_seen_multiplier = db.Column(
        db.Integer,
        default=2
    )

    auto_seen_after_blind = db.Column(
        db.Integer,
        default=5
    )

    # ================= SECURITY =================

    is_locked = db.Column(
        db.Boolean,
        default=False
    )

    is_private = db.Column(
        db.Boolean,
        default=False
    )

    password = db.Column(
        db.String(255)
    )

    anti_cheat_enabled = db.Column(
        db.Boolean,
        default=True
    )

    # ================= ADMIN =================

    admin_monitoring = db.Column(
        db.Boolean,
        default=True
    )

    admin_control_enabled = db.Column(
        db.Boolean,
        default=True
    )

    # ================= VOICE =================

    voice_enabled = db.Column(
        db.Boolean,
        default=True
    )

    voice_room_id = db.Column(
        db.String(255)
    )

    # ================= REALTIME =================

    socket_room = db.Column(
        db.String(255)
    )

    game_state = db.Column(
        db.JSON,
        default={}
    )

    # ================= ANALYTICS =================

    total_games = db.Column(
        db.Integer,
        default=0
    )

    total_volume = db.Column(
        db.BigInteger,
        default=0
    )

    highest_pot = db.Column(
        db.BigInteger,
        default=0
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

    started_at = db.Column(
        db.DateTime
    )

    ended_at = db.Column(
        db.DateTime
    )

    # ================= SERIALIZER =================

    def to_dict(self):

        return {

            "id": self.id,

            "uuid": self.uuid,

            "table_name": self.table_name,

            "boot_amount": self.boot_amount,

            "current_pot": self.current_pot,

            "status": self.status,

            "players": self.current_players,

            "max_players": self.max_players
        }