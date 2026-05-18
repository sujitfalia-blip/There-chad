# =========================================================
# ================= ADVANCED LOGGER ENGINE ================
# ================= ENTERPRISE PRODUCTION =================
# =========================================================

import os
import json
import gzip
import shutil
import logging
import traceback

from logging.handlers import (
    RotatingFileHandler,
    TimedRotatingFileHandler
)

from datetime import datetime

# =========================================================
# ================= PROJECT ROOT ==========================
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

LOG_DIR = os.path.join(
    PROJECT_ROOT,
    "logs"
)

os.makedirs(
    LOG_DIR,
    exist_ok=True
)

# =========================================================
# ================= LOG FILES =============================
# =========================================================

GAME_LOG_FILE = os.path.join(
    LOG_DIR,
    "game.log"
)

ERROR_LOG_FILE = os.path.join(
    LOG_DIR,
    "error.log"
)

SECURITY_LOG_FILE = os.path.join(
    LOG_DIR,
    "security.log"
)

TRANSACTION_LOG_FILE = os.path.join(
    LOG_DIR,
    "transaction.log"
)

SOCKET_LOG_FILE = os.path.join(
    LOG_DIR,
    "socket.log"
)

API_LOG_FILE = os.path.join(
    LOG_DIR,
    "api.log"
)

# =========================================================
# ================= CONFIG ================================
# =========================================================

MAX_LOG_SIZE = 20 * 1024 * 1024

BACKUP_COUNT = 10

ENABLE_CONSOLE_LOG = True

ENABLE_JSON_LOG = True

# =========================================================
# ================= LOG FORMAT ============================
# =========================================================

TEXT_FORMAT = logging.Formatter(

    "[%(asctime)s] "

    "[%(levelname)s] "

    "[%(name)s] "

    "%(message)s"
)

# =========================================================
# ================= JSON FORMATTER ========================
# =========================================================

class JsonFormatter(logging.Formatter):

    def format(self, record):

        payload = {

            "time":
                datetime.utcnow().isoformat(),

            "level":
                record.levelname,

            "logger":
                record.name,

            "message":
                record.getMessage()
        }

        return json.dumps(payload)

# =========================================================
# ================= COMPRESS ROTATED ======================
# =========================================================

class CompressedRotatingFileHandler(
    RotatingFileHandler
):

    def doRollover(self):

        super().doRollover()

        for i in range(
            self.backupCount,
            0,
            -1
        ):

            log_file = f"{self.baseFilename}.{i}"

            if os.path.exists(log_file):

                with open(
                    log_file,
                    'rb'
                ) as f_in:

                    with gzip.open(
                        f"{log_file}.gz",
                        'wb'
                    ) as f_out:

                        shutil.copyfileobj(
                            f_in,
                            f_out
                        )

                os.remove(log_file)

# =========================================================
# ================= CREATE LOGGER =========================
# =========================================================

def create_logger(
    logger_name,
    log_file,
    level=logging.INFO
):

    logger = logging.getLogger(
        logger_name
    )

    logger.setLevel(level)

    logger.propagate = False

    if logger.handlers:

        return logger

    # ================= FILE HANDLER =================

    file_handler = \
        CompressedRotatingFileHandler(

            log_file,

            maxBytes=MAX_LOG_SIZE,

            backupCount=BACKUP_COUNT
        )

    if ENABLE_JSON_LOG:

        file_handler.setFormatter(
            JsonFormatter()
        )

    else:

        file_handler.setFormatter(
            TEXT_FORMAT
        )

    logger.addHandler(
        file_handler
    )

    # ================= CONSOLE =================

    if ENABLE_CONSOLE_LOG:

        console_handler = \
            logging.StreamHandler()

        console_handler.setFormatter(
            TEXT_FORMAT
        )

        logger.addHandler(
            console_handler
        )

    return logger

# =========================================================
# ================= LOGGER INSTANCES ======================
# =========================================================

game_logger = create_logger(

    "GAME",

    GAME_LOG_FILE
)

error_logger = create_logger(

    "ERROR",

    ERROR_LOG_FILE,

    logging.ERROR
)

security_logger = create_logger(

    "SECURITY",

    SECURITY_LOG_FILE,

    logging.WARNING
)

transaction_logger = create_logger(

    "TRANSACTION",

    TRANSACTION_LOG_FILE
)

socket_logger = create_logger(

    "SOCKET",

    SOCKET_LOG_FILE
)

api_logger = create_logger(

    "API",

    API_LOG_FILE
)

# =========================================================
# ================= SAFE JSON =============================
# =========================================================

def safe_json(data):

    try:

        return json.dumps(
            data,
            default=str
        )

    except Exception:

        return str(data)

# =========================================================
# ================= GAME EVENT ============================
# =========================================================

def log_game_event(
    event,
    data=None
):

    payload = {

        "event":
            event,

        "data":
            data or {}
    }

    game_logger.info(
        safe_json(payload)
    )

# =========================================================
# ================= PLAYER ACTION =========================
# =========================================================

