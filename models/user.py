import uuid

from datetime import datetime

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import db


class User(db.Model):

    __tablename__ = "users"

    # ================= PRIMARY =================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    uuid = db.Column(
        db.String(100),
        unique=True,
        default=lambda: str(uuid.uuid4())
    )

    # ================= BASIC INFO =================

    name = db.Column(
        db.String(120),
        nullable=False
    )

    username = db.Column(
        db.String(80),
        unique=True
    )

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    profile_photo = db.Column(
        db.String(255)
    )

    bio = db.Column(
        db.Text
    )

    # ================= ROLE =================

    role = db.Column(
        db.String(50),
        default='player'
    )

    permissions = db.Column(
        db.JSON,
        default={}
    )

    # ================= WALLET =================

    coins = db.Column(
    Numeric(18, 2),
    default=0
    )

    bonus_coins = db.Column(
        db.BigInteger,
        default=0
    )

    referral_earnings = db.Column(
        db.BigInteger,
        default=0
    )

    total_deposit = db.Column(
        db.BigInteger,
        default=0
    )

    total_withdraw = db.Column(
        db.BigInteger,
        default=0
    )

    # ================= REFERRAL =================

    referral_code = db.Column(
        db.String(20),
        unique=True
    )

    referred_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    # ================= STATUS =================

    is_online = db.Column(
        db.Boolean,
        default=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    is_banned = db.Column(
        db.Boolean,
        default=False
    )

    is_verified = db.Column(
        db.Boolean,
        default=False
    )

    kyc_verified = db.Column(
        db.Boolean,
        default=False
    )

    # ================= GAME =================

    total_games = db.Column(
        db.Integer,
        default=0
    )

    total_wins = db.Column(
        db.Integer,
        default=0
    )

    total_loss = db.Column(
        db.Integer,
        default=0
    )

    current_table_id = db.Column(
        db.Integer
    )

    # ================= DEVICE =================

    device_id = db.Column(
        db.String(255)
    )

    last_ip = db.Column(
        db.String(100)
    )

    socket_id = db.Column(
        db.String(255)
    )

    # ================= VOICE =================

    mic_muted = db.Column(
        db.Boolean,
        default=False
    )

    voice_banned = db.Column(
        db.Boolean,
        default=False
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

    last_login = db.Column(
        db.DateTime
    )

    # ================= PASSWORD METHODS =================

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )

    # ================= JSON =================

    def to_dict(self):

        return {

            "id": self.id,

            "uuid": self.uuid,

            "name": self.name,

            "phone": self.phone,

            "coins": self.coins,

            "role": self.role,

            "is_online": self.is_online,

            "created_at": str(self.created_at)
        }
