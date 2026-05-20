class WithdrawalModel {

  // =====================================================
  // ================= BASIC ==============================
  // =====================================================

  final int id;

  final int userId;

  final String amount;

  final String paymentMethod;

  final String accountNumber;

  final String accountName;

  final String status;

  final String? adminNote;

  final String createdAt;

  final String updatedAt;

  // =====================================================
  // ================= CONSTRUCTOR ========================
  // =====================================================

  WithdrawalModel({

    required this.id,

    required this.userId,

    required this.amount,

    required this.paymentMethod,

    required this.accountNumber,

    required this.accountName,

    required this.status,

    required this.createdAt,

    required this.updatedAt,

    this.adminNote,
  });

  // =====================================================
  // ================= FROM JSON ==========================
  // =====================================================

  factory WithdrawalModel.fromJson(
    Map<String, dynamic> json,
  ) {

    return WithdrawalModel(

      id: _parseInt(json["id"]),

      userId: _parseInt(json["user_id"]),

      amount: json["amount"]?.toString() ?? "0.00",

      paymentMethod:
          json["payment_method"]?.toString() ?? "",

      accountNumber:
          json["account_number"]?.toString() ?? "",

      accountName:
          json["account_name"]?.toString() ?? "",

      status:
          json["status"]?.toString() ?? "pending",

      adminNote:
          json["admin_note"]?.toString(),

      createdAt:
          json["created_at"]?.toString() ?? "",

      updatedAt:
          json["updated_at"]?.toString() ?? "",
    );
  }

  // =====================================================
  // ================= TO JSON ============================
  // =====================================================

  Map<String, dynamic> toJson() {

    return {

      "id": id,

      "user_id": userId,

      "amount": amount,

      "payment_method": paymentMethod,

      "account_number": accountNumber,

      "account_name": accountName,

      "status": status,

      "admin_note": adminNote,

      "created_at": createdAt,

      "updated_at": updatedAt,
    };
  }

  // =====================================================
  // ================= COPY WITH ==========================
  // =====================================================

  WithdrawalModel copyWith({

    int? id,

    int? userId,

    String? amount,

    String? paymentMethod,

    String? accountNumber,

    String? accountName,

    String? status,

    String? adminNote,

    String? createdAt,

    String? updatedAt,
  }) {

    return WithdrawalModel(

      id: id ?? this.id,

      userId: userId ?? this.userId,

      amount: amount ?? this.amount,

      paymentMethod:
          paymentMethod ?? this.paymentMethod,

      accountNumber:
          accountNumber ?? this.accountNumber,

      accountName:
          accountName ?? this.accountName,

      status: status ?? this.status,

      adminNote: adminNote ?? this.adminNote,

      createdAt:
          createdAt ?? this.createdAt,

      updatedAt:
          updatedAt ?? this.updatedAt,
    );
  }

  // =====================================================
  // ================= HELPERS ============================
  // =====================================================

  bool get isPending =>
      status == "pending";

  bool get isApproved =>
      status == "approved";

  bool get isRejected =>
      status == "rejected";

  bool get isPaid =>
      status == "paid";

  // =====================================================
  // ================= PRIVATE ============================
  // =====================================================

  static int _parseInt(dynamic value) {

    if (value == null) {
      return 0;
    }

    return int.tryParse(
      value.toString(),
    ) ?? 0;
  }

  // =====================================================
  // ================= DEBUG ==============================
  // =====================================================

  @override
  String toString()
