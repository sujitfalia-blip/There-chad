import 'package:flutter/material.dart';
import 'app_loader.dart';

class AppStateWrapper extends StatelessWidget {
  final bool isLoading;
  final bool hasError;
  final String errorMessage;
  final Widget child;
  final VoidCallback onRetry;

  const AppStateWrapper({
    super.key,
    required this.isLoading,
    required this.hasError,
    required this.errorMessage,
    required this.child,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // ================= MAIN CONTENT =================
        child,

        // ================= LOADING OVERLAY =================
        if (isLoading)
          Container(
            color: Colors.black.withOpacity(0.5),
            child: const Center(
              child: AppLoader(),
            ),
          ),

        // ================= ERROR OVERLAY =================
        if (hasError)
          Container(
            color: Colors.black.withOpacity(0.7),
            child: Center(
              child: Container(
                margin: const EdgeInsets.all(20),
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.error_outline,
                      color: Colors.red,
                      size: 60,
                    ),
                    const SizedBox(height: 10),
                    Text(
                      errorMessage,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 16),
                    ),
                    const SizedBox(height: 15),
                    ElevatedButton(
                      onPressed: onRetry,
                      child: const Text("Retry"),
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}
