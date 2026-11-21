# Appearance Matters: The Boots Room

A procedural 2D fashion-critique game built with **Python** and **Pygame** (with a one-command **HTML5 / Canvas** web build generator). Step into *The Boots Room*, customise a spring-physics blob foot across four chaotic styling categories, watch it contort in real time to fit your footwear, and survive a dramatic drumroll verdict on a **4–40 tier-list scale**.

---

## Features

- **Live Contorting Blob Foot Renderer:** Smooth Bezier-curve vector-style rendering with spring squish-and-stretch physics that dynamically morphs your foot to match every silhouette—including two-tone sneakers, steel-toe work boots, cowboy boots, go-go platforms, and fuzzy yeti boots.
- **Style-Weighted 4–40 Judge Engine:** Randomises category points (`1–10` each) weighted around your chosen style's aesthetic range, keeping the 4-category bars, total score (`4–40`), tier rank (`F-Tier` through `God-Tier`), and custom judge dialogue 100% synchronised.
- **Built-In Shuffle Jukebox:** Automatically shuffles tracks from `assets/music/`, displays the currently playing song on screen, and lowers music volume during the drumroll reveal.
- **One-Command HTML5 Web Build (`build_web.py`):** Compiles your exact Python config, combos, and audio (auto-converting `.mp3` songs to `.ogg` via `pydub`) into a standalone browser game in `dist/web/`.

---

## Controls

| Key / Input | Action |
| :--- | :--- |
| **`◄` / `►`** or **`A` / `D`** (or click arrows) | Cycle through options in the current category |
| **`Enter`** or **`Space`** (or click button) | Confirm choice / Advance to next question / Play again |
| **`Backspace`** (or click `← BACK`) | Return to the previous question |
| **`N`** | Skip to the next shuffled song in the Jukebox |
| **`M`** | Mute / Unmute background Jukebox music |
| **`F11`** | Toggle Fullscreen / Windowed mode *(Desktop)* |
| **`Esc`** | Quit the game *(Desktop)* |

---

## Project Structure

```text
├── assets/
│   ├── music/          # Drop .mp3, .wav, .ogg, .flac, or .m4a tracks here
│   ├── drumroll.wav    # Suspense drumroll SFX
│   ├── cymbal.wav      # Final verdict cymbal SFX
│   └── icon.ico        # Custom window & taskbar icon
├── src/
│   ├── main.py         # Main Pygame entry point & UI loop
│   ├── config.py       # Skin tones, boot styles, colors, sticky materials & questions
│   ├── renderer.py     # Procedural Bezier & spring-physics blob foot renderer
│   ├── judge.py        # Style-weighted 4–40 tier-list judge engine
│   ├── audio.py        # Shuffled Jukebox & SFX loader
│   └── combos.json     # Named style combos, target score ranges & dialogue templates
├── build_web.py        # HTML5 + Pydub web build generator (-> dist/web/)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Getting Started (Desktop)

### 1. Prerequisites & Installation
Make sure you have **Python 3.9+** installed, then install the dependencies:

```bash
pip install -r requirements.txt
```

### 2. Run the Game
From the project root directory, run:

```bash
python src/main.py
```

---

## Customising Music, SFX & App Icon

### Background Jukebox (`assets/music/`)
1. Drop any `.mp3`, `.wav`, `.ogg`, `.flac`, or `.m4a` tracks into `assets/music/`.
2. Name each file **`Artist - Song Name.mp3`**—the Jukebox automatically strips the extension and displays that title in the top-right corner.
3. Every song in the folder plays once in random order before the playlist reshuffles and loops.
4. To adjust the default music volume, edit `Jukebox(volume=0.25)` in `src/main.py` (`0.0` = silent, `1.0` = max).

### Custom Sound Effects (`assets/`)
- **`assets/drumroll.wav`** — Plays during the screen-shake suspense buildup before the verdict.
- **`assets/cymbal.wav`** — Plays right as the final scorecard appears.
- Option cycling pops are synthesised procedurally in code, so no extra audio files are required.

### Window & Taskbar Icon (`icon.ico`)
Place your `icon.ico` file inside `assets/icon.ico` (or the project root). On Windows, `src/main.py` registers a unique AppUserModelID so your custom icon appears on the taskbar instead of the default Python launcher icon.

---

## How Judging & Scoring Work

Each run evaluates four categories on a **1–10 scale**, summing to a **4–40 total score**:

1. **Skin Tone Synergy** *(1–10)*
2. **Boot Silhouette** *(1–10)*
3. **Boot Color Pop** *(1–10, or `0/10` when Barefoot)*
4. **The Stick Factor** *(1–10)*

### Tier Brackets
- **35–40:** `GOD-TIER` — Avant-Garde Icon
- **27–34:** `A-TIER` — High-Fashion Hazard
- **18–26:** `B-TIER` — Chaotic Neutral
- **10–17:** `C-TIER` — Playground Accident
- **4–9:** `F-TIER` — Aggressively Mid

You can add or tweak secret named combinations, score ranges, and custom `{score}` dialogue templates anytime in `src/combos.json`.

---

## Building a Standalone Windows Executable (`.exe`)

To package the desktop game into a single standalone `.exe` with your custom `icon.ico` embedded as the app icon:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Appearance Matters - The Boots Room" --icon="assets/icon.ico" --add-data "assets;assets" --add-data "src/combos.json;." src/main.py
```

The compiled executable will appear in the `dist/` folder.

---

## Building a Browser Version (`dist/web`)

This repository includes **`build_web.py`**, which reads your existing `src/config.py`, `src/combos.json`, and `assets/` folder, uses **`pydub`** to batch-convert your `.mp3` songs into `.ogg` files, and outputs a complete HTML5/Canvas browser build into **`dist/web/`**.

### 1. Install `pydub`
```bash
pip install pydub
```
*(Note: `pydub` uses `ffmpeg` to decode `.mp3` files into `.ogg`. If `ffmpeg` is not installed, `build_web.py` still copies your `.mp3` tracks directly so the browser's `<audio>` player can play them natively.)*

### 2. Build to `dist/web`
From the project root directory, run:

```bash
python build_web.py
```

This generates:
- **`dist/web/index.html`** — Complete HTML5 Canvas & Tailwind CSS game with spring-physics blob foot animations, all 9 boot silhouettes, all 8 sticky materials, and the 4–40 combo judge.
- **`dist/web/assets/`** — Your converted `.ogg` jukebox tracks, `drumroll.wav`, `cymbal.wav`, and `icon.ico`.

### 3. Preview & Host Online
Test locally in your browser:

```bash
python -m http.server 8000 --directory dist/web
```

Open **`http://localhost:8000`**, click anywhere on the page to start the Jukebox audio, and play. To publish on **itch.io**, **GitHub Pages**, or **Netlify**, simply zip or upload the contents of **`dist/web/`**.

---

## Credits

Favicon created by [Magnific - Flaticon](https://www.flaticon.com/free-icons/snow-boot)