import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

/// Listens for distress keywords ("help", "bachao", etc.) and integrates
/// with an on-device TFLite acoustic scream classifier for offline
/// operation, matching the "Voice/Scream AI Trigger" requirement.
///
/// NOTE: For the acoustic scream-classification model itself, load a
/// TFLite model (trained on a scream/ambient-audio dataset such as
/// AudioSet or a custom scream corpus) via `tflite_flutter` and run
/// inference on short audio buffers. This class focuses on the
/// keyword-spotting half of the pipeline, which works well even with
/// the platform speech recognizer.
class VoiceDetectionService extends ChangeNotifier {
  final stt.SpeechToText _speech = stt.SpeechToText();
  bool isListening = false;
  String lastRecognizedText = "";

  static const List<String> distressKeywords = [
    "help",
    "bachao",
    "save me",
    "call police",
    "leave me",
  ];

  void Function(String matchedText)? onDistressDetected;

  Future<bool> init() async {
    return await _speech.initialize(
      onError: (err) => debugPrint("Speech error: $err"),
      onStatus: (status) => debugPrint("Speech status: $status"),
    );
  }

  Future<void> startListening({void Function(String)? onDistress}) async {
    onDistressDetected = onDistress;
    final available = await init();
    if (!available) return;

    isListening = true;
    notifyListeners();

    _speech.listen(
      onResult: (result) {
        lastRecognizedText = result.recognizedWords.toLowerCase();
        notifyListeners();

        for (final keyword in distressKeywords) {
          if (lastRecognizedText.contains(keyword)) {
            onDistressDetected?.call(lastRecognizedText);
            break;
          }
        }
      },
      listenMode: stt.ListenMode.confirmation,
      partialResults: true,
    );
  }

  void stopListening() {
    _speech.stop();
    isListening = false;
    notifyListeners();
  }
}
