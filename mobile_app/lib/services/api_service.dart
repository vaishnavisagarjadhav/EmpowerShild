import 'dart:convert';
import 'package:http/http.dart' as http;

/// Central HTTP client for talking to the EmpowerShield FastAPI backend.
/// Change [baseUrl] to your deployed backend URL before release.
class ApiService {
  // Use 10.0.2.2 for Android emulator -> localhost, or your deployed backend URL.
  static const String baseUrl = "http://10.0.2.2:8000";

  Future<Map<String, dynamic>> triggerSOS({
    required String userId,
    required double latitude,
    required double longitude,
    String triggerType = "manual",
    bool offlineMode = false,
    List<Map<String, dynamic>> guardianContacts = const [],
    String? notes,
  }) async {
    final response = await http.post(
      Uri.parse("$baseUrl/sos/trigger"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "user_id": userId,
        "latitude": latitude,
        "longitude": longitude,
        "trigger_type": triggerType,
        "offline_mode": offlineMode,
        "guardian_contacts": guardianContacts,
        "notes": notes,
      }),
    );
    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> getRiskScore(double lat, double lng) async {
    final response = await http.post(
      Uri.parse("$baseUrl/ai/risk-score"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"latitude": lat, "longitude": lng}),
    );
    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> getSafeRoute(
      List<Map<String, dynamic>> waypoints) async {
    final response = await http.post(
      Uri.parse("$baseUrl/ai/safe-route"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"waypoints": waypoints}),
    );
    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> checkFallMotion({
    required List<Map<String, double>> accelWindow,
    required List<Map<String, double>> gyroWindow,
  }) async {
    final response = await http.post(
      Uri.parse("$baseUrl/detect/motion"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "accel_window": accelWindow,
        "gyro_window": gyroWindow,
      }),
    );
    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> checkVoiceDistress({
    required double screamConfidence,
    String transcribedText = "",
  }) async {
    final response = await http.post(
      Uri.parse("$baseUrl/detect/voice"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "scream_confidence": screamConfidence,
        "transcribed_text": transcribedText,
      }),
    );
    return jsonDecode(response.body);
  }

  Future<List<dynamic>> getActiveIncidents() async {
    final response = await http.get(Uri.parse("$baseUrl/sos/active"));
    final data = jsonDecode(response.body);
    return data["active_incidents"] ?? [];
  }
}
