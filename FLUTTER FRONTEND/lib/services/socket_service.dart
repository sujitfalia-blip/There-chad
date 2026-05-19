import 'dart:async';
import 'package:socket_io_client/socket_io_client.dart' as IO;

class SocketService {
  static final SocketService _instance = SocketService._internal();
  factory SocketService() => _instance;

  SocketService._internal();

  late IO.Socket socket;

  bool _connected = false;
  String? _token;
  String? _url;

  final Map<String, StreamController<dynamic>> _streams = {};
  final List<Map<String, dynamic>> _pendingEmits = [];

  // ================= CONNECT =================
  void connect(String url, String token) {
    _url = url;
    _token = token;

    socket = IO.io(
      url,
      IO.OptionBuilder()
          .setTransports(['websocket'])
          .enableAutoConnect()
          .setReconnectionAttempts(999999)
          .setReconnectionDelay(2000)
          .setReconnectionDelayMax(5000)
          .setQuery({"token": token})
          .build(),
    );

    socket.connect();

    // ================= CONNECTED =================
    socket.onConnect((_) {
      _connected = true;
      print("✅ SOCKET CONNECTED");

      // resend pending emits
      _flushPending();
    });

    // ================= DISCONNECT =================
    socket.onDisconnect((_) {
      _connected = false;
      print("❌ SOCKET DISCONNECTED");
    });

    // ================= ERROR =================
    socket.onConnectError((data) {
      print("⚠️ CONNECT ERROR: $data");
    });

    socket.onError((data) {
      print("⚠️ SOCKET ERROR: $data");
    });
  }

  // =========================================================
  // ================= SAFE EMIT (QUEUE SYSTEM) =============
  // =========================================================
  void emit(String event, dynamic data) {
    if (_connected) {
      socket.emit(event, data);
    } else {
      _pendingEmits.add({
        "event": event,
        "data": data,
      });
    }
  }

  void _flushPending() {
    for (var item in _pendingEmits) {
      socket.emit(item["event"], item["data"]);
    }
    _pendingEmits.clear();
  }

  // =========================================================
  // ================= STREAM LISTENER (BEST FOR FLUTTER) ====
  // =========================================================
  Stream<dynamic> stream(String event) {
    if (!_streams.containsKey(event)) {
      final controller = StreamController<dynamic>.broadcast();

      socket.on(event, (data) {
        controller.add(data);
      });

      _streams[event] = controller;
    }

    return _streams[event]!.stream;
  }

  // =========================================================
  // ================= ONE-TIME LISTENER =====================
  // =========================================================
  void once(String event, Function(dynamic) callback) {
    socket.once(event, callback);
  }

  // =========================================================
  // ================= REMOVE LISTENER =======================
  // =========================================================
  void off(String event) {
    socket.off(event);
    _streams[event]?.close();
    _streams.remove(event);
  }

  // =========================================================
  // ================= MANUAL LISTEN =========================
  // =========================================================
  void on(String event, Function(dynamic) callback) {
    socket.off(event); // prevent duplicate listeners
    socket.on(event, callback);
  }

  // =========================================================
  // ================= RECONNECT MANUALLY ====================
  // =========================================================
  void reconnect() {
    if (_url != null && _token != null) {
      disconnect();
      connect(_url!, _token!);
    }
  }

  // =========================================================
  // ================= DISCONNECT ============================
  // =========================================================
  void disconnect() {
    socket.disconnect();
    _connected = false;

    for (var c in _streams.values) {
      c.close();
    }

    _streams.clear();
    _pendingEmits.clear();
  }

  bool get isConnected => _connected;
}
