import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';

class SoundService {
  static final SoundService _instance = SoundService._internal();
  factory SoundService() => _instance;

  SoundService._internal();

  final AudioPlayer _player = AudioPlayer();

  // ================= STATE =================
  bool soundEnabled = true;
  double volume = 1.0;

  String? _lastPlayed;
  bool _isPlaying = false;

  // ================= INIT =================
  Future<void> init() async {
    await _player.setReleaseMode(ReleaseMode.stop);
    await _player.setVolume(volume);
  }

  // ================= TOGGLE =================
  void toggleSound(bool value) {
    soundEnabled = value;
  }

  void setVolume(double v) {
    volume = v.clamp(0.0, 1.0);
    _player.setVolume(volume);
  }

  // ================= SAFE PLAY =================
  Future<void> play(String file) async {
    if (!soundEnabled) return;

    try {
      // prevent spam sound (important for teen patti taps)
      if (_isPlaying && _lastPlayed == file) return;

      _isPlaying = true;
      _lastPlayed = file;

      await _player.stop();
      await _player.play(AssetSource(file));

      _player.onPlayerComplete.listen((_) {
        _isPlaying = false;
      });
    } catch (e) {
      if (kDebugMode) {
        print("Sound error: $e");
      }
      _isPlaying = false;
    }
  }

  // ================= GAME SOUND WRAPPERS =================
  void click() => play("sounds/click.mp3");
  void turn() => play("sounds/turn.mp3");
  void win() => play("sounds/win.mp3");
  void lose() => play("sounds/lose.mp3");
  void pack() => play("sounds/pack.mp3");

  // ================= ADVANCED SOUNDS =================
  void chip() => play("sounds/chip.mp3");
  void deal() => play("sounds/deal.mp3");
  void winBig() => play("sounds/win_big.mp3");

  // ================= CLEANUP =================
  void dispose() {
    _player.dispose();
  }
}