def log_player_action(
    table_id,
    player_id,
    action,
    amount=None,
    extra_data=None
):

    payload = {

        "table_id":
            table_id,

        "player_id":
            player_id,

        "action":
            action,

        "amount":
            amount,

        "extra":
            extra_data or {}
    }

    game_logger.info(
        safe_json(payload)
    )

# =========================================================
# ================= SECURITY EVENT ========================
# =========================================================

def log_security_event(
    event,
    user_id=None,
    ip_address=None,
    severity="medium",
    extra_data=None
):

    payload = {

        "event":
            event,

        "user_id":
            user_id,

        "ip":
            ip_address,

        "severity":
            severity,

        "extra":
            extra_data or {}
    }

    security_logger.warning(
        safe_json(payload)
    )

# =========================================================
# ================= ERROR LOGGER ==========================
# =========================================================

def log_error(
    error_message,
    exception=None,
    extra_data=None
):

    payload = {

        "error":
            error_message,

        "extra":
            extra_data or {}
    }

    if exception:

        payload["traceback"] = \
            traceback.format_exc()

    error_logger.error(
        safe_json(payload)
    )

# =========================================================
# ================= TRANSACTION LOGGER ====================
# =========================================================

def log_transaction(
    transaction_type,
    user_id,
    amount,
    before_balance=None,
    after_balance=None,
    extra_data=None
):

    payload = {

        "transaction_type":
            transaction_type,

        "user_id":
            user_id,

        "amount":
            amount,

        "before_balance":
            before_balance,

        "after_balance":
            after_balance,

        "extra":
            extra_data or {}
    }

    transaction_logger.info(
        safe_json(payload)
    )

# =========================================================
# ================= SOCKET EVENT ==========================
# =========================================================

def log_socket_event(
    event,
    socket_id,
    user_id=None,
    table_id=None
):

    payload = {

        "event":
            event,

        "socket_id":
            socket_id,

        "user_id":
            user_id,

        "table_id":
            table_id
    }

    socket_logger.info(
        safe_json(payload)
    )

# =========================================================
# ================= API REQUEST ===========================
# =========================================================

def log_api_request(
    endpoint,
    method,
    status_code,
    user_id=None,
    ip_address=None,
    duration_ms=None
):

    payload = {

        "endpoint":
            endpoint,

        "method":
            method,

        "status_code":
            status_code,

        "user_id":
            user_id,

        "ip":
            ip_address,

        "duration_ms":
            duration_ms
    }

    api_logger.info(
        safe_json(payload)
    )

# =========================================================
# ================= WINNER LOGGER =========================
# =========================================================

def log_winner(
    table_id,
    winner_id,
    winning_amount,
    hand_name
):

    payload = {

        "table_id":
            table_id,

        "winner_id":
            winner_id,

        "winning_amount":
            winning_amount,

        "hand":
            hand_name
    }

    game_logger.info(
        safe_json(payload)
    )

# =========================================================
# ================= STARTUP ===============================
# =========================================================

def log_server_start():

    game_logger.info(

        safe_json({

            "event":
                "SERVER_STARTED"
        })
    )

# =========================================================
# ================= SHUTDOWN ==============================
# =========================================================

def log_server_shutdown():

    game_logger.info(

        safe_json({

            "event":
                "SERVER_STOPPED"
        })
    )

# =========================================================
# ================= CLEAR LOG FILE ========================
# =========================================================

def clear_log_file(log_file):

    try:

        with open(
            log_file,
            "w"
        ) as file:

            file.write("")

        return True

    except Exception as e:

        log_error(

            "Failed to clear log file",

            exception=e
        )

        return False

# =========================================================
# ================= CLEAR ALL LOGS ========================
# =========================================================

def clear_all_logs():

    files = [

        GAME_LOG_FILE,
        ERROR_LOG_FILE,
        SECURITY_LOG_FILE,
        TRANSACTION_LOG_FILE,
        SOCKET_LOG_FILE,
        API_LOG_FILE
    ]

    result = {}

    for file in files:

        result[file] = \
            clear_log_file(file)

    return result

# =========================================================
# ================= LOG FILE SIZE =========================
# =========================================================

def get_log_size(log_file):

    try:

        if os.path.exists(log_file):

            return round(

                os.path.getsize(log_file)
                / 1024 / 1024,

                2
            )

        return 0

    except Exception:

        return 0

# =========================================================
# ================= LOGGER STATUS =========================
# =========================================================

def logger_status():

    return {

        "log_directory":
            LOG_DIR,

        "game_log_size_mb":
            get_log_size(
                GAME_LOG_FILE
            ),

        "error_log_size_mb":
            get_log_size(
                ERROR_LOG_FILE
            ),

        "security_log_size_mb":
            get_log_size(
                SECURITY_LOG_FILE
            ),

        "transaction_log_size_mb":
            get_log_size(
                TRANSACTION_LOG_FILE
            ),

        "socket_log_size_mb":
            get_log_size(
                SOCKET_LOG_FILE
            ),

        "api_log_size_mb":
            get_log_size(
                API_LOG_FILE
            ),

        "json_logging":
            ENABLE_JSON_LOG,

        "console_logging":
            ENABLE_CONSOLE_LOG
}
