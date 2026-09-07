import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/api_service.dart';

/// Real-time monitoring view for guardians/family/admins — shows all
/// currently active SOS incidents so a loved one (or campus security)
/// can track them live.
class GuardianDashboardScreen extends StatefulWidget {
  const GuardianDashboardScreen({super.key});

  @override
  State<GuardianDashboardScreen> createState() => _GuardianDashboardScreenState();
}

class _GuardianDashboardScreenState extends State<GuardianDashboardScreen> {
  List<dynamic> _incidents = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadIncidents();
  }

  Future<void> _loadIncidents() async {
    final apiService = context.read<ApiService>();
    final incidents = await apiService.getActiveIncidents();
    setState(() {
      _incidents = incidents;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Guardian Dashboard"),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadIncidents),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _incidents.isEmpty
              ? const Center(child: Text("No active incidents. Everyone is safe. 🛡️"))
              : ListView.builder(
                  itemCount: _incidents.length,
                  itemBuilder: (context, index) {
                    final incident = _incidents[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      child: ListTile(
                        leading: const Icon(Icons.warning, color: Colors.red),
                        title: Text("User: ${incident['user_id']}"),
                        subtitle: Text(
                          "Trigger: ${incident['trigger_type']}\n"
                          "Location: (${incident['latitude']}, ${incident['longitude']})\n"
                          "Since: ${incident['created_at']}",
                        ),
                        isThreeLine: true,
                        trailing: const Icon(Icons.chevron_right),
                      ),
                    );
                  },
                ),
    );
  }
}
