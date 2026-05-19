class TableModel {
  final int id;
  final int bootAmount;
  final String status;
  final int totalPlayers;

  TableModel({
    required this.id,
    required this.bootAmount,
    required this.status,
    required this.totalPlayers,
  });

  factory TableModel.fromJson(Map<String, dynamic> json) {
    return TableModel(
      id: json['id'],
      bootAmount: json['boot_amount'] ?? 0,
      status: json['status'] ?? "waiting",
      totalPlayers: json['total_players'] ?? 0,
    );
  }
}
