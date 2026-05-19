class AppConfig {
  // =========================================================
  // ================= ENVIRONMENT ============================
  // =========================================================

  static const bool isProduction = true;

  // =========================================================
  // ================= BACKEND ================================
  // =========================================================

  static const String _devBaseUrl = "http://10.236.188.210:5000/api";
  static const String _devSocketUrl = "http://10.236.188.210:5000";

  static const String _prodBaseUrl =
      "https://there-chad.onrender.com/api";

  // ⚠️ Socket root only (no /api)
  static const String _prodSocketUrl =
      "https://there-chad.onrender.com";

  // =========================================================
  // ================= ACTIVE ================================
  // =========================================================

  static String get baseUrl =>
      isProduction ? _prodBaseUrl : _devBaseUrl;

  static String get socketUrl =>
      isProduction ? _prodSocketUrl : _devSocketUrl;

  // =========================================================
  // ================= GAME CONFIG ============================
  // =========================================================

  static const int turnTime = 50;
  static const int warningTime = 20;
  static const int autoPackTime = 50;

  // =========================================================
  // ================= FEATURES ===============================
  // =========================================================

  static const bool enableChat = true;
  static const bool enableSound = true;
  static const bool enableVibration = true;
  static const bool enableDebugLogs = false;

  // =========================================================
  // ================= LIMITS ================================
  // =========================================================

  static const int maxPlayersPerTable = 6;
  static const int minPlayersToStart = 2;

  static const int maxBetLimit = 100000;
  static const int minBetLimit = 10;

  // =========================================================
  // ================= SOCKET EVENTS ==========================
  // =========================================================

  static const String eventTurnStarted = "turn_started";
  static const String eventTurnWarning = "turn_warning";
  static const String eventAutoPacked = "auto_packed";
  static const String eventWinner = "winner";
  static const String eventShowdown = "showdown";
  static const String eventTurnSkipped = "turn_skipped";

  // =========================================================
  // ================= API ============================
  // =========================================================

  static const String apiLogin = "/auth/login";
  static const String apiRegister = "/auth/register";
  static const String apiJoinTable = "/game/join-table";
  static const String apiBalance = "/wallet/balance";

  // =========================================================
  // ================= TIME ============================
  // =========================================================

  static const Duration apiTimeout = Duration(seconds: 10);
  static const Duration socketReconnectDelay = Duration(seconds: 2);
}
