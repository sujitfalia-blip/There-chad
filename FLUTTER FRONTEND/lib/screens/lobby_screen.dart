import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LobbyScreen extends StatefulWidget {
  const LobbyScreen({super.key});

  @override
  State<LobbyScreen> createState() => _LobbyScreenState();
}

class _LobbyScreenState extends State<LobbyScreen> {

  final List<int> boots = [1, 2, 5, 10, 20, 50, 100];

  bool isLoading = false;

  String? errorMessage;

  // ================= JOIN TABLE =================

  Future<void> joinTable(int boot) async {

    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {

      final res = await ApiService().joinTable(boot);

      if (res["table_id"] != null) {

        Navigator.pushNamed(
          context,
          "/game",
          arguments: res["table_id"],
        );

      } else {

        setState(() {
          errorMessage = res["message"] ?? "Failed to join table";
        });
      }

    } catch (e) {

      setState(() {
        errorMessage = e.toString();
      });

    } finally {

      setState(() {
        isLoading = false;
      });
    }
  }

  // ================= UI =================

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      backgroundColor: Colors.black,

      appBar: AppBar(
        title: const Text("Teen Patti Lobby"),
        backgroundColor: Colors.black,
        elevation: 0,
      ),

      body: Stack(

        children: [

          // ================= TABLE LIST =================

          ListView.builder(

            padding: const EdgeInsets.all(12),

            itemCount: boots.length,

            itemBuilder: (context, index) {

              final boot = boots[index];

              return Card(

                color: Colors.grey[900],

                margin: const EdgeInsets.symmetric(vertical: 8),

                child: ListTile(

                  title: Text(
                    "Boot ₹$boot",
                    style: const TextStyle(color: Colors.white),
                  ),

                  subtitle: const Text(
                    "Join table and start playing",
                    style: TextStyle(color: Colors.grey),
                  ),

                  trailing: ElevatedButton(

                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                    ),

                    onPressed: isLoading
                        ? null
                        : () => joinTable(boot),

                    child: const Text("Join"),
                  ),
                ),
              );
            },
          ),

          // ================= LOADING =================

          if (isLoading)
            Container(
              color: Colors.black54,
              child: const Center(
                child: CircularProgressIndicator(
                  color: Colors.green,
                ),
              ),
            ),

          // ================= ERROR =================

          if (errorMessage != null)
            Positioned(
              bottom: 20,
              left: 20,
              right: 20,
              child: Container(
                padding: const EdgeInsets.all(12),
                color: Colors.red,
                child: Text(
                  errorMessage!,
                  style: const TextStyle(color: Colors.white),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
