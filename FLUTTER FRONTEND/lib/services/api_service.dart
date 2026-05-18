import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // ================= SINGLETON =================
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late final Dio dio;

  ApiService._internal() {
    dio = Dio(
      BaseOptions(
        baseUrl: "http://10.236.188.210:5000/api",
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        responseType: ResponseType.json,
        headers: {
          "Content-Type": "application/json",
        },
      ),
    );

    dio.interceptors.add(_authInterceptor());
  }

  // ================= TOKEN INTERCEPTOR =================
  InterceptorsWrapper _authInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString("token");

        if (token != null && token.isNotEmpty) {
          options.headers["Authorization"] = "Bearer $token";
        }

        return handler.next(options);
      },
    );
  }

  // ================= SAFE REQUEST HANDLER =================
  Future<Map<String, dynamic>> _safeRequest(
    Future<Response> Function() request,
  ) async {
    try {
      final response = await request();

      final data = response.data;

      if (data is Map<String, dynamic>) {
        return data;
      } else {
        return {
          "success": false,
          "message": "Invalid response format",
        };
      }
    } on DioException catch (e) {
      return {
        "success": false,
        "message": e.response?.data?["message"] ??
            e.message ??
            "Network error",
        "status": e.response?.statusCode,
      };
    } catch (e) {
      return {
        "success": false,
        "message": "Unexpected error",
        "error": e.toString(),
      };
    }
  }

  // =========================================================
  // ================= LOGIN ================================
  // =========================================================
  Future<Map<String, dynamic>> login(
    String phone,
    String password,
  ) async {
    final res = await _safeRequest(() {
      return dio.post(
        "/auth/login",
        data: {
          "phone": phone,
          "password": password,
        },
      );
    });

    if (res["token"] != null) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString("token", res["token"]);
    }

    return res;
  }

  // =========================================================
  // ================= REGISTER ==============================
  // =========================================================
  Future<Map<String, dynamic>> register(
    String name,
    String phone,
    String password,
  ) async {
    return _safeRequest(() {
      return dio.post(
        "/auth/register",
        data: {
          "name": name,
          "phone": phone,
          "password": password,
        },
      );
    });
  }

  // =========================================================
  // ================= JOIN TABLE ============================
  // =========================================================
  Future<Map<String, dynamic>> joinTable(int boot) async {
    return _safeRequest(() {
      return dio.post(
        "/game/join-table",
        data: {
          "boot": boot,
        },
      );
    });
  }

  // =========================================================
  // ================= WALLET ================================
  // =========================================================
  Future<Map<String, dynamic>> getBalance() async {
    return _safeRequest(() {
      return dio.get("/wallet/balance");
    });
  }

  // =========================================================
  // ================= LOGOUT ================================
  // =========================================================
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove("token");
  }
}
