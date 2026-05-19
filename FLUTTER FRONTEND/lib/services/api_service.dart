import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // ================= SINGLETON =================
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late final Dio dio;

  // ================= SIMPLE CACHE =================
  final Map<String, dynamic> _cache = {};

  ApiService._internal() {
    dio = Dio(
      BaseOptions(
        baseUrl: "http://10.236.188.210:5000/api",
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        sendTimeout: const Duration(seconds: 10),
        responseType: ResponseType.json,
        headers: {
          "Content-Type": "application/json",
        },
      ),
    );

    dio.interceptors.add(_authInterceptor());
    dio.interceptors.add(_logInterceptor());
  }

  // ================= AUTH INTERCEPTOR =================
  InterceptorsWrapper _authInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString("token");

        if (token != null && token.isNotEmpty) {
          options.headers["Authorization"] = "Bearer $token";
        }

        handler.next(options);
      },
    );
  }

  // ================= LOG + SLOW REQUEST DETECTOR =================
  InterceptorsWrapper _logInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) {
        options.extra["start_time"] = DateTime.now().millisecondsSinceEpoch;
        handler.next(options);
      },
      onResponse: (response, handler) {
        final start = response.requestOptions.extra["start_time"];
        final duration =
            DateTime.now().millisecondsSinceEpoch - (start ?? 0);

        if (duration > 2000) {
          // slow API warning
          print("⚠️ SLOW API: ${response.requestOptions.path} = ${duration}ms");
        }

        handler.next(response);
      },
      onError: (error, handler) {
        print("❌ API ERROR: ${error.requestOptions.path}");
        handler.next(error);
      },
    );
  }

  // ================= RETRY LOGIC =================
  Future<Response> _retryRequest(
    Future<Response> Function() request,
  ) async {
    int retries = 2;

    while (true) {
      try {
        return await request();
      } catch (e) {
        if (retries == 0) rethrow;
        retries--;
        await Future.delayed(const Duration(milliseconds: 500));
      }
    }
  }

  // ================= SAFE REQUEST =================
  Future<Map<String, dynamic>> _safeRequest(
    String cacheKey,
    Future<Response> Function() request,
  ) async {
    try {
      // ===== CACHE HIT =====
      if (_cache.containsKey(cacheKey)) {
        return _cache[cacheKey];
      }

      final response = await _retryRequest(() => request());

      final data = response.data;

      if (data is Map<String, dynamic>) {
        _cache[cacheKey] = data; // cache store
        return data;
      }

      return {
        "success": false,
        "message": "Invalid response format",
      };
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
    final res = await _safeRequest(
      "login_$phone",
      () => dio.post(
        "/auth/login",
        data: {
          "phone": phone,
          "password": password,
        },
      ),
    );

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
    return _safeRequest(
      "register_$phone",
      () => dio.post(
        "/auth/register",
        data: {
          "name": name,
          "phone": phone,
          "password": password,
        },
      ),
    );
  }

  // =========================================================
  // ================= JOIN TABLE ============================
  // =========================================================
  Future<Map<String, dynamic>> joinTable(int boot) async {
    return _safeRequest(
      "join_$boot",
      () => dio.post(
        "/game/join-table",
        data: {
          "boot": boot,
        },
      ),
    );
  }

  // =========================================================
  // ================= WALLET ================================
  // =========================================================
  Future<Map<String, dynamic>> getBalance() async {
    return _safeRequest(
      "balance",
      () => dio.get("/wallet/balance"),
    );
  }

  // =========================================================
  // ================= CLEAR CACHE ===========================
  // =========================================================
  void clearCache() {
    _cache.clear();
  }

  // =========================================================
  // ================= LOGOUT ================================
  // =========================================================
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove("token");
    clearCache();
  }
}
