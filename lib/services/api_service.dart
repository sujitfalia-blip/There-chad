import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {

  // ================= SINGLETON =================

  static final ApiService _instance = ApiService._internal();

  factory ApiService() => _instance;

  late Dio dio;

  ApiService._internal() {
    dio = Dio(
      BaseOptions(
        baseUrl: "http://10.236.188.210:5000/api",
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {
          "Content-Type": "application/json"
        }
      ),
    );

    // ================= TOKEN INTERCEPTOR =================

    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {

          final prefs = await SharedPreferences.getInstance();

          final token = prefs.getString("token");

          if (token != null) {
            options.headers["Authorization"] = "Bearer $token";
          }

          return handler.next(options);
        },
      ),
    );
  }

  // =========================================================
  // ================= AUTH LOGIN ============================
  // =========================================================

  Future<Map<String, dynamic>> login(
      String phone, String password) async {

    try {

      final response = await dio.post(
        "/auth/login",
        data: {
          "phone": phone,
          "password": password
        },
      );

      final data = response.data;

      // save token
      if (data["token"] != null) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString("token", data["token"]);
      }

      return data;

    } catch (e) {

      return {
        "success": false,
        "message": "Login failed",
        "error": e.toString()
      };
    }
  }

  // =========================================================
  // ================= REGISTER ==============================
  // =========================================================

  Future<Map<String, dynamic>> register(
      String name, String phone, String password) async {

    try {

      final response = await dio.post(
        "/auth/register",
        data: {
          "name": name,
          "phone": phone,
          "password": password
        },
      );

      return response.data;

    } catch (e) {

      return {
        "success": false,
        "message": "Register failed",
        "error": e.toString()
      };
    }
  }

  // =========================================================
  // ================= JOIN TABLE ============================
  // =========================================================

  Future<Map<String, dynamic>> joinTable(int boot) async {

    try {

      final response = await dio.post(
        "/game/join-table",
        data: {
          "boot": boot
        },
      );

      return response.data;

    } catch (e) {

      return {
        "success": false,
        "message": "Join table failed",
        "error": e.toString()
      };
    }
  }

  // =========================================================
  // ================= WALLET ================================
  // =========================================================

  Future<Map<String, dynamic>> getBalance() async {

    try {

      final response = await dio.get("/wallet/balance");

      return response.data;

    } catch (e) {

      return {
        "success": false,
        "message": "Failed to fetch balance",
        "error": e.toString()
      };
    }
  }

  // =========================================================
  // ================= LOGOUT ================================
  // =========================================================

  Future<void> logout() async {

    final prefs = await SharedPreferences.getInstance();

    await prefs.remove("token");
  }
}
