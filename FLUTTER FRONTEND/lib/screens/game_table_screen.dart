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

  // ================= SOCKET INIT =================

  void initSocket() {

    socketService.connect();

    setState(() {
      isConnected = true;
      status = "Connected to Table";
    });

    socketService.joinTable(widget.tableId);

    socketService.onPlayerJoined((data) {

      if (!mounted) return;

      setState(() {
        players.add(data);
      });
    });
  }

  // ================= UI =================

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      backgroundColor: const Color(0xFF0B3D2E),

      appBar: AppBar(
        title: Text("Table #${widget.tableId}"),
        backgroundColor: Colors.black,
        elevation: 0,
      ),

      body: Stack(

        children: [

          // ================= TABLE BACKGROUND =================

          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Color(0xFF0B3D2E),
                  Color(0xFF06281E),
                ],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            ),
          ),

          // ================= MAIN CONTENT =================

          Column(

            children: [

              const SizedBox(height: 20),

              // ================= STATUS BAR =================

              Container(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [

                    Text(
                      status,
                      style: const TextStyle(color: Colors.white),
                    ),

                    Text(
                      "Players: ${players.length}",
                      style: const TextStyle(
                        color: Colors.amber,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // ================= TABLE VIEW =================

              Expanded(

                child: GridView.builder(

                  padding: const EdgeInsets.all(16),

                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                    childAspectRatio: 1.5,
                  ),

                  itemCount: players.length,

                  itemBuilder: (context, index) {

                    final player = players[index];

                    return Container(

                      decoration: BoxDecoration(
                        color: Colors.black87,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: Colors.greenAccent,
                          width: 1,
                        ),
                      ),

                      child: Column(

                        mainAxisAlignment: MainAxisAlignment.center,

                        children: [

                          const Icon(
                            Icons.person,
                            color: Colors.white,
                            size: 30,
                          ),

                          const SizedBox(height: 8),

                          Text(
                            "Player ${index + 1}",
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),

                          const SizedBox(height: 4),

                          Text(
                            player.toString(),
                            style: const TextStyle(
                              color: Colors.grey,
                              fontSize: 12,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
