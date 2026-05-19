import 'dart:async';
import '../services/socket_service.dart';

class GameController {
  static final GameController _instance = GameController._internal();
  factory GameController() => _instance;

  GameController._internal();

  final SocketService _socket = SocketService();

  // ================= GAME STATE =================
  int? currentPlayerId;
  int? myPlayerId;

  int remainingSeconds = 0;
  int? tableId;

  bool isMyTurn = false;
  bool isPacked = false;

  bool _initialized = false;

  final StreamController<void> _updateController =
      StreamController<void>.broadcast();

  Stream<void> get stream => _updateController.stream;

  // =========================================================
  // ================= INIT (SAFE) ============================
  // =========================================================
  void init({
    required int tableId,
    required int myPlayerId,
  }) {
    this.tableId = tableId;
    this.myPlayerId = myPlayerId;

    if (_initialized) return;

    _initialized = true;
    _listenSocket();
  }

  // =========================================================
  // ================= SOCKET LISTEN ==========================
  // =========================================================
  void _listenSocket() {
    _socket.stream("turn_started").listen((data) {
      currentPlayerId = data["player_id"];
      remainingSeconds = data["turn_time"];

      _updateTurn();
      _notify();
    });

    _socket.stream("turn_warning").listen((data) {
      remainingSeconds = data["remaining_time"];
      _notify();
    });

    _socket.stream("auto_packed").listen((data) {
      if (data["player_id"] == myPlayerId) {
        isPacked = true;
      }
      _notify();
    });

    _socket.stream("turn_skipped").listen((data) {
      _updateTurn();
      _notify();
    });

    _socket.stream("winner").listen((data) {
      _resetTurn();
      _notify();
    });
  }

  // =========================================================
  // ================= TURN LOGIC =============================
  // =========================================================
  void _updateTurn() {
    isMyTurn = (currentPlayerId == myPlayerId);
  }

  void _resetTurn() {
    currentPlayerId = null;
    isMyTurn = false;
    remainingSeconds = 0;
  }

  // =========================================================
  // ================= ACTION VALIDATION ======================
  // =========================================================
  bool get canPlay => isMyTurn && !isPacked;

  void pack() {
    if (!canPlay) return;

    _socket.emit("pack", {
      "table_id": tableId,
      "player_id": myPlayerId,
    });
  }

  void showCard() {
    if (!canPlay) return;

    _socket.emit("show", {
      "table_id": tableId,
      "player_id": myPlayerId,
    });
  }

  void bet(int amount) {
    if (!canPlay) return;

    _socket.emit("bet", {
      "table_id": tableId,
      "player_id": myPlayerId,
      "amount": amount,
    });
  }

  // =========================================================
  // ================= UI UPDATE ==============================
  // =========================================================
  void _notify() {
    if (!_updateController.isClosed) {
      _updateController.add(null);
    }
  }

  // =========================================================
  // ================= RESET (NEW GAME) ======================
  // =========================================================
  void reset() {
    currentPlayerId = null;
    remainingSeconds = 0;
    isMyTurn = false;
    isPacked = false;
    tableId = null;
    myPlayerId = null;

    _notify();
  }

  // =========================================================
  // ================= DISPOSE ================================
  // =========================================================
  void dispose() {
    _updateController.close();
    _initialized = false;
  }
}
