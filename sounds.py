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

def play_music_file(file_path):
    def _play_music():
        if sound is None:
            print(f"[Simulated Playback] Playing {file_path}")
            return
        try:
            sound.play_file(file_path, play_type=Sound.PLAY_WAIT_FOR_COMPLETE)
        except Exception as e:
            print(f"Error playing file: {e}")
    threading.Thread(target=_play_music, daemon=True).start()