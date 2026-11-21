"""
APPEARANCE MATTERS: THE BOOTS ROOM — HTML5 Web Build Generator
=============================================================
Reads the main repo's src/config.py, src/combos.json, and assets/,
uses pydub to convert MP3 music tracks into web-ready OGG files,
and outputs a self-contained HTML5 Canvas web build into dist/web/.

Usage:
    python build_web.py
"""

import json
import os
import shutil
import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
DIST_WEB_DIR = os.path.join(ROOT_DIR, "dist", "web")
DIST_ASSETS_DIR = os.path.join(DIST_WEB_DIR, "assets")
DIST_MUSIC_DIR = os.path.join(DIST_ASSETS_DIR, "music")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    from config import SKIN_TONES, BOOT_TYPES, BOOT_COLORS, STICKY_MATERIALS, QUESTIONS
except ImportError as exc:
    print(f"[Build Error] Could not import src/config.py: {exc}")
    sys.exit(1)


def load_combos_data():
    """Loads src/combos.json safely with UTF-8 encoding."""
    combos_path = os.path.join(SRC_DIR, "combos.json")
    try:
        with open(combos_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
            return data.get("combos", [])
    except Exception as exc:
        print(f"[Build Warning] Could not read src/combos.json ({exc}); using default brackets.")
        return []


def prepare_audio_and_assets():
    """
    Copies SFX/icons and uses pydub to convert any .mp3 tracks in assets/music/
    into .ogg files inside dist/web/assets/music/.
    Returns a list of relative web paths for the Jukebox playlist.
    """
    os.makedirs(DIST_MUSIC_DIR, exist_ok=True)
    playlist = []

    # Copy drumroll.wav, cymbal.wav, and icon.ico if present
    for asset_name in ("drumroll.wav", "cymbal.wav", "icon.ico"):
        src_file = os.path.join(ASSETS_DIR, asset_name)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, os.path.join(DIST_ASSETS_DIR, asset_name))

    music_candidates = [
        os.path.join(ASSETS_DIR, "music"),
        os.path.join(os.getcwd(), "assets", "music"),
        os.path.join(SRC_DIR, "assets", "music"),
    ]
    music_src_dir = None
    for cand in music_candidates:
        if os.path.isdir(cand):
            music_src_dir = cand
            break

    if music_src_dir is None:
        print("[Build] No assets/music/ folder found in checked locations:")
        for cand in music_candidates:
            print(f"  - {cand}")
        print("[Build] Create assets/music/ and add .mp3/.ogg/.wav/.flac/.m4a files to bundle tracks.")
        return playlist

    print(f"[Build] Scanning music folder: {music_src_dir}")

    # Try loading pydub for MP3 -> OGG conversion
    AudioSegment = None
    try:
        from pydub import AudioSegment as _AudioSegment
        AudioSegment = _AudioSegment
    except Exception as exc:
        print(f"[Build Note] pydub import failed ({exc}) under {sys.executable}.")
        print("[Build Note] Fix: run `python -m pip install pydub pyaudioop audioop-lts` using the same python command.")

    supported_exts = (".ogg", ".wav", ".mp3", ".flac", ".m4a")
    all_entries = sorted(os.listdir(music_src_dir))
    if not all_entries:
        print(f"[Build] Folder '{music_src_dir}' exists but is completely empty.")
        return playlist

    for entry in all_entries:
        full_path = os.path.join(music_src_dir, entry)
        if not os.path.isfile(full_path):
            print(f"[Build Skip] '{entry}' is a subfolder, not a file.")
            continue

        stem, ext = os.path.splitext(entry)
        ext_low = ext.lower()
        if ext_low not in supported_exts:
            print(f"[Build Skip] '{entry}' has unsupported extension '{ext_low}' (supported: {', '.join(supported_exts)}).")
            continue

        if ext_low in (".ogg", ".wav"):
            dest_name = f"{stem}{ext_low}"
            shutil.copy2(full_path, os.path.join(DIST_MUSIC_DIR, dest_name))
            playlist.append({"title": stem, "url": f"assets/music/{dest_name}"})
        elif ext_low == ".mp3":
            out_ogg = os.path.join(DIST_MUSIC_DIR, f"{stem}.ogg")
            if AudioSegment is not None:
                try:
                    print(f"[Pydub] Converting '{entry}' -> '{stem}.ogg'...")
                    sound = AudioSegment.from_mp3(full_path)
                    sound.export(out_ogg, format="ogg")
                    playlist.append({"title": stem, "url": f"assets/music/{stem}.ogg"})
                    continue
                except Exception as exc:
                    print(f"[Pydub Warning] Could not convert '{entry}' ({exc}); copying raw .mp3 fallback.")
            # Fallback: copy .mp3 directly (modern HTML5 <audio> supports .mp3 natively)
            shutil.copy2(full_path, os.path.join(DIST_MUSIC_DIR, entry))
            playlist.append({"title": stem, "url": f"assets/music/{entry}"})
        else:
            # .flac or .m4a: convert to .ogg via pydub if possible, else copy directly
            out_ogg = os.path.join(DIST_MUSIC_DIR, f"{stem}.ogg")
            fmt = ext_low.lstrip(".")
            if AudioSegment is not None:
                try:
                    print(f"[Pydub] Converting '{entry}' -> '{stem}.ogg'...")
                    sound = AudioSegment.from_file(full_path, format=fmt)
                    sound.export(out_ogg, format="ogg")
                    playlist.append({"title": stem, "url": f"assets/music/{stem}.ogg"})
                    continue
                except Exception as exc:
                    print(f"[Pydub Warning] Could not convert '{entry}' ({exc}); copying '{entry}' directly.")
            shutil.copy2(full_path, os.path.join(DIST_MUSIC_DIR, entry))
            playlist.append({"title": stem, "url": f"assets/music/{entry}"})

    return playlist


