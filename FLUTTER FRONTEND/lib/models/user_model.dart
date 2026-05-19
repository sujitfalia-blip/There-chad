class UserModel {
  final int id;
  final String name;
  final String phone;
  final int balance;

  UserModel({
    required this.id,
    required this.name,
    required this.phone,
    required this.balance,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      name: json['name'],
      phone: json['phone'],
      balance: json['balance'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      "id": id,
      "name": name,
      "phone": phone,
      "balance": balance,
    };
  }
}
