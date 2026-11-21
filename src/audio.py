"""
Audio Engine: Loads custom assets/drumroll.wav & assets/cymbal.wav if present,
manages the shuffled background Jukebox from assets/music/, and synthesises UI pops.
"""

import io
import math
import os
import random
import struct
import wave
import pygame

# Resolve project root cleanly whether launched from root or inside src/
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, ".."))


def _resolve_assets_dir():
    """Finds the assets directory, prioritising src/../assets/music."""
    root_assets = os.path.join(PROJECT_ROOT, "assets")
    cwd_assets = os.path.join(os.getcwd(), "assets")
    src_assets = os.path.join(SRC_DIR, "assets")

    # Prefer whichever assets folder actually contains a music/ subfolder with files
    for candidate in (root_assets, cwd_assets, src_assets):
        music_sub = os.path.join(candidate, "music")
        if os.path.isdir(music_sub) and os.listdir(music_sub):
            return candidate

    for candidate in (root_assets, cwd_assets, src_assets):
        if os.path.isdir(candidate):
            return candidate

    return root_assets


class Jukebox:
    """
    Background music jukebox that loads all audio files from assets/music/,
    shuffles them into a random order, plays through the entire playlist
    without repeats, and reshuffles once finished before looping.
    """

    SUPPORTED_EXTS = (".mp3", ".wav", ".ogg", ".flac", ".m4a")

    def __init__(self, music_dir=None, volume=0.25):
        # Force a clean stereo mixer initialisation if needed
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            except Exception as exc:
                print(f"[Jukebox] Mixer init warning: {exc}")

        print(f"[Jukebox] Active mixer config: {pygame.mixer.get_init()}")

        if music_dir is None:
            music_dir = os.path.join(_resolve_assets_dir(), "music")
        self.music_dir = os.path.abspath(music_dir)
        self.base_volume = volume
        self.muted = False
        self.tracks = []
        self.queue = []
        self.current_track = None
        self.last_played = None
        self.status_note = ""

        self.reload_tracks()

    def reload_tracks(self):
        """Scans assets/music/ for audio files and prepares the first shuffled queue."""
        os.makedirs(self.music_dir, exist_ok=True)
        try:
            all_files = os.listdir(self.music_dir)
            self.tracks = [
                os.path.join(self.music_dir, f)
                for f in all_files
                if os.path.isfile(os.path.join(self.music_dir, f))
                and f.lower().endswith(self.SUPPORTED_EXTS)
            ]
            print(f"[Jukebox] Folder: {self.music_dir}")
            print(f"[Jukebox] All files in folder: {all_files}")
            print(f"[Jukebox] Playable tracks found: {len(self.tracks)}")
        except Exception as exc:
            print(f"[Jukebox] Error scanning '{self.music_dir}': {exc}")
            self.tracks = []

        self._refill_queue()

    def _refill_queue(self):
        """Shuffles all tracks into a fresh cycle, avoiding immediate back-to-back repeats."""
        if not self.tracks:
            self.queue = []
            return

        self.queue = list(self.tracks)
        random.shuffle(self.queue)

        # Avoid playing the exact same song twice in a row across loop boundaries
        if len(self.queue) > 1 and self.queue[0] == self.last_played:
            self.queue.append(self.queue.pop(0))

    def play_next(self):
        """Pops the next shuffled track and starts playback via pygame.mixer.music."""
        if not self.tracks:
            self.status_note = f"No audio files in {self.music_dir}"
            return

        if not self.queue:
            self._refill_queue()

        next_path = self.queue.pop(0)
        track_title = os.path.splitext(os.path.basename(next_path))[0]
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(next_path)
            pygame.mixer.music.set_volume(0.0 if self.muted else self.base_volume)
            pygame.mixer.music.play()
            self.current_track = track_title
            self.last_played = next_path
            self.status_note = ""
            print(f"[Jukebox] Playing: {track_title} | busy={pygame.mixer.music.get_busy()}")
        except Exception as exc:
            print(f"[Jukebox] Failed to load '{next_path}': {exc}")
            self.current_track = f"Load Error ({os.path.basename(next_path)})"
            self.status_note = str(exc)
            if self.queue:
                self.play_next()

    def update(self):
        """Call once per frame to advance to the next shuffled song when one finishes."""
        if self.tracks and not pygame.mixer.music.get_busy():
            self.play_next()

    def set_ducked(self, ducked):
        """Lowers music volume during the drumroll & cymbal reveal."""
        if not self.tracks:
            return
        if self.muted:
            pygame.mixer.music.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(self.base_volume * 0.25 if ducked else self.base_volume)

    def toggle_mute(self):
        """Toggles background jukebox audio on/off."""
        self.muted = not self.muted
        if self.tracks:
            pygame.mixer.music.set_volume(0.0 if self.muted else self.base_volume)


def load_game_sfx():
    """
    Loads custom SFX files from the assets/ folder:
    - assets/drumroll.wav  (Starts when suspense sequence begins)
    - assets/cymbal.wav    (Triggers when results pop up)
    Falls back gracefully if files are missing.
    """
    sfx = {}
    assets_dir = _resolve_assets_dir()
    drumroll_path = os.path.join(assets_dir, "drumroll.wav")
    cymbal_path = os.path.join(assets_dir, "cymbal.wav")

    try:
        if os.path.exists(drumroll_path):
            sfx["drumroll"] = pygame.mixer.Sound(drumroll_path)
        else:
            sfx["drumroll"] = None

        if os.path.exists(cymbal_path):
            sfx["cymbal"] = pygame.mixer.Sound(cymbal_path)
        else:
            sfx["cymbal"] = None
    except Exception:
        sfx["drumroll"] = None
        sfx["cymbal"] = None

    return sfx


def generate_pop_sound(freq=520, duration_sec=0.06, sample_rate=44100):
    """Generates a crisp UI pop sound when cycling options."""
    try:
        num_samples = int(duration_sec * sample_rate)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                env = math.exp(-t * 55.0)
                val = math.sin(2.0 * math.pi * (freq + t * 900.0) * t) * env * 0.45
                frames += struct.pack("<h", int(max(-0.98, min(0.98, val)) * 32767))
            wav_file.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(file=buf)
    except Exception:
        return None