def generate_html(game_payload):
    """Generates the complete self-contained HTML5/Canvas/JS game string."""
    payload_json = json.dumps(game_payload, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Appearance Matters: The Boots Room</title>
  <link rel="icon" href="assets/icon.ico" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{
      box-sizing: border-box;
    }}
    body {{
      font-family: 'Inter', sans-serif;
      background-color: #12141C;
      color: #F8F5EE;
      user-select: none;
      margin: 0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 0.75rem;
    }}
    @media (min-width: 640px) {{
      body {{
        padding: 1.5rem;
      }}
    }}
    .hidden {{
      display: none !important;
    }}
    .flex {{
      display: flex;
    }}
    .flex-col {{
      flex-direction: column;
    }}
    .flex-wrap {{
      flex-wrap: wrap;
    }}
    .items-center {{
      align-items: center;
    }}
    .justify-between {{
      justify-content: space-between;
    }}
    .justify-center {{
      justify-content: center;
    }}
    .gap-2 {{
      gap: 0.5rem;
    }}
    .gap-3 {{
      gap: 0.75rem;
    }}
    .gap-4 {{
      gap: 1rem;
    }}
    .gap-5 {{
      gap: 1.25rem;
    }}
    .gap-6 {{
      gap: 1.5rem;
    }}
    .space-y-3 > * + * {{
      margin-top: 0.75rem;
    }}
    .w-full {{
      width: 100%;
    }}
    .h-full {{
      height: 100%;
    }}
    .max-w-6xl {{
      max-width: 72rem;
    }}
    .max-w-md {{
      max-width: 28rem;
    }}
    .max-w-\[460px\] {{
      max-width: 460px;
    }}
    .max-w-\[220px\] {{
      max-width: 220px;
    }}
    @media (min-width: 640px) {{
      .sm\:max-w-xs {{
        max-width: 20rem;
      }}
      .sm\:p-6 {{
        padding: 1.5rem;
      }}
      .sm\:p-8 {{
        padding: 2rem;
      }}
      .sm\:text-sm {{
        font-size: 0.875rem;
        line-height: 1.25rem;
      }}
      .sm\:text-base {{
        font-size: 1rem;
        line-height: 1.5rem;
      }}
      .sm\:text-lg {{
        font-size: 1.125rem;
        line-height: 1.75rem;
      }}
      .sm\:text-xl {{
        font-size: 1.25rem;
        line-height: 1.75rem;
      }}
      .sm\:text-2xl {{
        font-size: 1.5rem;
        line-height: 2rem;
      }}
      .sm\:text-3xl {{
        font-size: 1.875rem;
        line-height: 2.25rem;
      }}
      .sm\:text-4xl {{
        font-size: 2.25rem;
        line-height: 2.5rem;
      }}
      .sm\:text-5xl {{
        font-size: 3rem;
        line-height: 1;
      }}
    }}
    .mx-auto {{
      margin-left: auto;
      margin-right: auto;
    }}
    .my-auto {{
      margin-top: auto;
      margin-bottom: auto;
    }}
    .my-2 {{
      margin-top: 0.5rem;
      margin-bottom: 0.5rem;
    }}
    .mb-5 {{
      margin-bottom: 1.25rem;
    }}
    .mt-1 {{
      margin-top: 0.25rem;
    }}
    .mt-2 {{
      margin-top: 0.5rem;
    }}
    .pb-3 {{
      padding-bottom: 0.75rem;
    }}
    .pt-2 {{
      padding-top: 0.5rem;
    }}
    .pt-3 {{
      padding-top: 0.75rem;
    }}
    .p-1 {{
      padding: 0.25rem;
    }}
    .p-4 {{
      padding: 1rem;
    }}
    .p-6 {{
      padding: 1.5rem;
    }}
    .px-2 {{
      padding-left: 0.5rem;
      padding-right: 0.5rem;
    }}
    .px-3\.5 {{
      padding-left: 0.875rem;
      padding-right: 0.875rem;
    }}
    .px-4 {{
      padding-left: 1rem;
      padding-right: 1rem;
    }}
    .px-5 {{
      padding-left: 1.25rem;
      padding-right: 1.25rem;
    }}
    .px-6 {{
      padding-left: 1.5rem;
      padding-right: 1.5rem;
    }}
    .py-1\.5 {{
      padding-top: 0.375rem;
      padding-bottom: 0.375rem;
    }}
    .py-2 {{
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }}
    .py-4 {{
      padding-top: 1rem;
      padding-bottom: 1rem;
    }}
    .min-h-\[520px\] {{
      min-height: 520px;
    }}
    .w-2\.5 {{
      width: 0.625rem;
    }}
    .h-2\.5 {{
      height: 0.625rem;
    }}
    .w-3\.5 {{
      width: 0.875rem;
    }}
    .h-3\.5 {{
      height: 0.875rem;
    }}
    .w-11 {{
      width: 2.75rem;
    }}
    .h-11 {{
      height: 2.75rem;
    }}
    .w-14 {{
      width: 3.5rem;
    }}
    .h-14 {{
      height: 3.5rem;
    }}
    .h-3 {{
      height: 0.75rem;
    }}
    .h-5 {{
      height: 1.25rem;
    }}
    .w-44 {{
      width: 11rem;
    }}
    .aspect-square {{
      aspect-ratio: 1 / 1;
    }}
    .relative {{
      position: relative;
    }}
    .block {{
      display: block;
    }}
    .truncate {{
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .overflow-hidden {{
      overflow: hidden;
    }}
    .text-center {{
      text-align: center;
    }}
    .text-xs {{
      font-size: 0.75rem;
      line-height: 1rem;
    }}
    .text-lg {{
      font-size: 1.125rem;
      line-height: 1.75rem;
    }}
    .text-xl {{
      font-size: 1.25rem;
      line-height: 1.75rem;
    }}
    .text-2xl {{
      font-size: 1.5rem;
      line-height: 2rem;
    }}
    .text-3xl {{
      font-size: 1.875rem;
      line-height: 2.25rem;
    }}
    .text-4xl {{
      font-size: 2.25rem;
      line-height: 2.5rem;
    }}
    .font-medium {{
      font-weight: 500;
    }}
    .font-semibold {{
      font-weight: 600;
    }}
    .font-bold {{
      font-weight: 700;
    }}
    .font-extrabold {{
      font-weight: 800;
    }}
    .italic {{
      font-style: italic;
    }}
    .uppercase {{
      text-transform: uppercase;
    }}
    .tracking-wider {{
      letter-spacing: 0.05em;
    }}
    .tracking-tight {{
      letter-spacing: -0.025em;
    }}
    .tracking-wide {{
      letter-spacing: 0.025em;
    }}
    .leading-relaxed {{
      line-height: 1.625;
    }}
    .rounded-2xl {{
      border-radius: 1rem;
    }}
    .rounded-3xl {{
      border-radius: 1.5rem;
    }}
    .rounded-full {{
      border-radius: 9999px;
    }}
    .border {{
      border: 1px solid #505876;
    }}
    .border-2 {{
      border-width: 2px;
      border-style: solid;
    }}
    .border-white {{
      border-color: #FFFFFF;
    }}
    .border-slate-700\/70 {{
      border-color: rgba(51, 65, 85, 0.7);
    }}
    .border-slate-700\/60 {{
      border-color: rgba(51, 65, 85, 0.6);
    }}
    .border-\[\#3E445C\] {{
      border-color: #3E445C;
    }}
    .border-\[\#3A4056\] {{
      border-color: #3A4056;
    }}
    .border-\[\#D4AF37\] {{
      border-color: #D4AF37;
    }}
    .border-\[\#6E7696\] {{
      border-color: #6E7696;
    }}
    .border-\[\#5F6682\] {{
      border-color: #5F6682;
    }}
    .border-\[\#505876\] {{
      border-color: #505876;
    }}
    .bg-slate-900\/80 {{
      background-color: rgba(15, 23, 42, 0.8);
    }}
    .bg-slate-900\/70 {{
      background-color: rgba(15, 23, 42, 0.7);
    }}
    .bg-amber-400 {{
      background-color: #FBBF24;
    }}
    .bg-\[\#1C1F2C\] {{
      background-color: #1C1F2C;
    }}
    .bg-\[\#1A1D28\] {{
      background-color: #1A1D28;
    }}
    .bg-\[\#242838\] {{
      background-color: #242838;
    }}
    .bg-\[\#30354A\] {{
      background-color: #30354A;
    }}
    .bg-\[\#303548\] {{
      background-color: #303548;
    }}
    .bg-\[\#2D3244\] {{
      background-color: #2D3244;
    }}
    .bg-\[\#4287F5\] {{
      background-color: #4287F5;
    }}
    .bg-\[\#D4AF37\] {{
      background-color: #D4AF37;
    }}
    .text-white {{
      color: #FFFFFF;
    }}
    .text-amber-400 {{
      color: #FBBF24;
    }}
    .text-emerald-300 {{
      color: #6EE7B7;
    }}
    .text-slate-100 {{
      color: #F1F5F9;
    }}
    .text-slate-200 {{
      color: #E2E8F0;
    }}
    .text-slate-300 {{
      color: #CBD5E1;
    }}
    .text-slate-400 {{
      color: #94A3B8;
    }}
    .text-slate-500 {{
      color: #64748B;
    }}
    .text-\[\#F8F5EE\] {{
      color: #F8F5EE;
    }}
    .text-\[\#D4AF37\] {{
      color: #D4AF37;
    }}
    .text-\[\#12141C\] {{
      color: #12141C;
    }}
    .shadow-md {{
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.35);
    }}
    .shadow-lg {{
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }}
    .shadow-2xl {{
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.55);
    }}
    .transition {{
      transition-property: color, background-color, border-color, transform, filter;
      transition-duration: 150ms;
      transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .transition-all {{
      transition-property: all;
      transition-duration: 75ms;
      transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .duration-75 {{
      transition-duration: 75ms;
    }}
    .active\:scale-95:active {{
      transform: scale(0.95);
    }}
    .hover\:text-amber-400:hover {{
      color: #FBBF24;
    }}
    .hover\:bg-\[\#3E4560\]:hover {{
      background-color: #3E4560;
    }}
    .hover\:bg-\[\#3A4056\]:hover {{
      background-color: #3A4056;
    }}
    .hover\:brightness-110:hover {{
      filter: brightness(1.1);
    }}
    button {{
      cursor: pointer;
      font-family: inherit;
      background-color: transparent;
      border: none;
      color: inherit;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(1, minmax(0, 1fr));
    }}
    @media (min-width: 1024px) {{
      .lg\:grid-cols-12 {{
        grid-template-columns: repeat(12, minmax(0, 1fr));
      }}
      .lg\:col-span-6 {{
        grid-column: span 6 / span 6;
      }}
    }}
    @keyframes pulseDot {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.4; }}
    }}
    .animate-pulse {{
      animation: pulseDot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}
    @keyframes bounceTitle {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-8px); }}
    }}
    .animate-bounce {{
      animation: bounceTitle 1s infinite;
    }}
    @keyframes stageShake {{
      0%, 100% {{ transform: translate(0, 0); }}
      20% {{ transform: translate(-6px, 4px); }}
      40% {{ transform: translate(6px, -4px); }}
      60% {{ transform: translate(-5px, -3px); }}
      80% {{ transform: translate(5px, 3px); }}
    }}
    .shaking {{
      animation: stageShake 0.14s infinite;
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between p-3 sm:p-6">

  <!-- Top Jukebox Bar -->
  <header class="max-w-6xl w-full mx-auto flex flex-wrap items-center justify-between gap-2 pb-3 text-xs sm:text-sm text-slate-400">
    <div class="flex items-center gap-2 font-bold tracking-wider uppercase text-amber-400">
      <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
      Appearance Matters: The Boots Room
    </div>
    <div class="flex items-center gap-3 bg-slate-900/80 border border-slate-700/70 px-3.5 py-1.5 rounded-full">
      <span id="jukeboxLabel" class="truncate max-w-[220px] sm:max-w-xs">♪ JUKEBOX: Touch anywhere to play</span>
      <button id="btnSkipTrack" type="button" class="px-2 py-0.5 rounded-full bg-[#2A3042] hover:bg-[#384058] text-slate-200 hover:text-amber-400 font-semibold transition">[N] Skip</button>
      <button id="btnMuteTrack" type="button" class="px-2 py-0.5 rounded-full bg-[#2A3042] hover:bg-[#384058] text-slate-200 hover:text-amber-400 font-semibold transition">[M] Mute</button>
    </div>
  </header>

  <!-- Main 2-Column Stage & Controls -->
  <main class="max-w-6xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch my-auto">

    <!-- Left Runway Stage -->
    <section id="stageCard" class="lg:col-span-6 bg-[#1C1F2C] border-2 border-[#3E445C] rounded-3xl p-4 sm:p-6 flex flex-col items-center justify-between shadow-2xl">
      <div class="w-full aspect-square max-w-[460px] relative flex items-center justify-center">
        <canvas id="blobCanvas" class="w-full h-full block rounded-2xl"></canvas>
      </div>
      <div id="stageCaption" class="mt-2 px-4 py-2 rounded-full bg-slate-900/70 border border-slate-700/60 text-xs sm:text-sm text-slate-300 text-center font-medium">
        Loading runway...
      </div>
    </section>

    <!-- Right Interactive Panel -->
    <section class="lg:col-span-6 bg-[#1A1D28] border-2 border-[#3A4056] rounded-3xl p-6 sm:p-8 flex flex-col justify-between shadow-2xl min-h-[520px]">

      <!-- VIEW 1: QUESTION STEPPER -->
      <div id="viewQuestion" class="flex flex-col justify-between h-full gap-6">
        <div>
          <div id="stepDots" class="flex items-center gap-2.5 mb-5"></div>
          <h1 id="qTitle" class="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#F8F5EE]"></h1>
          <p id="qSubtitle" class="text-slate-400 text-sm sm:text-base mt-2"></p>
        </div>

        <!-- Option Carousel Card -->
        <div class="bg-[#242838] border-2 border-[#D4AF37] rounded-2xl p-6 flex flex-col items-center justify-center gap-4 my-auto">
          <div id="swatchCircle" class="w-11 h-11 rounded-full border-2 border-white shadow-md"></div>
          <div class="w-full flex items-center justify-between gap-3">
            <button id="btnPrevOpt" type="button" aria-label="Previous Option"
              class="w-14 h-14 rounded-2xl bg-[#30354A] hover:bg-[#3E4560] border-2 border-[#6E7696] text-xl font-bold transition active:scale-95 flex items-center justify-center">
              ◄
            </button>
            <div id="optName" class="text-xl sm:text-2xl font-extrabold text-center text-white px-2"></div>
            <button id="btnNextOpt" type="button" aria-label="Next Option"
              class="w-14 h-14 rounded-2xl bg-[#30354A] hover:bg-[#3E4560] border-2 border-[#6E7696] text-xl font-bold transition active:scale-95 flex items-center justify-center">
              ►
            </button>
          </div>
          <div id="optCounter" class="text-xs sm:text-sm text-slate-400"></div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex items-center gap-3 pt-2">
          <button id="btnBackStep" type="button"
            class="hidden px-5 py-4 rounded-2xl bg-[#2D3244] hover:bg-[#3A4056] border-2 border-[#5F6682] font-bold text-slate-200 transition active:scale-95">
            ← BACK
          </button>
          <button id="btnConfirm" type="button"
            class="flex-1 py-4 px-6 rounded-2xl bg-[#4287F5] hover:brightness-110 font-extrabold text-base sm:text-lg tracking-wide transition active:scale-95 shadow-lg">
            NEXT QUESTION →
          </button>
        </div>
      </div>

      <!-- VIEW 2: DRUMROLL SUSPENSE -->
      <div id="viewDrumroll" class="hidden flex-col items-center justify-center text-center h-full gap-6 my-auto">
        <div class="text-3xl sm:text-4xl font-extrabold text-amber-400 animate-bounce">
          DRUMROLL PLEASE...
        </div>
        <p class="text-slate-300 text-base sm:text-lg">
          The Fashion Judge is calculating your fate...
        </p>
        <div class="w-full max-w-md h-5 bg-[#2D3244] rounded-full overflow-hidden p-1">
          <div id="drumrollBar" class="h-full bg-[#D4AF37] rounded-full transition-all duration-75" style="width: 0%"></div>
        </div>
      </div>

      <!-- VIEW 3: 4-40 TIER RESULTS -->
      <div id="viewResults" class="hidden flex-col justify-between h-full gap-4">
        <div>
          <div id="resCombo" class="text-xs sm:text-sm font-bold uppercase tracking-wider text-[#D4AF37]"></div>
          <div id="resScore" class="text-4xl sm:text-5xl font-extrabold text-white mt-1"></div>
          <div id="resTier" class="text-lg sm:text-xl font-bold text-emerald-300 mt-1"></div>
        </div>

        <!-- 4 Category Breakdown Bars -->
        <div id="resBreakdown" class="space-y-3 my-2"></div>

        <!-- Judge Dialogue Card -->
        <div class="bg-[#242838] border border-[#505876] rounded-2xl p-4 text-sm sm:text-base text-slate-100 leading-relaxed">
          <p id="resRoast" class="italic"></p>
        </div>

        <button id="btnPlayAgain" type="button"
          class="w-full py-4 rounded-2xl bg-[#D4AF37] hover:brightness-110 text-[#12141C] font-extrabold text-lg transition active:scale-95 shadow-lg">
          BUILD ANOTHER FIT ↻
        </button>
      </div>

    </section>
  </main>

  <footer class="max-w-6xl w-full mx-auto pt-3 text-center text-xs text-slate-500">
    Use ◄ / ► or A / D to browse • Enter / Space to confirm • Backspace to go back
  </footer>

  <script>
    const GAME_DATA = {payload_json};

    const SKIN_TONES = GAME_DATA.skin_tones;
    const BOOT_TYPES = GAME_DATA.boot_types;
    const BOOT_COLORS = GAME_DATA.boot_colors;
    const STICKY_MATERIALS = GAME_DATA.sticky_materials;
    const QUESTIONS = GAME_DATA.questions;
    const COMBOS = GAME_DATA.combos;
    const PLAYLIST = GAME_DATA.playlist;

    // --- AUDIO & SHUFFLED JUKEBOX ---
    const bgAudio = new Audio();
    bgAudio.volume = 0.25;
    bgAudio.preload = "auto";
    let trackQueue = [];
    let lastTrackUrl = null;
    let currentTrackTitle = "";
    let isMuted = false;
    let audioUnlocked = false;
    let unlockRetryTimer = null;

    const drumrollAudio = new Audio("assets/drumroll.wav");
    const cymbalAudio = new Audio("assets/cymbal.wav");

    function refillQueue() {{
      if (!PLAYLIST.length) return;
      trackQueue = [...PLAYLIST];
      for (let i = trackQueue.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [trackQueue[i], trackQueue[j]] = [trackQueue[j], trackQueue[i]];
      }}
      if (trackQueue.length > 1 && trackQueue[0].url === lastTrackUrl) {{
        trackQueue.push(trackQueue.shift());
      }}
    }}

    function updateJukeboxUI() {{
      const lbl = document.getElementById("jukeboxLabel");
      if (!PLAYLIST.length) {{
        lbl.textContent = "♪ JUKEBOX: No tracks in assets/music/";
        return;
      }}
      if (!audioUnlocked) {{
        lbl.textContent = "♪ JUKEBOX: Touch anywhere to play";
        return;
      }}
      const prefix = isMuted ? "MUTED" : "♪ JUKEBOX";
      lbl.textContent = `${{prefix}}: ${{currentTrackTitle || "Ready"}}`;
    }}

    function playNextTrack() {{
      if (!PLAYLIST.length) return;
      if (!trackQueue.length) refillQueue();
      const next = trackQueue.shift();
      lastTrackUrl = next.url;
      currentTrackTitle = next.title;
      bgAudio.src = next.url;
      bgAudio.muted = isMuted;
      if (state !== "DRUMROLL") {{
        bgAudio.volume = 0.25;
      }}
      const p = bgAudio.play();
      if (p && typeof p.catch === "function") {{
        p.catch(() => {{}});
      }}
      updateJukeboxUI();
    }}

    bgAudio.addEventListener("ended", playNextTrack);
    bgAudio.addEventListener("error", () => {{
      if (audioUnlocked && PLAYLIST.length > 1) {{
        setTimeout(playNextTrack, 250);
      }}
    }});

    function unlockAudio() {{
      if (!PLAYLIST.length) {{
        audioUnlocked = true;
        updateJukeboxUI();
        return;
      }}
      if (!audioUnlocked) {{
        audioUnlocked = true;
        playNextTrack();
        // Keep retrying briefly on first touch if the browser is still decoding/buffering
        if (!unlockRetryTimer) {{
          unlockRetryTimer = setInterval(() => {{
            if (!bgAudio.paused || isMuted) {{
              clearInterval(unlockRetryTimer);
              unlockRetryTimer = null;
              return;
            }}
            if (bgAudio.src) {{
              bgAudio.muted = isMuted;
              const retry = bgAudio.play();
              if (retry && typeof retry.catch === "function") retry.catch(() => {{}});
            }}
          }}, 400);
          setTimeout(() => {{
            if (unlockRetryTimer) {{
              clearInterval(unlockRetryTimer);
              unlockRetryTimer = null;
            }}
          }}, 4000);
        }}
      }} else if (bgAudio.paused && !isMuted && bgAudio.src) {{
        const resumeP = bgAudio.play();
        if (resumeP && typeof resumeP.catch === "function") resumeP.catch(() => {{}});
      }}
      updateJukeboxUI();
    }}

    // Unlock immediately on any touch, click, pointerdown, or keydown anywhere in the document
    ["pointerdown", "touchstart", "click", "keydown"].forEach((evtName) => {{
      document.addEventListener(evtName, unlockAudio, {{ passive: true }});
    }});

    // Web Audio API synthesized pop sound
    let audioCtx = null;
    function playPopSound() {{
      try {{
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === "suspended") audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(520, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.055);
        gain.gain.setValueAtTime(0.18, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.06);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.065);
      }} catch (e) {{}}
    }}

    // --- 4-40 JUDGE ENGINE (MIRRORS src/judge.py) ---
    function rollStylePoints(basePts, spread = 2, minVal = 1, maxVal = 10) {{
      const low = Math.max(minVal, basePts - spread);
      const high = Math.min(maxVal, basePts + spread);
      return Math.floor(Math.random() * (high - low + 1)) + low;
    }}

    function evaluateFit(skin, boot, color, sticky) {{
      const isBarefoot = boot.name === "None (Barefoot)";
      const choice = {{
        skin: skin.name,
        boot: boot.name,
        color: isBarefoot ? null : color.name,
        sticky: sticky.name,
      }};

      let bestMatch = null;
      let bestSpec = -1;
      let bestWeight = -1;

      for (const combo of COMBOS) {{
        const criteria = combo.criteria || {{}};
        const keys = Object.keys(criteria);
        if (!keys.length) continue;
        const matches = keys.every(k => choice[k] === criteria[k]);
        if (matches) {{
          const spec = keys.length;
          const weight = combo.max_score || combo.score || 20;
          if (spec > bestSpec || (spec === bestSpec && weight > bestWeight)) {{
            bestSpec = spec;
            bestWeight = weight;
            bestMatch = combo;
          }}
        }}
      }}

      let skinPts = rollStylePoints(skin.points);
      let bootPts = rollStylePoints(boot.points);
      let colorPts = isBarefoot ? 0 : rollStylePoints(color.points);
      let stickyPts = rollStylePoints(sticky.points);

      if (bestMatch && Array.isArray(bestMatch.score_range)) {{
        const [lowT, highT] = bestMatch.score_range;
        const targetTotal = Math.floor(Math.random() * (highT - lowT + 1)) + lowT;
        const active = isBarefoot ? [0, 1, 3] : [0, 1, 2, 3];
        const rolled = [skinPts, bootPts, colorPts, stickyPts];
        active.forEach(i => rolled[i] = Math.max(1, Math.min(10, rolled[i])));

        let guard = 0;
        while (active.reduce((s, i) => s + rolled[i], 0) !== targetTotal && guard < 250) {{
          guard++;
          const curSum = active.reduce((s, i) => s + rolled[i], 0);
          const idx = active[Math.floor(Math.random() * active.length)];
          if (curSum < targetTotal && rolled[idx] < 10) rolled[idx]++;
          else if (curSum > targetTotal && rolled[idx] > 1) rolled[idx]--;
        }}
        [skinPts, bootPts, colorPts, stickyPts] = rolled;
      }}

      const totalScore = Math.max(4, Math.min(40, skinPts + bootPts + colorPts + stickyPts));
      const footwearDesc = isBarefoot ? "bare blob feet" : `${{color.name.toLowerCase()}} ${{boot.name}} boots`;

      let tierTitle = "";
      let defaultRoast = "";

      if (totalScore >= 35) {{
        tierTitle = `GOD-TIER (${{totalScore}}/40): AVANT-GARDE ICON`;
        defaultRoast = `A staggering ${{totalScore}}/40! Pairing ${{skin.name.toLowerCase()}} skin with ${{footwearDesc}} and ${{sticky.name.toLowerCase()}} breaks every rule of fashion in the best way.`;
      }} else if (totalScore >= 27) {{
        tierTitle = `A-TIER (${{totalScore}}/40): HIGH-FASHION HAZARD`;
        defaultRoast = `Scored ${{totalScore}}/40! Bold, messy, and unforgettable—the ${{sticky.name.toLowerCase()}} transforms ${{footwearDesc}} into pure runway drama.`;
      }} else if (totalScore >= 18) {{
        tierTitle = `B-TIER (${{totalScore}}/40): CHAOTIC NEUTRAL`;
        defaultRoast = `A solid ${{totalScore}}/40. Mixing ${{skin.name.toLowerCase()}} skin, ${{footwearDesc}}, and ${{sticky.name.toLowerCase()}} shouldn't work, yet you're somehow pulling it off.`;
      }} else if (totalScore >= 10) {{
        tierTitle = `C-TIER (${{totalScore}}/40): PLAYGROUND ACCIDENT`;
        defaultRoast = `Only ${{totalScore}}/40. This looks less like high fashion and more like stepping in ${{sticky.name.toLowerCase()}} on the way to work.`;
      }} else {{
        tierTitle = `F-TIER (${{totalScore}}/40): AGGRESSIVELY MID`;
        defaultRoast = `Bottom of the chart at ${{totalScore}}/40. Even with ${{sticky.name.toLowerCase()}}, ${{footwearDesc}} on ${{skin.name.toLowerCase()}} skin is way too tame for the runway.`;
      }}

      let roastText = defaultRoast;
      if (bestMatch && bestMatch.roast) {{
        roastText = bestMatch.roast
          .replace(/\\{{score\\}}/g, totalScore)
          .replace(/\\{{skin\\}}/g, skin.name.toLowerCase())
          .replace(/\\{{footwear\\}}/g, footwearDesc)
          .replace(/\\{{sticky\\}}/g, sticky.name.toLowerCase());
      }}

      const comboName = bestMatch
        ? bestMatch.name
        : (isBarefoot ? `Barefoot with ${{sticky.name}}` : `${{color.name}} ${{boot.name}} with ${{sticky.name}}`);

      return {{
        breakdown: [
          ["Skin Tone Synergy", skinPts],
          ["Boot Silhouette", bootPts],
          ["Boot Color Pop", colorPts],
          ["The Stick Factor", stickyPts],
        ],
        totalScore,
        comboName,
        tierTitle,
        roastText,
      }};
    }}

    // --- PROCEDURAL SPRING-PHYSICS BLOB FOOT RENDERER (HTML5 CANVAS) ---
    const canvas = document.getElementById("blobCanvas");
    const ctx = canvas.getContext("2d");

    function resizeCanvas() {{
      const rect = canvas.parentElement.getBoundingClientRect();
      const size = Math.max(280, Math.floor(rect.width));
      canvas.width = size;
      canvas.height = size;
    }}
    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();

    const blob = {{
      legWidth: 112,
      legTopY: 115,
      footLength: 240,
      footHeight: 125,
      toeLift: 0,
      soleThickness: 0,
      puffiness: 0,
      scaleX: 1,
      scaleY: 1,
      velX: 0,
      velY: 0,
      bounce() {{
        this.scaleX = 1.16;
        this.scaleY = 0.86;
      }},
      update(dt, bootName) {{
        const targets = {{
          "None (Barefoot)": [112, 115, 240, 125, 0, 0, 0],
          "Sneaker":         [114, 255, 262, 122, 6, 20, 4],
          "Hiking":          [120, 145, 260, 138, 4, 18, 8],
          "Chelsea":         [104, 125, 250, 120, 8, 10, -4],
          "Steel-Toe Work":  [124, 130, 272, 146, 0, 24, 12],
          "Combat":          [122, 95,  265, 142, 5, 24, 8],
          "Cowboy":          [110, 82,  295, 118, 26, 16, -2],
          "Go-Go Platform":  [108, 75,  255, 122, 10, 46, 2],
          "Fuzzy Yeti":      [148, 95,  290, 165, 0, 20, 24],
        }};
        const t = targets[bootName] || targets["None (Barefoot)"];
        const k = Math.min(1, dt * 12);
        this.legWidth += (t[0] - this.legWidth) * k;
        this.legTopY += (t[1] - this.legTopY) * k;
        this.footLength += (t[2] - this.footLength) * k;
        this.footHeight += (t[3] - this.footHeight) * k;
        this.toeLift += (t[4] - this.toeLift) * k;
        this.soleThickness += (t[5] - this.soleThickness) * k;
        this.puffiness += (t[6] - this.puffiness) * k;

        const stiffness = 180;
        const damping = 14;
        const fx = (1 - this.scaleX) * stiffness;
        const fy = (1 - this.scaleY) * stiffness;
        this.velX = (this.velX + fx * dt) * Math.exp(-damping * dt);
        this.velY = (this.velY + fy * dt) * Math.exp(-damping * dt);
        this.scaleX += this.velX * dt;
        this.scaleY += this.velY * dt;
      }}
    }};

    function rgbStr(arr, alpha = 1) {{
      return `rgba(${{arr[0]}}, ${{arr[1]}}, ${{arr[2]}}, ${{alpha}})`;
    }}

    function traceBlobPath(c, cx, baseY, lw, topY, fl, fh, toeLift, puff) {{
      const leftX = cx - lw * 0.54;
      const rightLegX = cx + lw * 0.46;
      const ankleY = baseY - fh;
      const toeX = leftX + fl + puff * 0.4;

      const pTopLeft = [leftX, topY];
      const pTopRight = [rightLegX, topY];
      const pAnkleStart = [rightLegX, ankleY - 34];
      const pInstepMid = [rightLegX + (toeX - rightLegX) * 0.48, ankleY + 6 - toeLift * 0.25];
      const pToeTip = [toeX, baseY - fh * 0.36 - toeLift * 0.45];
      const pToeBottom = [toeX - 36, baseY - toeLift * 0.15];
      const pHeelBottom = [leftX + 44, baseY];
      const pHeelBack = [leftX - puff * 0.18, baseY - 48];
      const midSoleX = (pToeBottom[0] + pHeelBottom[0]) * 0.5;

      c.beginPath();
      c.moveTo(...pTopLeft);
      c.lineTo(...pTopRight);
      c.lineTo(...pAnkleStart);
      c.bezierCurveTo(rightLegX, ankleY + 4, rightLegX + 14, ankleY + 4, ...pInstepMid);
      c.bezierCurveTo(toeX - 16, ankleY + 8 - toeLift * 0.45, toeX + 4, baseY - fh * 0.72 - toeLift * 0.5, ...pToeTip);
      c.bezierCurveTo(toeX + 2, baseY - 6 - toeLift * 0.35, toeX - 14, baseY + 2 - toeLift * 0.2, ...pToeBottom);
      c.bezierCurveTo(midSoleX + 25, baseY + 10, midSoleX - 25, baseY + 10, ...pHeelBottom);
      c.bezierCurveTo(leftX + 8, baseY + 2, leftX - 6 - puff * 0.2, baseY - 16, ...pHeelBack);
      c.bezierCurveTo(leftX - puff * 0.1, ankleY, leftX, topY + 40, ...pTopLeft);
      c.closePath();
    }}

    function renderScene(timeSec, skin, boot, color, sticky) {{
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      ctx.save();
      const s = w / 520;
      ctx.scale(s, s);

      const cx = 215;
      const baseY = 426 - blob.soleThickness * 0.35;
      const outline = "#2A221C";

      // Runway Spotlight Pedestal
      ctx.fillStyle = "#2A2F42";
      ctx.strokeStyle = "#D4AF37";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.ellipse(260, 462, 195, 34, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Contact Shadow
      ctx.fillStyle = "rgba(18, 20, 28, 0.55)";
      ctx.beginPath();
      ctx.ellipse(cx + blob.footLength * 0.26, 456, blob.footLength * 0.52, 12, 0, 0, Math.PI * 2);
      ctx.fill();

      // Apply Squish & Stretch around floor anchor
      ctx.save();
      ctx.translate(cx + 45, 445);
      ctx.scale(blob.scaleX, blob.scaleY);
      ctx.translate(-(cx + 45), -445);

      ctx.lineJoin = "round";
      ctx.lineCap = "round";

      // 1. Bare Skin Blob Leg & Foot
      traceBlobPath(ctx, cx, baseY, blob.legWidth, 72, blob.footLength, blob.footHeight, blob.toeLift, blob.puffiness);
      ctx.fillStyle = rgbStr(skin.rgb);
      ctx.fill();
      ctx.lineWidth = 7;
      ctx.strokeStyle = outline;
      ctx.stroke();

      const bootName = boot.name;
      const bootCol = color.rgb;

      // 2. Boot Layer
      if (bootName !== "None (Barefoot)") {{
        const bootLw = blob.legWidth + 14;
        const bootFl = blob.footLength + 12;
        const bootFh = blob.footHeight + 8;
        const cuffY = blob.legTopY + 48;
        const leftX = cx - bootLw * 0.54;
        const rightX = cx + bootLw * 0.46;
        const toeX = leftX + bootFl + (blob.puffiness + 3) * 0.4;

        // Outsole & Heel
        if (blob.soleThickness > 2) {{
          const st = Math.max(10, blob.soleThickness * 0.55);
          const heelH = st + (["Cowboy", "Combat", "Hiking", "Steel-Toe Work"].includes(bootName) ? 10 : 2);
          ctx.beginPath();
          ctx.moveTo(leftX + 6, baseY - 6);
          ctx.bezierCurveTo(leftX + bootFl * 0.35, baseY + 4, leftX + bootFl * 0.65, baseY + 4, toeX - 8, baseY - 6 - blob.toeLift * 0.22);
          ctx.lineTo(toeX - 10, baseY + st - blob.toeLift * 0.22);
          ctx.lineTo(leftX + bootFl * 0.44, baseY + st + 3);
          ctx.lineTo(leftX + bootFl * 0.34, baseY + heelH);
          ctx.lineTo(leftX + 12, baseY + heelH);
          ctx.closePath();
          ctx.fillStyle = bootName === "Cowboy" ? "#442C1E" : (bootName === "Sneaker" ? "#F2F4F8" : "#24242A");
          ctx.fill();
          ctx.lineWidth = 7;
          ctx.strokeStyle = outline;
          ctx.stroke();
        }}

        // Main Boot Upper
        traceBlobPath(ctx, cx, baseY, bootLw, cuffY, bootFl, bootFh, blob.toeLift, blob.puffiness + 3);
        ctx.fillStyle = rgbStr(bootCol);
        ctx.fill();
        ctx.lineWidth = 7;
        ctx.strokeStyle = outline;
        ctx.stroke();

        // Silhouette Details
        if (bootName === "Sneaker") {{
          // Two-tone white front half
          ctx.save();
          traceBlobPath(ctx, cx, baseY, bootLw, cuffY, bootFl, bootFh, blob.toeLift, blob.puffiness + 3);
          ctx.clip();
          const midX = leftX + bootFl * 0.5;
          ctx.fillStyle = "#F5F6FA";
          ctx.fillRect(midX, 0, 520 - midX, 520);
          ctx.beginPath();
          ctx.moveTo(midX - 6, baseY - bootFh + 6);
          ctx.bezierCurveTo(midX + 14, baseY - bootFh * 0.55, midX + 12, baseY - bootFh * 0.25, midX - 2, baseY - 3);
          ctx.lineWidth = 6;
          ctx.strokeStyle = outline;
          ctx.stroke();
          ctx.restore();

          // Redraw outer ink
          traceBlobPath(ctx, cx, baseY, bootLw, cuffY, bootFl, bootFh, blob.toeLift, blob.puffiness + 3);
          ctx.lineWidth = 7;
          ctx.strokeStyle = outline;
          ctx.stroke();

          // White Tongue & Laces
          ctx.fillStyle = "#F5F6FA";
          ctx.beginPath();
          ctx.roundRect(rightX - 14, cuffY - 20, 30, 36, 10);
          ctx.fill();
          ctx.lineWidth = 5;
          ctx.stroke();

          for (let i = 0; i < 4; i++) {{
            const lx = rightX + 8 + i * 20;
            const ly = cuffY + 14 + i * 11;
            ctx.lineWidth = 10;
            ctx.strokeStyle = outline;
            ctx.beginPath();
            ctx.moveTo(lx - 4, ly + 4);
            ctx.lineTo(lx + 18, ly - 10);
            ctx.stroke();
            ctx.lineWidth = 5;
            ctx.strokeStyle = "#F8F9FC";
            ctx.stroke();
          }}
        }} else if (bootName === "Cowboy") {{
          ctx.strokeStyle = outline;
          ctx.lineWidth = 6;
          ctx.beginPath();
          ctx.moveTo(leftX + 6, cuffY + 4);
          ctx.lineTo((leftX + rightX) * 0.5, cuffY + 24);
          ctx.lineTo(rightX - 6, cuffY + 4);
          ctx.stroke();
        }} else if (["Combat", "Hiking", "Steel-Toe Work"].includes(bootName)) {{
          ctx.fillStyle = "#303038";
          ctx.strokeStyle = outline;
          ctx.lineWidth = 5;
          ctx.beginPath();
          ctx.roundRect(leftX - 4, cuffY - 6, bootLw + 8, 24, 10);
          ctx.fill();
          ctx.stroke();

          const count = bootName === "Combat" ? 5 : 3;
          for (let i = 0; i < count; i++) {{
            const ly = cuffY + 32 + i * 22;
            if (ly < baseY - 38) {{
              ctx.beginPath();
              ctx.moveTo(rightX - 24, ly);
              ctx.lineTo(rightX + 6, ly - 5);
              ctx.stroke();
            }}
          }}
          if (bootName === "Steel-Toe Work") {{
            ctx.fillStyle = "#A8B2C0";
            ctx.beginPath();
            ctx.arc(toeX - 42, baseY - 30, 36, -0.4, Math.PI, true);
            ctx.closePath();
            ctx.fill();
            ctx.lineWidth = 6;
            ctx.stroke();
          }}
        }} else if (bootName === "Chelsea") {{
          ctx.fillStyle = "#202026";
          ctx.strokeStyle = outline;
          ctx.lineWidth = 5;
          ctx.beginPath();
          ctx.roundRect(cx - 22, cuffY + 18, 38, 76, 16);
          ctx.fill();
          ctx.stroke();
        }} else if (bootName === "Go-Go Platform") {{
          ctx.fillStyle = "#F5F5FA";
          ctx.strokeStyle = outline;
          ctx.lineWidth = 4;
          ctx.beginPath();
          ctx.roundRect(leftX - 2, cuffY + 14, bootLw + 4, 18, 6);
          ctx.fill();
          ctx.stroke();
          ctx.fillStyle = "#EBC341";
          ctx.beginPath();
          ctx.roundRect(cx - 10, cuffY + 11, 24, 24, 5);
          ctx.fill();
          ctx.stroke();
        }} else if (bootName === "Fuzzy Yeti") {{
          const puffs = [
            [leftX + 8, cuffY + 6, 22],
            [leftX + 42, cuffY + 2, 24],
            [cx + 12, cuffY + 4, 23],
            [rightX - 6, cuffY + 8, 21],
          ];
          ctx.fillStyle = rgbStr(bootCol);
          ctx.strokeStyle = outline;
          ctx.lineWidth = 5;
          for (const [px, py, pr] of puffs) {{
            ctx.beginPath();
            ctx.arc(px, py, pr, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
          }}
        }}
      }}

      // 3. Sticky Material Layer
      if (sticky.name !== "None (Clean)") {{
        const wobble = Math.sin(timeSec * 4.2) * 3.5;
        const leftX = cx - blob.legWidth * 0.54;
        const toeX = leftX + blob.footLength;
        const midX = leftX + blob.footLength * 0.56;

        ctx.fillStyle = rgbStr(sticky.rgb, 0.92);
        ctx.strokeStyle = outline;
        ctx.lineWidth = 5;

        if (sticky.name === "Wet Cement") {{
          ctx.beginPath();
          ctx.moveTo(leftX - 12, baseY - 84);
          ctx.lineTo(midX + 45, baseY - 78);
          ctx.lineTo(toeX + 22, baseY - 64);
          ctx.lineTo(toeX + 26, baseY + 18);
          ctx.lineTo(leftX - 16, baseY + 18);
          ctx.closePath();
          ctx.fill();
          ctx.stroke();
        }} else if (sticky.name === "Bubblegum") {{
          ctx.beginPath();
          ctx.ellipse(midX + 14, baseY - 46, 44, 32, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();
          ctx.beginPath();
          ctx.moveTo(midX + 6, baseY - 18);
          ctx.lineTo(midX + 24, baseY - 18);
          ctx.lineTo(midX + 18 + wobble, baseY + 26);
          ctx.lineTo(midX + 10 + wobble, baseY + 26);
          ctx.closePath();
          ctx.fill();
          ctx.stroke();
        }} else {{
          const capX = cx - 10;
          const capY = baseY - blob.footHeight - 12;
          const d1 = 58 + wobble * 1.4;
          const d2 = 42 - wobble * 1.2;
          ctx.beginPath();
          ctx.roundRect(capX - 22, capY + 8, 128, 36, 18);
          ctx.roundRect(capX + 2, capY + 24, 22, d1, 11);
          ctx.roundRect(capX + 48, capY + 24, 22, d2, 11);
          ctx.ellipse(midX + 18, baseY - 38, 52, 34, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();
        }}
      }}

      ctx.restore();
      ctx.restore();
    }}

    // --- UI & GAME STATE CONTROLLER ---
    let state = "QUESTION";
    let currentStep = 0;
    const selections = [0, 1, 0, 0];

    const viewQuestion = document.getElementById("viewQuestion");
    const viewDrumroll = document.getElementById("viewDrumroll");
    const viewResults = document.getElementById("viewResults");
    const stageCard = document.getElementById("stageCard");

    function getActiveItems() {{
      return {{
        skin: SKIN_TONES[selections[0]],
        boot: BOOT_TYPES[selections[1]],
        color: BOOT_COLORS[selections[2]],
        sticky: STICKY_MATERIALS[selections[3]],
      }};
    }}

    function syncUI() {{
      const {{ skin, boot, color, sticky }} = getActiveItems();
      const isBarefoot = boot.name === "None (Barefoot)";
      const bootLabel = isBarefoot ? "Barefoot" : `${{color.name}} ${{boot.name}}`;
      document.getElementById("stageCaption").textContent = `${{skin.name}}  •  ${{bootLabel}}  •  ${{sticky.name}}`;

      viewQuestion.classList.toggle("hidden", state !== "QUESTION");
      viewQuestion.classList.toggle("flex", state === "QUESTION");
      viewDrumroll.classList.toggle("hidden", state !== "DRUMROLL");
      viewDrumroll.classList.toggle("flex", state === "DRUMROLL");
      viewResults.classList.toggle("hidden", state !== "RESULTS");
      viewResults.classList.toggle("flex", state === "RESULTS");
      stageCard.classList.toggle("shaking", state === "DRUMROLL");

      if (state === "QUESTION") {{
        const q = QUESTIONS[currentStep];
        const opts = q.options;
        const selected = opts[selections[currentStep]];
        const visibleSteps = isBarefoot ? [0, 1, 3] : [0, 1, 2, 3];
        const displayNum = visibleSteps.indexOf(currentStep) + 1;
        const totalNum = visibleSteps.length;

        const dotsEl = document.getElementById("stepDots");
        dotsEl.innerHTML = visibleSteps.map(stepId =>
          `<span class="w-3.5 h-3.5 rounded-full ${{stepId <= currentStep ? "bg-[#D4AF37]" : "bg-[#3C4155]"}}"></span>`
        ).join("");

        let title = q.title;
        if (isBarefoot && currentStep === 3) title = "STEP 3 OF 3: CHOOSE STICKY MATERIAL";
        else if (isBarefoot) title = title.replace("OF 4:", "OF 3:");

        document.getElementById("qTitle").textContent = title;
        document.getElementById("qSubtitle").textContent = q.subtitle;
        document.getElementById("optName").textContent = selected.name;
        document.getElementById("optCounter").textContent = `Option ${{selections[currentStep] + 1}} of ${{opts.length}}`;

        const swatch = document.getElementById("swatchCircle");
        if (selected.rgb && selected.name !== "None (Clean)") {{
          swatch.classList.remove("hidden");
          swatch.style.backgroundColor = rgbStr(selected.rgb);
        }} else {{
          swatch.classList.add("hidden");
        }}

        const backBtn = document.getElementById("btnBackStep");
        backBtn.classList.toggle("hidden", currentStep === 0);

        const isFinal = displayNum === totalNum;
        const confirmBtn = document.getElementById("btnConfirm");
        confirmBtn.textContent = isFinal ? "JUDGE MY FIT! ★" : "NEXT QUESTION →";
        confirmBtn.className = isFinal
          ? "flex-1 py-4 px-6 rounded-2xl bg-[#D4AF37] text-[#12141C] hover:brightness-110 font-extrabold text-base sm:text-lg tracking-wide transition active:scale-95 shadow-lg"
          : "flex-1 py-4 px-6 rounded-2xl bg-[#4287F5] text-white hover:brightness-110 font-extrabold text-base sm:text-lg tracking-wide transition active:scale-95 shadow-lg";
      }}
    }}

    function cycleOption(delta) {{
      unlockAudio();
      const opts = QUESTIONS[currentStep].options;
      selections[currentStep] = (selections[currentStep] + delta + opts.length) % opts.length;
      blob.bounce();
      playPopSound();
      syncUI();
    }}

    function advanceStep() {{
      unlockAudio();
      const isBarefoot = BOOT_TYPES[selections[1]].name === "None (Barefoot)";
      if (currentStep === 1 && isBarefoot) {{
        currentStep = 3;
        blob.bounce();
        playPopSound();
        syncUI();
      }} else if (currentStep < 3) {{
        currentStep++;
        blob.bounce();
        playPopSound();
        syncUI();
      }} else {{
        startDrumroll();
      }}
    }}

    function goBackStep() {{
      unlockAudio();
      const isBarefoot = BOOT_TYPES[selections[1]].name === "None (Barefoot)";
      if (currentStep === 3 && isBarefoot) {{
        currentStep = 1;
      }} else if (currentStep > 0) {{
        currentStep--;
      }}
      blob.bounce();
      playPopSound();
      syncUI();
    }}

    function startDrumroll() {{
      state = "DRUMROLL";
      syncUI();
      bgAudio.volume = 0.06;
      drumrollAudio.currentTime = 0;
      drumrollAudio.play().catch(() => {{}});

      const duration = 2400;
      const start = performance.now();
      const bar = document.getElementById("drumrollBar");

      function tickDrumroll(now) {{
        const pct = Math.min(100, ((now - start) / duration) * 100);
        bar.style.width = `${{pct}}%`;
        if (now - start < duration) {{
          requestAnimationFrame(tickDrumroll);
        }} else {{
          showResults();
        }}
      }}
      requestAnimationFrame(tickDrumroll);
    }}

    function showResults() {{
      const {{ skin, boot, color, sticky }} = getActiveItems();
      const verdict = evaluateFit(skin, boot, color, sticky);
      state = "RESULTS";
      blob.bounce();
      bgAudio.volume = 0.25;
      cymbalAudio.currentTime = 0;
      cymbalAudio.play().catch(() => {{}});

      document.getElementById("resCombo").textContent = `COMBO: ${{verdict.comboName}}`;
      document.getElementById("resScore").textContent = `${{verdict.totalScore}} / 40`;
      document.getElementById("resTier").textContent = verdict.tierTitle;
      document.getElementById("resRoast").textContent = `"${{verdict.roastText}}"`;

      const bdEl = document.getElementById("resBreakdown");
      bdEl.innerHTML = verdict.breakdown.map(([label, pts]) => `
        <div class="flex items-center justify-between gap-4 text-sm">
          <span class="text-slate-300 font-medium">${{label}}: <strong class="text-white">${{pts}}/10</strong></span>
          <div class="w-44 h-3 bg-[#303548] rounded-full overflow-hidden">
            <div class="h-full bg-[#D4AF37] rounded-full" style="width: ${{pts * 10}}%"></div>
          </div>
        </div>
      `).join("");

      syncUI();
    }}

    // Button & Keyboard Listeners
    document.getElementById("btnPrevOpt").addEventListener("click", () => cycleOption(-1));
    document.getElementById("btnNextOpt").addEventListener("click", () => cycleOption(1));
    document.getElementById("btnBackStep").addEventListener("click", goBackStep);
    document.getElementById("btnConfirm").addEventListener("click", advanceStep);
    document.getElementById("btnPlayAgain").addEventListener("click", () => {{
      unlockAudio();
      state = "QUESTION";
      currentStep = 0;
      blob.bounce();
      playPopSound();
      syncUI();
    }});

    document.getElementById("btnSkipTrack").addEventListener("click", () => {{
      unlockAudio();
      playNextTrack();
    }});
    document.getElementById("btnMuteTrack").addEventListener("click", () => {{
      unlockAudio();
      isMuted = !isMuted;
      bgAudio.muted = isMuted;
      updateJukeboxUI();
    }});

    window.addEventListener("keydown", (e) => {{
      unlockAudio();
      if (e.key === "m" || e.key === "M") {{
        isMuted = !isMuted;
        bgAudio.muted = isMuted;
        updateJukeboxUI();
      }} else if (e.key === "n" || e.key === "N") {{
        playNextTrack();
      }} else if (state === "QUESTION") {{
        if (e.key === "ArrowLeft" || e.key === "a" || e.key === "A") cycleOption(-1);
        else if (e.key === "ArrowRight" || e.key === "d" || e.key === "D") cycleOption(1);
        else if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); advanceStep(); }}
        else if (e.key === "Backspace" && currentStep > 0) goBackStep();
      }} else if (state === "RESULTS") {{
        if (e.key === "Enter" || e.key === " " || e.key === "r" || e.key === "R") {{
          state = "QUESTION";
          currentStep = 0;
          blob.bounce();
          syncUI();
        }}
      }}
    }});

    // Animation Loop
    let lastFrame = performance.now();
    function loop(now) {{
      const dt = Math.min(0.05, (now - lastFrame) / 1000);
      lastFrame = now;
      const {{ skin, boot, color, sticky }} = getActiveItems();
      blob.update(dt, boot.name);
      renderScene(now / 1000, skin, boot, color, sticky);
      requestAnimationFrame(loop);
    }}

    updateJukeboxUI();
    syncUI();
    requestAnimationFrame(loop);
  </script>
</body>
</html>
"""


def main():
    print("=====================================================")
    print("  BUILDING HTML5 WEB VERSION -> dist/web/")
    print("=====================================================")

    combos = load_combos_data()
    playlist = prepare_audio_and_assets()

    payload = {
        "skin_tones": SKIN_TONES,
        "boot_types": BOOT_TYPES,
        "boot_colors": BOOT_COLORS,
        "sticky_materials": STICKY_MATERIALS,
        "questions": QUESTIONS,
        "combos": combos,
        "playlist": playlist,
    }

    os.makedirs(DIST_WEB_DIR, exist_ok=True)
    out_html_path = os.path.join(DIST_WEB_DIR, "index.html")
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(generate_html(payload))

    print(f"[Build Complete] Output written to: {out_html_path}")
    print(f"[Build Complete] Jukebox tracks bundled: {len(playlist)}")
    print("\nTo test locally, run:")
    print("  python -m http.server 8000 --directory dist/web")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"[Build Failed] {err}")
        sys.exit(1)