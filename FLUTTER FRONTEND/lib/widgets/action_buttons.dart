import 'package:flutter/material.dart';
import '../controllers/game_controller.dart';

class ActionButtons extends StatelessWidget {
  final GameController controller = GameController();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        ElevatedButton(
          onPressed: controller.pack,
          child: const Text("PACK"),
        ),
        ElevatedButton(
          onPressed: controller.showCard,
          child: const Text("SHOW"),
        ),
      ],
    );
  }
}
