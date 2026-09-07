import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/api_service.dart';
import '../services/location_service.dart';
import '../services/sensor_service.dart';
import '../services/voice_detection_service.dart';
import '../widgets/sos_button.dart';
import 'guardian_dashboard.dart';
import 'safe_route_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _sosActive = false;
  String _statusMessage = "You're protected. Stay safe.";

  final TextEditingController _myNumberController = TextEditingController();

  // Demo user + guardian contacts — replace with values from Firebase Auth
  // and the user's saved trusted-contacts list.
  final String _userId = "demo_user_001";
  final List<Map<String, dynamic>> _guardianContacts = [
    {"name": "Mom", "phone": "+911234567890"},
    {"name": "Best Friend", "phone": "+919876543210"},
  ];

  @override
  void initState() {
    super.initState();
    _initBackgroundMonitoring();
    _myNumberController.text = "+911234567890"; // change this to your number
  }

  @override
  void dispose() {
    _myNumberController.dispose();
    super.dispose();
  }

  void _initBackgroundMonitoring() {
    final sensorService = context.read<SensorService>();
    sensorService.startMonitoring(onFall: _handleAutoTrigger);

    final voiceService = context.read<VoiceDetectionService>();
    voiceService.startListening(onDistress: (text) => _handleAutoTrigger());
  }

  Future<void> _handleAutoTrigger() async {
    setState(() => _statusMessage = "Possible danger detected — confirm you're okay?");
    // In production: show a 10-second countdown dialog letting the user
    // cancel a false positive before auto-triggering the SOS.
    await _triggerSOS(triggerType: "auto_ai");
  }

  Future<void> _triggerSOS({String triggerType = "manual"}) async {
    setState(() {
      _sosActive = true;
      _statusMessage = "Sending SOS...";
    });

    final locationService = context.read<LocationService>();
    final apiService = context.read<ApiService>();

    final position = await locationService.getCurrentLocation();
    if (position == null) {
      setState(() {
        _sosActive = false;
        _statusMessage = "Location permission required for SOS.";
      });
      return;
    }

    // Ensure user's own phone number is included so they (or a monitored number)
    // receives the live location SMS/push.
    final guardiansToNotify = List<Map<String, dynamic>>.from(_guardianContacts);
    final myNumber = _myNumberController.text.trim();
    if (myNumber.isNotEmpty) {
      guardiansToNotify.insert(0, {"name": "You", "phone": myNumber});
    }

    final result = await apiService.triggerSOS(
      userId: _userId,
      latitude: position.latitude,
      longitude: position.longitude,
      triggerType: triggerType,
      guardianContacts: guardiansToNotify,
    );

    locationService.startLiveTracking((_) {
      // Stream live position updates to backend/Firestore here for the
      // Guardian Dashboard's real-time map.
    });

    setState(() {
      _statusMessage = "SOS sent! Guardians notified. Incident: "
          "${result['incident']?['id'] ?? 'unknown'}";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("EmpowerShield"),
        actions: [
          IconButton(
            icon: const Icon(Icons.map_outlined),
            tooltip: "Safe Route Planner",
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const SafeRouteScreen()),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.dashboard_outlined),
            tooltip: "Guardian Dashboard",
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const GuardianDashboardScreen()),
            ),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 48.0, vertical: 8.0),
              child: TextField(
                controller: _myNumberController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Your phone number',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            SosButton(
              isActive: _sosActive,
              onPressed: () => _triggerSOS(triggerType: "manual"),
            ),
            const SizedBox(height: 32),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                _statusMessage,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ),
            const SizedBox(height: 24),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              alignment: WrapAlignment.center,
              children: const [
                _FeatureChip(icon: Icons.mic, label: "Voice AI Active"),
                _FeatureChip(icon: Icons.sensors, label: "Fall Detection Active"),
                _FeatureChip(icon: Icons.wifi_off, label: "Offline Ready"),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _FeatureChip extends StatelessWidget {
  final IconData icon;
  final String label;
  const _FeatureChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: Icon(icon, size: 18, color: Colors.green.shade700),
      label: Text(label),
      backgroundColor: Colors.green.shade50,
    );
  }
}
