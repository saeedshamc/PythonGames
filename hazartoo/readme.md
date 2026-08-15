<p align="center">
  <img src="img/banner.png" alt="Hazartoo" width="720">
</p>

<p align="center">
  <b>هزارتو</b> — Persian for <i>"labyrinth"</i>
</p>

> **Khwarazmi University (Karaj Campus)** · **Advanced Programming (AP) Project**
> **Instructor:** Eng. Zahra Alizadeh
> **Authors:** Rouhollah Hosseini, Shayan Rezapour

---

## 📝 About

**Hazartoo** is a 2D procedural maze game built with Python and Pygame. Every level is generated on the fly with a randomized depth‑first‑search algorithm, and the maze gets larger and trickier as you climb through 10 levels.

This version is a full rewrite of the original class project, focused on making the movement feel great and the game itself rock‑solid — see [What's improved](#-whats-improved-in-this-version) below.

---

## ✨ Features

- **Fluid, held‑key movement** — press and hold a direction and the player glides continuously through the corridors at a constant speed, exactly like a classic arcade maze game. Release the key and it stops immediately; switch directions mid‑corner without breaking stride.
- **Procedural, always‑solvable mazes** — a new maze every level, and the exit is guaranteed to be reachable (it's picked as the farthest point from the start via a breadth‑first search).
- **Progressive difficulty** — corridors shrink level after level, capped at a sensible minimum so the maze never becomes unplayably small.
- **Stable at any size** — maze generation was rewritten to be non‑recursive, removing the crash risk Python's recursion limit posed on large, tightly‑packed mazes.
- **Pause, restart, mute** — full in‑game controls, a proper menu, a level‑clear transition, timers, and a game‑complete screen.
- **Graceful fallbacks** — missing icon or music files never crash the game.

---

## 🎮 How to Play

| Element | Meaning |
|---|---|
| 🔵 Blue tile | Start point |
| 🟠 Orange pulsing dot | Exit / goal |
| 🟢 Green circle | You |

Get from the blue tile to the orange goal to advance. Clear level 10 to win.

### Controls

| Key | Action |
|---|---|
| `↑ ↓ ← →` or `W A S D` | Move — **hold to keep moving**, release to stop |
| `P` or `ESC` | Pause / resume |
| `R` | Restart the current level |
| `M` | Mute / unmute music |
| `SPACE` / `ENTER` | Start game (menu) / play again (after finishing) |
| `ESC` (in menu) | Quit |

---

## 🚀 Installation & Usage

### Prerequisites
Python 3.8+ installed on your system.

### Steps
```bash
# 1. Extract or clone the project
cd hazartoo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the game
python3 app.py
```

---

## 🛠 What's improved in this version

This is a from-scratch rewrite of the movement and maze systems on top of the original game concept:

1. **Continuous, held-key movement** (the main ask): the player now moves smoothly cell‑by‑cell for as long as a direction key is held, instead of nudging one tile per key press. Movement is frame‑rate independent (delta‑time based) and turns feel responsive even around corners.
2. **Non‑recursive maze generation**: the original generator carved the maze with a recursive function. On higher levels the maze can contain several thousand cells, and Python's default recursion limit (1000) made that a real stability risk. The generator was rewritten iteratively with an explicit stack — it now scales to any maze size safely.
3. **Guaranteed solvable exit**: the exit is now chosen with a breadth‑first search as the cell farthest from the start *among the cells the generator actually carved*, so it's always reachable. The original always placed the exit in the bottom‑right corner, which could technically land on a wall.
4. **Performance**: the maze is rendered once to an off‑screen surface per level and then just blitted every frame, instead of drawing every single tile 60 times a second.
5. **Full game‑feel pass**: pause menu, restart, mute toggle, per‑level and total timers, a proper start menu, a level‑clear transition, and a game‑complete screen with your time.
6. **New visual identity**: a new name, icon, and color palette (see below).
7. **Safer resource loading**: icon and music loading failures are caught individually and never crash the game or leave the mixer in a bad state.

---

## 🎨 Name & Logo

The game was renamed **Hazartoo**, from the Persian word **هزارتو** (*hezâr-tu*, literally "a thousand insides") — the everyday Persian word for *labyrinth/maze*. The new icon is a stylised square labyrinth spiral running from the start (green) to the exit (orange), matching the in‑game colors.

---

## 📁 Project Structure

```
hazartoo/
├── app.py              # game source
├── requirements.txt
├── LICENSE
├── img/
│   ├── icon.png         # window icon (256×256)
│   ├── icon_512.png      # high-res icon
│   └── banner.png        # readme banner
└── music/
    └── game_music.mp3
```

---

## 📜 License

See [LICENSE](LICENSE).
