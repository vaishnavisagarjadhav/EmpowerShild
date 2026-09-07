import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/api_service.dart';

/// Lets the user check the AI risk score of their current route and see
/// which segments are flagged as high-risk crime hotspots.
class SafeRouteScreen extends StatefulWidget {
  const SafeRouteScreen({super.key});

  @override
  State<SafeRouteScreen> createState() => _SafeRouteScreenState();
}

class _SafeRouteScreenState extends State<SafeRouteScreen> {
  Map<String, dynamic>? _routeResult;
  bool _loading = false;

  // Demo waypoints — in production these come from Google Maps Directions
  // API polyline sampling between the user's origin and destination.
  final List<Map<String, dynamic>> _demoWaypoints = [
    {"lat": 28.6139, "lng": 77.2090, "label": "Start"},
    {"lat": 28.6229, "lng": 77.2180, "label": "Midpoint"},
    {"lat": 28.6339, "lng": 77.2280, "label": "Destination"},
  ];

  Future<void> _checkRoute() async {
    setState(() => _loading = true);
    final apiService = context.read<ApiService>();
    final result = await apiService.getSafeRoute(_demoWaypoints);
    setState(() {
      _routeResult = result;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Safe Route Planner")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ElevatedButton.icon(
              onPressed: _loading ? null : _checkRoute,
              icon: const Icon(Icons.route),
              label: Text(_loading ? "Analyzing route..." : "Analyze My Route"),
            ),
            const SizedBox(height: 20),
            if (_routeResult != null) ...[
              Text(
                "Overall risk score: ${_routeResult!['overall_risk_score']}",
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Text(_routeResult!['recommendation'] ?? ""),
              const SizedBox(height: 16),
              Expanded(
                child: ListView.builder(
                  itemCount: (_routeResult!['waypoints'] as List).length,
                  itemBuilder: (context, index) {
                    final wp = _routeResult!['waypoints'][index];
                    final isHigh = wp['risk_level'] == 'HIGH';
                    return Card(
                      color: isHigh ? Colors.red.shade50 : Colors.green.shade50,
                      child: ListTile(
                        leading: Icon(
                          isHigh ? Icons.warning_amber : Icons.check_circle,
                          color: isHigh ? Colors.red : Colors.green,
                        ),
                        title: Text(wp['label'] ?? "Waypoint"),
                        subtitle: Text(
                          "Risk: ${wp['risk_level']} (${wp['risk_score']})",
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
