import 'package:flutter/material.dart';

class PlayerCardWidget extends StatelessWidget {
  final String name;
  final bool isTurn;
  final bool isPacked;

  const PlayerCardWidget({
    super.key,
    required this.name,
    required this.isTurn,
    required this.isPacked,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: isTurn ? Colors.green : Colors.grey.shade800,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Text(name,
              style: const TextStyle(color: Colors.white)),
          if (isPacked)
            const Text("PACKED",
                style: TextStyle(color: Colors.red)),
        ],
      ),
    );
  }
}
