# Appearance Matters: The Boots Room

A procedural 2D fashion-critique game built with **Python** and **Pygame**. Step into *The Boots Room*, customise a spring-physics blob foot across four chaotic styling categories, watch it contort in real time to fit your footwear, and survive a dramatic drumroll verdict on a **4–40 tier-list scale**.

---

## Features

* **Live Contorting Blob Foot Renderer:** Smooth Bezier-curve vector-style rendering with spring squish-and-stretch physics that dynamically morphs your foot to match every silhouette—including two-tone sneakers, steel-toe work boots, cowboy boots, go-go platforms, and fuzzy yeti boots.
* **Style-Weighted 4–40 Judge Engine:** randomises category points (`1–10` each) weighted around your chosen style's aesthetic range, keeping the 4-category bars, total score (`4–40`), tier rank (`F-Tier` through `God-Tier`), and custom judge dialogue 100% synchronised.
* **Built-In Shuffle Jukebox:** Automatically displays the currently playing on screen, and lowers music volume during the drumroll reveal.

---

## Controls

| Key / Input | Action |
| :--- | :--- |
| **`◄` / `►`** or **`A` / `D`** (or click arrows) | Cycle through options in the current category |
| **`Enter`** or **`Space`** (or click button) | Confirm choice / Advance to next question / Play again |
| **`Backspace`** (or click `← BACK`) | Return to the previous question |
| **`N`** | Skip to the next shuffled song in the Jukebox |
| **`M`** | Mute / Unmute background Jukebox music |
| **`F11`** | Toggle Fullscreen / Windowed mode |
| **`Esc`** | Quit the game |

---

## Getting Started

### 1. Prerequisites & Installation
Make sure you have **Python 3.9+** installed, then install `pygame`:

```bash
pip install -r requirements.txt
```

### 2. Run the Game
From the project root directory, run:

```bash
python src/main.py
```

---

## customising Music, SFX & App Icon

### Background Jukebox (`assets/music/`)
1. Drop any `.mp3`, `.wav`, `.ogg`, `.flac`, or `.m4a` tracks into `assets/music/`.
2. Name each file **`Artist - Song Name.mp3`**—the Jukebox automatically strips the extension and displays that title in the top-right corner.
3. Every song in the folder plays once in random order before the playlist reshuffles and loops.
4. To adjust the default music volume, edit `Jukebox(volume=0.25)` in `src/main.py` (`0.0` = silent, `1.0` = max).

### Custom Sound Effects (`assets/`)
* **`assets/drumroll.wav`** — Plays during the screen-shake suspense buildup before the verdict.
* **`assets/cymbal.wav`** — Plays right as the final scorecard appears.
* Option cycling pops are synthesised procedurally in code, so no extra audio files are required.

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
* **35–40:** `GOD-TIER` — Avant-Garde Icon
* **27–34:** `A-TIER` — High-Fashion Hazard
* **18–26:** `B-TIER` — Chaotic Neutral
* **10–17:** `C-TIER` — Playground Accident
* **4–9:** `F-TIER` — Aggressively Mid

You can add or tweak secret named combinations, score ranges, and custom `{score}` dialogue templates anytime in `src/combos.json`.

---

## Building a Standalone Windows Executable (`.exe`)

To package the game into a single standalone `.exe` with your custom `icon.ico` embedded as the app icon:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Appearance Matters - The Boots Room" --icon="assets/icon.ico" --add-data "assets;assets" --add-data "src/combos.json;." src/main.py
```

The compiled executable will appear in the `dist/` folder.

## Credits

Favicon created by [Magnific - Flaticon](https://www.flaticon.com/free-icons/snow-boot)