import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // ================= SINGLETON =================
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late final Dio dio;

  final Map<String, dynamic> _cache = {};

  // 🔥 PRODUCTION BASE URL (RENDER)
  static const String baseUrl = "https://there-chad.onrender.com/api";

  ApiService._internal() {
    dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
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

  // ================= AUTH =================
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

  // ================= LOG =================
  InterceptorsWrapper _logInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) {
        options.extra["start"] = DateTime.now().millisecondsSinceEpoch;
        handler.next(options);
      },
      onResponse: (response, handler) {
        final start = response.requestOptions.extra["start"];
        final time =
            DateTime.now().millisecondsSinceEpoch - (start ?? 0);

        if (time > 2000) {
          print("⚠️ SLOW API: ${response.requestOptions.path} ${time}ms");
        }

        handler.next(response);
      },
      onError: (error, handler) {
        print("❌ API ERROR: ${error.requestOptions.path}");
        handler.next(error);
      },
    );
  }

  // ================= RETRY =================
  Future<Response> _retry(Future<Response> Function() req) async {
    int retry = 2;

    while (true) {
      try {
        return await req();
      } catch (_) {
        if (retry == 0) rethrow;
        retry--;
        await Future.delayed(const Duration(milliseconds: 500));
      }
    }
  }

  // ================= SAFE REQUEST =================
  Future<Map<String, dynamic>> _safe(
    String key,
    Future<Response> Function() req,
  ) async {
    try {
      if (_cache.containsKey(key)) return _cache[key];

      final res = await _retry(req);
      final data = res.data;

      if (data is Map<String, dynamic>) {
        _cache[key] = data;
        return data;
      }

      return {"success": false, "message": "Invalid response"};
    } on DioException catch (e) {
      return {
        "success": false,
        "message": e.response?.data?["message"] ?? e.message,
        "status": e.response?.statusCode,
      };
    }
  }

  // ================= API =================
  Future<Map<String, dynamic>> login(String phone, String password) async {
    final res = await _safe(
      "login_$phone",
      () => dio.post("/auth/login",
          data: {"phone": phone, "password": password}),
    );

    if (res["token"] != null) {
      final prefs = await SharedPreferences.getInstance();
      prefs.setString("token", res["token"]);
    }

    return res;
  }

  Future<Map<String, dynamic>> register(
      String name, String phone, String password) {
    return _safe(
      "register_$phone",
      () => dio.post("/auth/register",
          data: {"name": name, "phone": phone, "password": password}),
    );
  }

  Future<Map<String, dynamic>> joinTable(int boot) {
    return _safe(
      "join_$boot",
      () => dio.post("/game/join-table", data: {"boot": boot}),
    );
  }

  Future<Map<String, dynamic>> getBalance() {
    return _safe(
      "balance",
      () => dio.get("/wallet/balance"),
    );
  }

  void clearCache() => _cache.clear();

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    prefs.remove("token");
    clearCache();
  }
}
