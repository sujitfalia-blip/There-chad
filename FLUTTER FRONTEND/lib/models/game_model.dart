class GameModel {
  final int tableId;
  final int currentPlayerId;
  final int remainingSeconds;

  GameModel({
    required this.tableId,
    required this.currentPlayerId,
    required this.remainingSeconds,
  });

  factory GameModel.fromJson(Map<String, dynamic> json) {
    return GameModel(
      tableId: json['table_id'],
      currentPlayerId: json['current_turn_player_id'],
      remainingSeconds: json['remaining_seconds'] ?? 0,
    );
  }
}
