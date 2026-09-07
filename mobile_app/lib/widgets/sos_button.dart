import 'package:flutter/material.dart';

/// Large, unmistakable One-Tap SOS button — the core interaction of the app.
class SosButton extends StatelessWidget {
  final VoidCallback onPressed;
  final bool isActive;

  const SosButton({super.key, required this.onPressed, this.isActive = false});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onPressed,
      onLongPress: onPressed,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        width: 180,
        height: 180,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: isActive ? Colors.red.shade900 : Colors.red.shade600,
          boxShadow: [
            BoxShadow(
              color: Colors.red.withOpacity(0.5),
              blurRadius: isActive ? 30 : 15,
              spreadRadius: isActive ? 8 : 2,
            ),
          ],
        ),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.shield, color: Colors.white, size: 42),
              const SizedBox(height: 6),
              Text(
                isActive ? "SENDING..." : "HOLD FOR\nSOS",
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
