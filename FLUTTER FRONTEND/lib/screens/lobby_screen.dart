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

  Future<void> joinTable(int boot) async {
    if (isLoading) return;

    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final res = await ApiService().joinTable(boot);

      final tableId = res["table_id"];

      if (tableId != null) {
        if (!mounted) return;

        Navigator.pushNamed(
          context,
          "/game",
          arguments: tableId,
        );
      } else {
        setState(() {
          errorMessage = res["message"] ?? "Failed to join table";
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = "Something went wrong: $e";
      });
    } finally {
      if (mounted) {
        setState(() {
          isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0B0B),

      appBar: AppBar(
        title: const Text("Teen Patti Lobby"),
        backgroundColor: Colors.black,
        elevation: 0,
      ),

      body: Stack(
        children: [
          // ================= TABLE LIST =================
          ListView.separated(
            padding: const EdgeInsets.all(12),
            itemCount: boots.length,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final boot = boots[index];

              return Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A1A),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.greenAccent.withOpacity(0.4)),
                ),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),

                  title: Text(
                    "Boot ₹$boot",
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  subtitle: const Text(
                    "Join table and start playing instantly",
                    style: TextStyle(color: Colors.grey),
                  ),

                  trailing: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 18,
                        vertical: 10,
                      ),
                    ),
                    onPressed: isLoading ? null : () => joinTable(boot),
                    child: const Text("JOIN"),
                  ),
                ),
              );
            },
          ),

          // ================= LOADING OVERLAY =================
          if (isLoading)
            Container(
              color: Colors.black54,
              child: const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(color: Colors.green),
                    SizedBox(height: 10),
                    Text(
                      "Joining Table...",
                      style: TextStyle(color: Colors.white),
                    )
                  ],
                ),
              ),
            ),

          // ================= ERROR =================
          if (errorMessage != null)
            Positioned(
              bottom: 20,
              left: 16,
              right: 16,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.9),
                  borderRadius: BorderRadius.circular(12),
                ),
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
