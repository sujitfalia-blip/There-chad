class PlayerModel {
  final int playerId;
  final String name;
  final bool isActive;
  final bool isPacked;
  final bool isTurn;

  PlayerModel({
    required this.playerId,
    required this.name,
    required this.isActive,
    required this.isPacked,
    required this.isTurn,
  });

  factory PlayerModel.fromJson(Map<String, dynamic> json) {
    return PlayerModel(
      playerId: json['player_id'],
      name: json['name'] ?? "",
      isActive: json['is_active'] ?? false,
      isPacked: json['is_packed'] ?? false,
      isTurn: json['is_turn_active'] ?? false,
    );
  }
}
