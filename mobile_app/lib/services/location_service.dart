import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';

/// Handles GPS permission, live location capture, and continuous
/// live-tracking used by the Guardian Dashboard during an active incident.
class LocationService extends ChangeNotifier {
  Position? currentPosition;
  StreamSubscription<Position>? _positionStream;
  bool isTracking = false;

  Future<bool> ensurePermission() async {
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    return permission == LocationPermission.always ||
        permission == LocationPermission.whileInUse;
  }

  Future<Position?> getCurrentLocation() async {
    if (!await ensurePermission()) return null;
    currentPosition = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );
    notifyListeners();
    return currentPosition;
  }

  /// Starts continuous location streaming — used the moment an SOS
  /// is triggered so the Guardian Dashboard sees live movement.
  void startLiveTracking(void Function(Position) onUpdate) {
    if (isTracking) return;
    isTracking = true;
    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 5, // meters
      ),
    ).listen((position) {
      currentPosition = position;
      onUpdate(position);
      notifyListeners();
    });
  }

  void stopLiveTracking() {
    _positionStream?.cancel();
    isTracking = false;
    notifyListeners();
  }

  @override
  void dispose() {
    _positionStream?.cancel();
    super.dispose();
  }
}
