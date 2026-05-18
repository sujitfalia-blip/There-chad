# =========================================================
# ================= SOCKET EVENTS ENGINE ==================
# ================= ENTERPRISE PRODUCTION =================
# =========================================================

from datetime import datetime

from flask import request

from flask_socketio import (
    emit,
    join_room,
    leave_room,
    disconnect
)

from flask_jwt_extended import (
    decode_token
)

from sqlalchemy.exc import SQLAlchemyError

from extensions import (
    socketio,
    db
)

from models.user import User
from models.table import Table
from models.player_card import PlayerCard

# =========================================================
# ================= CONFIG ================================
# =========================================================

MAX_RECONNECT_SECONDS = 30

# =========================================================
# ================= SAFE USER =============================
# =========================================================

def get_user_by_socket(socket_id):

    return User.query.filter_by(
        socket_id=socket_id
    ).first()


# =========================================================
# ================= SOCKET CONNECT ========================
# =========================================================

@socketio.on("connect")
def handle_connect():

    try:

        print(
            f"[SOCKET CONNECTED] {request.sid}"
        )

        emit(

            "connected",

            {

                "success": True,

                "socket_id":
                    request.sid,

                "message":
                    "Socket connection established"
            }
        )

    except Exception as e:

        print(
            f"[CONNECT ERROR] {str(e)}"
        )


# =========================================================
# ================= SOCKET DISCONNECT =====================
# =========================================================

@socketio.on("disconnect")
def handle_disconnect():

    try:

        user = get_user_by_socket(
            request.sid
        )

        if not user:

            return

        # ================= UPDATE USER =================

        user.is_online = False

        user.socket_id = None

        user.last_seen = datetime.utcnow()

        db.session.commit()

        # ================= PLAYER OFFLINE =================

        if user.current_table_id:

            socketio.emit(

                "player_offline",

                {

                    "user_id":
                        user.id,

                    "username":
                        user.username
                },

                room=f"table_{user.current_table_id}"
            )

        # ================= ADMIN UPDATE =================

        socketio.emit(

            "admin_user_offline",

            {

                "user_id":
                    user.id,

                "table_id":
                    user.current_table_id
            },

            room="super_admin"
        )

        print(
            f"[SOCKET DISCONNECTED] {request.sid}"
        )

    except Exception as e:

        print(
            f"[DISCONNECT ERROR] {str(e)}"
        )


# =========================================================
# ================= JOIN TABLE SOCKET =====================
# =========================================================

@socketio.on("join_table")
def join_table_socket(data):

    try:

        # ================= VALIDATION =================

        if not data:

            emit(

                "error",

                {
                    "message":
                        "Invalid socket request"
                }
            )

            return

        # ================= TOKEN =================

        token = data.get("token")

        table_id = data.get("table_id")

        if not token:

            emit(

                "error",

                {
                    "message":
                        "Authentication token missing"
                }
            )

            disconnect()

            return

        # ================= JWT =================

        decoded = decode_token(token)

        user_id = decoded["sub"]

        # ================= USER =================

        user = User.query.get(user_id)

        if not user:

            emit(

                "error",

                {
                    "message":
                        "User not found"
                }
            )

            disconnect()

            return

        # ================= ACCOUNT CHECK =================

        if user.is_banned:

            emit(

                "error",

                {
                    "message":
                        "Account banned"
                }
            )

            disconnect()

            return

        if not user.is_active:

            emit(

                "error",

                {
                    "message":
                        "Account inactive"
                }
            )

            disconnect()

            return

        # ================= TABLE =================

        table = Table.query.get(table_id)

        if not table:

            emit(

                "error",

                {
                    "message":
                        "Table not found"
                }
            )

            return

        # ================= TABLE STATUS =================

        if table.is_locked:

            emit(

                "error",

                {
                    "message":
                        "Table locked by admin"
                }
            )

            return

        # ================= DUPLICATE LOGIN =================

        if user.socket_id and \
           user.socket_id != request.sid:

            socketio.emit(

                "force_logout",

                {

                    "message":
                        "Logged in from another device"
                },

                room=user.socket_id
            )

        # ================= UPDATE USER =================

        user.socket_id = request.sid

        user.is_online = True

        user.last_seen = datetime.utcnow()

        db.session.commit()

        # ================= ROOM =================

        room_name = f"table_{table.id}"

        join_room(room_name)

        # ================= PLAYER JOIN =================

        socketio.emit(

            "player_joined",

            {

                "user_id":
                    user.id,

                "username":
                    user.username,

                "table_id":
                    table.id
            },

            room=room_name
        )

        # ================= JOIN SUCCESS =================

        emit(

            "join_success",

            {

                "success": True,

                "socket_id":
                    request.sid,

                "table_id":
                    table.id,

                "message":
                    "Joined successfully"
            }
        )

        # ================= ADMIN LIVE UPDATE =================

        socketio.emit(

            "admin_live_table_update",

            {

                "table_id":
                    table.id,

                "user_id":
                    user.id,

                "username":
                    user.username,

                "action":
                    "joined"
            },

            room="super_admin"
        )

        print(
            f"[JOINED] User {user.id} -> {room_name}"
        )

    except Exception as e:

        emit(

            "error",

            {
                "message":
                    str(e)
            }
        )


