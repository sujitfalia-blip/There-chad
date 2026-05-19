import 'package:flutter/material.dart';
import '../controllers/game_controller.dart';

class TimerWidget extends StatelessWidget {
  final GameController controller = GameController();

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      stream: controller.stream,
      builder: (context, snapshot) {
        return Text(
          "${controller.remainingSeconds}s",
          style: const TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Colors.red,
          ),
        );
      },
    );
  }
}
