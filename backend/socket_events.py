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

from extensions import (
    socketio,
    db
)

from models.user import User
from models.table import Table

# ================= CONNECT =================

@socketio.on('connect')
def handle_connect():

    print(
        f"Socket Connected: {request.sid}"
    )

# ================= DISCONNECT =================

@socketio.on('disconnect')
def handle_disconnect():

    user = User.query.filter_by(
        socket_id=request.sid
    ).first()

    if user:

        user.is_online = False

        user.socket_id = None

        db.session.commit()

        if user.current_table_id:

            emit(

                'player_offline',

                {
                    "user_id": user.id
                },

                room=f"table_{user.current_table_id}"
            )

    print(
        f"Socket Disconnected: {request.sid}"
    )

# ================= JOIN TABLE =================

@socketio.on('join_table')
def join_table_socket(data):

    try:

        # ================= TOKEN =================

        token = data.get('token')

        if not token:

            emit(
                'error',
                {
                    "message": "Token missing"
                }
            )

            disconnect()

            return

        decoded = decode_token(token)

        user_id = decoded['sub']

        # ================= USER =================

        user = User.query.get(user_id)

        if not user:

            emit(
                'error',
                {
                    "message": "User not found"
                }
            )

            disconnect()

            return

        # ================= USER STATUS =================

        if user.is_banned:

            emit(
                'error',
                {
                    "message": "User banned"
                }
            )

            disconnect()

            return

        # ================= TABLE =================

        table_id = data.get('table_id')

        table = Table.query.get(table_id)

        if not table:

            emit(
                'error',
                {
                    "message": "Table not found"
                }
            )

            return

        # ================= TABLE SECURITY =================

        if table.is_locked:

            emit(
                'error',
                {
                    "message": "Table locked"
                }
            )

            return

        # ================= DUPLICATE SOCKET =================

        if user.socket_id:

            emit(

                'force_disconnect',

                {
                    "message": "New login detected"
                },

                room=user.socket_id
            )

        # ================= UPDATE USER =================

        user.socket_id = request.sid

        user.is_online = True

        db.session.commit()

        # ================= ROOM =================

        room_name = f"table_{table.id}"

        join_room(room_name)

        # ================= JOIN SUCCESS =================

        emit(

            'join_success',

            {
                "success": True,

                "table_id": table.id,

                "socket_id": request.sid
            }
        )

        # ================= BROADCAST =================

        emit(

            'player_joined',

            {

                "user_id": user.id,

                "table_id": table.id,

                "username": user.username
            },

            room=room_name,

            include_self=False
        )

        # ================= ADMIN MONITOR =================

        emit(

            'admin_table_update',

            {

                "table_id": table.id,

                "user_id": user.id,

                "action": "joined"
            },

            room="super_admin"
        )

        print(
            f"User {user.id} joined {room_name}"
        )

    # ================= ERROR =================

    except Exception as e:

        emit(

            'error',

            {
                "message": str(e)
            }
        )

# ================= LEAVE TABLE =================

@socketio.on('leave_table')
def leave_table_socket(data):

    try:

        token = data.get('token')

        decoded = decode_token(token)

        user_id = decoded['sub']

        user = User.query.get(user_id)

        table_id = data.get('table_id')

        room_name = f"table_{table_id}"

        leave_room(room_name)

        if user:

            user.current_table_id = None

            db.session.commit()

        emit(

            'player_left',

            {
                "user_id": user_id
            },

            room=room_name
        )

    except Exception as e:

        emit(
            'error',
            {
                "message": str(e)
            }
        )

# ================= HEARTBEAT =================

@socketio.on('heartbeat')
def heartbeat():

    emit(
        'heartbeat_response',
        {
            "status": "alive"
        }
    )
