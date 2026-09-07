import 'dart:async';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:sensors_plus/sensors_plus.dart';

/// Continuously samples accelerometer + gyroscope data and runs a
/// lightweight on-device threshold check (mirrors the TFLite model used
/// in the trained fall_detection.tflite for offline operation).
class SensorService extends ChangeNotifier {
  static const double fallAccelThreshold = 2.5; // g
  static const double fallGyroThreshold = 200.0; // deg/s

  final List<AccelerometerEvent> _accelWindow = [];
  final List<GyroscopeEvent> _gyroWindow = [];
  static const int windowSize = 50; // ~1 second at 50Hz

  StreamSubscription? _accelSub;
  StreamSubscription? _gyroSub;

  bool fallSuspected = false;
  void Function()? onFallDetected;

  void startMonitoring({void Function()? onFall}) {
    onFallDetected = onFall;

    _accelSub = accelerometerEventStream().listen((event) {
      _accelWindow.add(event);
      if (_accelWindow.length > windowSize) _accelWindow.removeAt(0);
      _evaluateWindow();
    });

    _gyroSub = gyroscopeEventStream().listen((event) {
      _gyroWindow.add(event);
      if (_gyroWindow.length > windowSize) _gyroWindow.removeAt(0);
    });
  }

  void _evaluateWindow() {
    if (_accelWindow.isEmpty || _gyroWindow.isEmpty) return;

    final peakAccel = _accelWindow
        .map((e) => sqrt(e.x * e.x + e.y * e.y + e.z * e.z) / 9.8) // convert to g
        .reduce(max);

    final peakGyro = _gyroWindow
        .map((e) => sqrt(e.x * e.x + e.y * e.y + e.z * e.z) * (180 / pi))
        .reduce(max);

    final detected = peakAccel >= fallAccelThreshold && peakGyro >= fallGyroThreshold;

    if (detected && !fallSuspected) {
      fallSuspected = true;
      onFallDetected?.call();
      notifyListeners();
    } else if (!detected) {
      fallSuspected = false;
    }
  }

  void stopMonitoring() {
    _accelSub?.cancel();
    _gyroSub?.cancel();
  }

  @override
  void dispose() {
    stopMonitoring();
    super.dispose();
  }
}
