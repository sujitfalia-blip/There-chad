import 'package:flutter/material.dart';

import '../screens/lobby_screen.dart';
import '../screens/game_table_screen.dart';

class AppRoutes {
  // =========================================================
  // ================= ROUTE NAMES ===========================
  // =========================================================

  static const String lobby = "/";
  static const String table = "/table";

  // =========================================================
  // ================= ROUTE GENERATOR =======================
  // =========================================================

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {

      // ================= LOBBY =================
      case lobby:
        return _buildRoute(const LobbyScreen());

      // ================= GAME TABLE =================
      case table:
        final args = settings.arguments as Map<String, dynamic>?;

        final tableId = args?["tableId"];
        final myPlayerId = args?["playerId"];

        if (tableId == null || myPlayerId == null) {
          return _errorRoute("Missing table data");
        }

        return _buildRoute(
          GameTableScreen(
            tableId: tableId,
            myPlayerId: myPlayerId,
          ),
        );

      // ================= DEFAULT =================
      default:
        return _errorRoute("Route Not Found");
    }
  }

  // =========================================================
  // ================= ROUTE BUILDER =========================
  // =========================================================

  static Route<dynamic> _buildRoute(Widget page) {
    return MaterialPageRoute(
      builder: (_) => page,
      settings: const RouteSettings(),
    );
  }

  // =========================================================
  // ================= ERROR ROUTE ===========================
  // =========================================================

  static Route<dynamic> _errorRoute(String message) {
    return MaterialPageRoute(
      builder: (_) => Scaffold(
        body: Center(
          child: Text(
            message,
            style: const TextStyle(
              color: Colors.red,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}
