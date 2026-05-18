import uuid
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from extensions import db

from models.table import Table


# ================= CONFIG =================

ALLOWED_BOOT_AMOUNTS = [1, 2, 5, 10, 20, 50, 100]

MAX_PLAYERS_PER_TABLE = 5


# ================= TABLE ENGINE =================

def find_or_create_table(boot_amount):

    try:

        # ================= VALIDATION =================

        if not isinstance(boot_amount, int):

            raise ValueError("Boot must be integer")

        if boot_amount not in ALLOWED_BOOT_AMOUNTS:

            raise ValueError("Invalid boot amount")

        # ================= LOCK SAFE QUERY =================

        table = Table.query.filter(

            Table.boot_amount == boot_amount,
            Table.status == "waiting",
            Table.is_locked == False,
            Table.current_players < Table.max_players

        ).order_by(

            Table.id.asc()

        ).with_for_update(of=Table).first()

        # ================= REUSE TABLE =================

        if table:

            table.updated_at = datetime.utcnow()

            return table

        # ================= CREATE NEW TABLE =================

        new_table = Table(

            table_name=f"Table-{boot_amount}-{uuid.uuid4().hex[:6]}",

            table_code=uuid.uuid4().hex[:8],

            boot_amount=boot_amount,

            max_players=MAX_PLAYERS_PER_TABLE,

            current_players=0,

            active_players=0,

            spectators=0,

            current_pot=0,

            status="waiting",

            is_locked=False,

            admin_monitoring=True,

            created_at=datetime.utcnow(),

            updated_at=datetime.utcnow()
        )

        db.session.add(new_table)

        db.session.flush()  # get ID without commit

        return new_table

    # ================= DATABASE ERROR =================

    except SQLAlchemyError as e:

        db.session.rollback()

        raise Exception(
            f"Database error: {str(e)}"
        )

    # ================= VALIDATION ERROR =================

    except ValueError as e:

        raise Exception(
            f"Validation error: {str(e)}"
        )

    # ================= UNKNOWN ERROR =================

    except Exception as e:

        raise Exception(
            f"Table engine crash: {str(e)}"
        )
