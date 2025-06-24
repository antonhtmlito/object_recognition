import threading

try:
    from ev3dev2.sound import Sound
    sound = Sound()
except ImportError:
    sound = None

def play_sound_thread(text=None, tones=None):
    def _play():
        if sound is None:
            print(f"[Simulated Sound] {text or tones}")
            return
        if text:
            sound.speak(text)
        elif tones:
            sound.tone(tones)
    threading.Thread(target=_play, daemon=True).start()

def play_music_file(file_path, volume=100):
    def _play_music():
        if sound is None:
            print(f"[Simulated Playback] Playing {file_path} at volume{volume}")
            return
        try:
            sound.volume = volume
            sound.play_file(
                file_path,
                volume=volume,
                play_type=Sound.PLAY_NO_WAIT_FOR_COMPLETE
            )
        except Exception as e:
            print(f"Error playing file {file_path}: {e}")
    threading.Thread(target=_play_music, daemon=True).start()