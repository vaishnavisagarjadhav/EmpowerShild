import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart';

import 'screens/home_screen.dart';
import 'services/api_service.dart';
import 'services/location_service.dart';
import 'services/sensor_service.dart';
import 'services/voice_detection_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Uncomment once firebase_options.dart is generated via `flutterfire configure`
  // await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  runApp(const EmpowerShieldApp());
}

class EmpowerShieldApp extends StatelessWidget {
  const EmpowerShieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider(create: (_) => ApiService()),
        ChangeNotifierProvider(create: (_) => LocationService()),
        ChangeNotifierProvider(create: (_) => SensorService()),
        ChangeNotifierProvider(create: (_) => VoiceDetectionService()),
      ],
      child: MaterialApp(
        title: 'EmpowerShield',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorSchemeSeed: const Color(0xFF1E4D6B),
          useMaterial3: true,
        ),
        home: const HomeScreen(),
      ),
    );
  }
}