# =========================================================
# ================= LEAVE TABLE SOCKET ====================
# =========================================================

@socketio.on("leave_table")
def leave_table_socket(data):

    try:

        token = data.get("token")

        table_id = data.get("table_id")

        decoded = decode_token(token)

        user_id = decoded["sub"]

        user = User.query.get(user_id)

        if not user:

            return

        room_name = f"table_{table_id}"

        # ================= LEAVE ROOM =================

        leave_room(room_name)

        # ================= UPDATE USER =================

        user.current_table_id = None

        db.session.commit()

        # ================= PLAYER LEFT =================

        socketio.emit(

            "player_left",

            {

                "user_id":
                    user.id,

                "username":
                    user.username
            },

            room=room_name
        )

        # ================= ADMIN UPDATE =================

        socketio.emit(

            "admin_live_table_update",

            {

                "table_id":
                    table_id,

                "user_id":
                    user.id,

                "action":
                    "left"
            },

            room="super_admin"
        )

        print(
            f"[LEFT] User {user.id} -> {room_name}"
        )

    except Exception as e:

        emit(

            "error",

            {
                "message":
                    str(e)
            }
        )


# =========================================================
# ================= HEARTBEAT =============================
# =========================================================

@socketio.on("heartbeat")
def heartbeat(data=None):

    try:

        emit(

            "heartbeat_response",

            {

                "status":
                    "alive",

                "socket_id":
                    request.sid,

                "server_time":
                    str(datetime.utcnow())
            }
        )

    except Exception as e:

        emit(

            "error",

            {
                "message":
                    str(e)
            }
        )


# =========================================================
# ================= RECONNECT SYSTEM ======================
# =========================================================

@socketio.on("reconnect_player")
def reconnect_player(data):

    try:

        token = data.get("token")

        decoded = decode_token(token)

        user_id = decoded["sub"]

        user = User.query.get(user_id)

        if not user:

            emit(

                "error",

                {
                    "message":
                        "User not found"
                }
            )

            return

        # ================= UPDATE SOCKET =================

        user.socket_id = request.sid

        user.is_online = True

        user.last_seen = datetime.utcnow()

        db.session.commit()

        # ================= REJOIN ROOM =================

        if user.current_table_id:

            room_name = \
                f"table_{user.current_table_id}"

            join_room(room_name)

        emit(

            "reconnect_success",

            {

                "success": True,

                "table_id":
                    user.current_table_id
            }
        )

        print(
            f"[RECONNECTED] User {user.id}"
        )

    except Exception as e:

        emit(

            "error",

            {
                "message":
                    str(e)
            }
        )


# =========================================================
# ================= PING TEST =============================
# =========================================================

@socketio.on("ping_test")
def ping_test():

    emit(

        "pong_test",

        {
            "message":
                "pong"
        }
        )
