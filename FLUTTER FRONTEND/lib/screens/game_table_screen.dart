import 'package:flutter/material.dart';
import '../services/socket_service.dart';

class GameTable extends StatefulWidget {
  final String tableId;

  const GameTable({super.key, required this.tableId});

  @override
  State<GameTable> createState() => _GameTableState();
}

class _GameTableState extends State<GameTable> {

  final SocketService socketService = SocketService();

  List players = [];
  bool isConnected = false;
  String status = "Connecting...";

  @override
  void initState() {
    super.initState();
    initSocket();
  }

  void initSocket() {
    socketService.connect();

    setState(() {
      isConnected = true;
      status = "Connected";
    });

    socketService.joinTable(widget.tableId);

    socketService.onPlayerJoined((data) {
      if (!mounted) return;

      setState(() {
        players.add(data);
      });
    });
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: const Color(0xFF0B3D2E),

      appBar: AppBar(
        title: Text("Table #${widget.tableId}"),
        backgroundColor: Colors.black,
      ),

      body: Column(

        children: [

          // ================= STATUS =================
          Container(
            margin: const EdgeInsets.all(12),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.black54,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(status, style: const TextStyle(color: Colors.white)),
                Text("Players: ${players.length}",
                    style: const TextStyle(color: Colors.amber)),
              ],
            ),
          ),

          const SizedBox(height: 10),

          // ================= GAME TABLE =================
          Expanded(
            child: Center(
              child: Stack(

                alignment: Alignment.center,

                children: [

                  // 🟢 Poker Table
                  Container(
                    width: 280,
                    height: 280,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.green[800],
                      border: Border.all(color: Colors.white24, width: 3),
                    ),
                  ),

                  // 🧑 Players around table
                  ...List.generate(players.length, (index) {

                    double angle = (index / players.length) * 3.14 * 2;

                    double radius = 140;

                    return Positioned(
                      left: 150 + radius * (Math().cos(angle)),
                      top: 150 + radius * (Math().sin(angle)),

                      child: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.black87,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Column(
                          children: [
                            const Icon(Icons.person, color: Colors.white),
                            Text(
                              "P${index + 1}",
                              style: const TextStyle(color: Colors.white),
                            )
                          ],
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),

          // ================= ACTION BAR =================
          Container(
            padding: const EdgeInsets.all(12),
            color: Colors.black87,

            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,

              children: [

                ElevatedButton(
                  onPressed: () {},
                  child: const Text("BET"),
                ),

                ElevatedButton(
                  onPressed: () {},
                  child: const Text("PACK"),
                ),

                ElevatedButton(
                  onPressed: () {},
                  child: const Text("SEE"),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
