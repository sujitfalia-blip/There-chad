import 'dart:async';
import 'package:socket_io_client/socket_io_client.dart' as IO;

import '../config/app_config.dart';

class SocketService {
  static final SocketService _instance = SocketService._internal();
  factory SocketService() => _instance;

  SocketService._internal();

  IO.Socket? socket;

  bool _connected = false;

  String? _token;
  String? _url;

  final Map<String, StreamController<dynamic>> _streams = {};
  final List<Map<String, dynamic>> _pendingEmits = [];

  // =========================================================
  // ================= CONNECT ================================
  // =========================================================
  void connect({String? url, required String token}) {
    _token = token;
    _url = url ?? AppConfig.socketUrl;

    // 🔥 CLEAN RE-CONNECT SAFETY
    disconnect();

    socket = IO.io(
      _url!,
      IO.OptionBuilder()
          .setTransports(['websocket'])
          .enableAutoConnect()
          .setReconnectionAttempts(10) // 🔥 safe production limit
          .setReconnectionDelay(2000)
          .setReconnectionDelayMax(5000)
          .setQuery({"token": token})
          .build(),
    );

    socket!.connect();

    // ================= CONNECTED =================
    socket!.onConnect((_) {
      _connected = true;
      print("✅ SOCKET CONNECTED: $_url");

      _flushPending();
    });

    // ================= DISCONNECT =================
    socket!.onDisconnect((_) {
      _connected = false;
      print("❌ SOCKET DISCONNECTED");
    });

    // ================= ERROR =================
    socket!.onConnectError((data) {
      print("⚠️ CONNECT ERROR: $data");
    });

    socket!.onError((data) {
      print("⚠️ SOCKET ERROR: $data");
    });
  }

  // =========================================================
  // ================= SAFE EMIT =============================
  // =========================================================
  void emit(String event, dynamic data) {
    if (_connected && socket != null) {
      socket!.emit(event, data);
    } else {
      _pendingEmits.add({
        "event": event,
        "data": data,
      });
    }
  }

  void _flushPending() {
    if (socket == null) return;

    for (var item in _pendingEmits) {
      socket!.emit(item["event"], item["data"]);
    }

    _pendingEmits.clear();
  }

  // =========================================================
  // ================= STREAM LISTENER ========================
  // =========================================================
  Stream<dynamic> stream(String event) {
    if (!_streams.containsKey(event)) {
      final controller = StreamController<dynamic>.broadcast();

      socket?.on(event, (data) {
        controller.add(data);
      });

      _streams[event] = controller;
    }

    return _streams[event]!.stream;
  }

  // =========================================================
  // ================= ONE TIME LISTENER ======================
  // =========================================================
  void once(String event, Function(dynamic) callback) {
    socket?.once(event, callback);
  }

  // =========================================================
  // ================= REMOVE LISTENER ========================
  // =========================================================
  void off(String event) {
    socket?.off(event);

    _streams[event]?.close();
    _streams.remove(event);
  }

  // =========================================================
  // ================= MANUAL LISTENER ========================
  // =========================================================
  void on(String event, Function(dynamic) callback) {
    socket?.off(event);
    socket?.on(event, callback);
  }

  // =========================================================
  // ================= RECONNECT ==============================
  // =========================================================
  void reconnect() {
    if (_token != null) {
      disconnect();
      connect(token: _token!);
    }
  }

  // =========================================================
  // ================= DISCONNECT =============================
  // =========================================================
  void disconnect() {
    socket?.disconnect();
    socket?.dispose();

    socket = null;
    _connected = false;

    for (var c in _streams.values) {
      c.close();
    }

    _streams.clear();
    _pendingEmits.clear();
  }

  bool get isConnected => _connected;
}
