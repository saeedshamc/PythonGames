# ============================================================
#  HAZARTOO (هزارتو) - Procedural Maze Adventure
#  نسخه بهبود یافته - حرکت پیوسته با کیبرد + ماز پایدار برای مراحل بزرگ
# ============================================================
import sys
import random
from collections import deque

import pygame

# ------------------------------------------------------------
# ثابت‌ها
# ------------------------------------------------------------
WALL, EMPTY = 1, 0

# رنگ‌ها (RGB) - پالت هماهنگ با لوگو
BG_DARK      = (10, 11, 18)
WALL_COLOR   = (14, 16, 26)
WALL_EDGE    = (28, 32, 48)
FLOOR_COLOR  = (232, 234, 240)
FLOOR_LINE   = (214, 217, 226)
START_COLOR  = (70, 130, 255)
END_COLOR    = (255, 150, 40)
PLAYER_COLOR = (60, 220, 140)
PLAYER_DARK  = (30, 150, 90)
TEXT_COLOR   = (240, 241, 246)
MUTED_COLOR  = (160, 165, 180)
ACCENT_COLOR = (60, 220, 140)
OVERLAY      = (8, 9, 15, 200)

WIN_W, WIN_H = 900, 600
FPS = 60

START_SIZE = 64      # اندازه بلاک در مرحله ۱ (پیکسل)
SIZE_STEP  = 6        # هر مرحله چقدر بلاک‌ها کوچک‌تر می‌شوند
MIN_CELL   = 18        # کوچک‌ترین اندازه مجاز بلاک (تا ماز همیشه قابل بازی/دیدن بماند)
MAX_LEVEL  = 10

BASE_SPEED_CELLS_PER_SEC = 6.2   # سرعت حرکت بازیکن بر حسب «خانه در ثانیه»

# ------------------------------------------------------------
# راه‌اندازی pygame
# ------------------------------------------------------------
pygame.init()
pygame.display.set_caption("Hazartoo | هزارتو")
screen = pygame.display.set_mode((WIN_W, WIN_H))
clock = pygame.time.Clock()

# آیکون پنجره - اگر فایل موجود نبود بازی نباید کرش کند
try:
    pygame.display.set_icon(pygame.image.load("img/icon.png"))
except Exception:
    pass

pygame.font.init()
FONT_XL = pygame.font.SysFont("arial", 64, bold=True)
FONT_LG = pygame.font.SysFont("arial", 34, bold=True)
FONT_MD = pygame.font.SysFont("arial", 24, bold=True)
FONT_SM = pygame.font.SysFont("arial", 18)

# موزیک پس‌زمینه - اختیاری و ایمن در برابر نبود فایل
music_available = False
try:
    pygame.mixer.init()
    pygame.mixer.music.load("music/game_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    music_available = True
except Exception:
    music_available = False

music_on = True
if music_available:
    pygame.mixer.music.play(-1)


# ------------------------------------------------------------
# تولید ماز به صورت غیربازگشتی (Iterative DFS)
#
# نسخه‌ی قبلی این تابع را با «بازگشت» (recursion) پیاده‌سازی کرده بود.
# مشکل: در مراحل بالاتر که بلاک‌ها کوچک می‌شوند تعداد خانه‌های ماز به
# چند هزار می‌رسد و عمق بازگشت از سقف پیش‌فرض پایتون (۱۰۰۰) عبور
# می‌کند و بازی با خطای RecursionError کرش می‌کند.
# اینجا همان الگوریتم را با یک پشته (stack) دستی نوشته‌ایم که برای
# هر اندازه‌ای از ماز پایدار است.
# ------------------------------------------------------------
def maze_generator(w, h):
    WIDTH = w if w % 2 != 0 else w - 1
    HEIGHT = h if h % 2 != 0 else h - 1
    WIDTH = max(WIDTH, 5)
    HEIGHT = max(HEIGHT, 5)

    maze = {(x, y): WALL for x in range(WIDTH) for y in range(HEIGHT)}

    start = (1, 1)
    maze[start] = EMPTY
    visited = {start}
    stack = [start]

    while stack:
        x, y = stack[-1]
        neighbors = []
        if y > 1 and (x, y - 2) not in visited:
            neighbors.append((x, y - 2, x, y - 1))
        if y < HEIGHT - 2 and (x, y + 2) not in visited:
            neighbors.append((x, y + 2, x, y + 1))
        if x > 1 and (x - 2, y) not in visited:
            neighbors.append((x - 2, y, x - 1, y))
        if x < WIDTH - 2 and (x + 2, y) not in visited:
            neighbors.append((x + 2, y, x + 1, y))

        if not neighbors:
            stack.pop()
            continue

        nx, ny, wx, wy = random.choice(neighbors)
        maze[(wx, wy)] = EMPTY   # برداشتن دیوار بین دو خانه
        maze[(nx, ny)] = EMPTY
        visited.add((nx, ny))
        stack.append((nx, ny))

    # -----------------------------------------------------
    # پیدا کردن نقطه‌ی پایان با BFS: دورترین خانه‌ی قابل دسترس از
    # نقطه‌ی شروع. این تضمین می‌کند که همیشه یک مسیر واقعی بین
    # شروع و پایان وجود دارد (در نسخه‌ی قبلی امکان داشت نقطه‌ی
    # پایان اصلاً به بقیه‌ی ماز متصل نباشد).
    # -----------------------------------------------------
    dist = {start: 0}
    q = deque([start])
    farthest = start
    while q:
        cx, cy = q.popleft()
        if dist[(cx, cy)] > dist[farthest]:
            farthest = (cx, cy)
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nxt = (cx + dx, cy + dy)
            if maze.get(nxt, WALL) == EMPTY and nxt not in dist:
                dist[nxt] = dist[(cx, cy)] + 1
                q.append(nxt)

    return maze, WIDTH, HEIGHT, farthest


def build_maze_surface(maze, w, h, size):
    """
    رسم یک بار ماز روی یک Surface جدا و استفاده از آن به عنوان کش.
    این کار به جای رسم هزاران مستطیل در هر فریم، فقط یک‌بار در هر
    مرحله انجام می‌شود و عملکرد بازی را به‌طور محسوسی بهتر می‌کند،
    خصوصا در مراحل بالا که تعداد خانه‌ها زیاد است.
    """
    surf = pygame.Surface((w * size, h * size))
    surf.fill(WALL_COLOR)
    inset = max(1, size // 14)
    for x in range(w):
        for y in range(h):
            if maze.get((x, y), WALL) == EMPTY:
                rect = (x * size, y * size, size, size)
                pygame.draw.rect(surf, FLOOR_COLOR, rect)
                if size > 6:
                    pygame.draw.rect(surf, FLOOR_LINE, rect, 1)
    return surf


# ------------------------------------------------------------
# منطق یک مرحله
# ------------------------------------------------------------
class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.size = max(MIN_CELL, START_SIZE - (level_num - 1) * SIZE_STEP)
        w = WIN_W // self.size
        h = WIN_H // self.size
        self.maze, self.w, self.h, self.end_cell = maze_generator(w, h)
        self.start_cell = (1, 1)
        self.surface = build_maze_surface(self.maze, self.w, self.h, self.size)

        # موقعیت پیکسلی بازیکن (برای حرکت نرم و پیوسته)
        self.player_px = float(self.start_cell[0] * self.size)
        self.player_py = float(self.start_cell[1] * self.size)
        self.from_cell = self.start_cell
        self.to_cell = self.start_cell
        self.t = 0.0          # پیشرفت حرکت بین from_cell و to_cell (0..1)
        self.current_dir = (0, 0)

        self.speed = BASE_SPEED_CELLS_PER_SEC  # خانه بر ثانیه

    def cell_open(self, cell):
        return self.maze.get(cell, WALL) == EMPTY

    def offset(self):
        """آفست برای وسط‌چین کردن ماز داخل پنجره."""
        ox = (WIN_W - self.w * self.size) // 2
        oy = (WIN_H - self.h * self.size) // 2
        return ox, oy

    # --------------------------------------------------------
    # این متد قلب سیستم «حرکت پیوسته با نگه‌داشتن کلید» است.
    # تا وقتی کاربر جهت را نگه داشته باشد، بازیکن با سرعت ثابت به
    # همان سمت حرکت می‌کند و دقیقا سر هر خانه دوباره تصمیم می‌گیرد
    # که ادامه بدهد، بچرخد یا (اگر دیوار جلویش بود) بایستد.
    # آزاد شدن کلید فوراً بازیکن را متوقف می‌کند.
    # --------------------------------------------------------
    def update(self, dt, desired_dir):
        step = self.speed * dt  # چقدر از یک خانه را در این فریم طی می‌کنیم

        while step > 0:
            if self.t <= 0.0 and self.from_cell == self.to_cell:
                # بازیکن دقیقا وسط یک خانه است -> تصمیم‌گیری برای جهت بعدی
                next_dir = None
                if desired_dir != (0, 0):
                    cand = (self.from_cell[0] + desired_dir[0],
                            self.from_cell[1] + desired_dir[1])
                    if self.cell_open(cand):
                        next_dir = desired_dir
                if next_dir is None and self.current_dir != (0, 0):
                    cand = (self.from_cell[0] + self.current_dir[0],
                            self.from_cell[1] + self.current_dir[1])
                    if self.cell_open(cand):
                        next_dir = self.current_dir

                if next_dir is None:
                    self.current_dir = (0, 0)
                    break  # هیچ حرکتی ممکن نیست، همینجا بمان

                self.current_dir = next_dir
                self.to_cell = (self.from_cell[0] + next_dir[0],
                                 self.from_cell[1] + next_dir[1])
                self.t = 0.0

            # حرکت به سمت to_cell
            remaining = 1.0 - self.t
            if step >= remaining:
                self.t = 1.0
                step -= remaining
                self.from_cell = self.to_cell
                self.t = 0.0
            else:
                self.t += step
                step = 0.0

        self.player_px = (self.from_cell[0] + self.current_dir[0] * self.t) * self.size
        self.player_py = (self.from_cell[1] + self.current_dir[1] * self.t) * self.size

    @property
    def player_cell(self):
        return self.from_cell if self.t < 0.5 else self.to_cell

    @property
    def finished(self):
        return self.from_cell == self.end_cell and self.t == 0.0

    def draw(self, surface, elapsed_time):
        ox, oy = self.offset()
        surface.blit(self.surface, (ox, oy))

        s = self.size
        # نقطه‌ی شروع
        sx, sy = self.start_cell
        pygame.draw.rect(surface, START_COLOR,
                          (ox + sx * s, oy + sy * s, s, s), border_radius=max(2, s // 5))

        # نقطه‌ی پایان با یک ضربان ملایم (pulse) برای دیده شدن بهتر
        ex, ey = self.end_cell
        pulse = 3 + int(2 * abs(pygame.math.Vector2(1, 0).rotate(elapsed_time * 200).x))
        cx, cy = ox + ex * s + s // 2, oy + ey * s + s // 2
        pygame.draw.circle(surface, END_COLOR, (cx, cy), max(4, s // 2 - pulse))
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), max(4, s // 2 - pulse), 2)

        # بازیکن
        px = ox + self.player_px + s / 2
        py = oy + self.player_py + s / 2
        r = max(4, int(s * 0.38))
        pygame.draw.circle(surface, PLAYER_DARK, (int(px), int(py) + 2), r)
        pygame.draw.circle(surface, PLAYER_COLOR, (int(px), int(py)), r)
        pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), r, 2)


# ------------------------------------------------------------
# کمکی‌های رابط کاربری
# ------------------------------------------------------------
def draw_text_center(surface, text, font, color, cy, cx=WIN_W // 2):
    img = font.render(text, True, color)
    surface.blit(img, (cx - img.get_width() // 2, cy - img.get_height() // 2))


def draw_overlay():
    ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    ov.fill(OVERLAY)
    screen.blit(ov, (0, 0))


def format_time(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    ms = int((seconds - int(seconds)) * 100)
    return f"{m:02d}:{s:02d}.{ms:02d}"


# ------------------------------------------------------------
# مدیریت کلیدهای نگه‌داشته‌شده (برای حرکت پیوسته)
# ترتیب فشردن کلیدها را نگه می‌داریم تا اگر کاربر دو جهت را با هم
# نگه‌دارد، آخرین کلید فشرده‌شده اولویت داشته باشد؛ و با رها کردن
# آن، بازی بلافاصله به کلید قبلی (اگر هنوز نگه‌داشته) برمی‌گردد.
# ------------------------------------------------------------
KEY_DIRS = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}

held_keys = []  # لیست کلیدهای جهت‌دار که همین الان نگه داشته شده‌اند


def current_desired_dir():
    for k in reversed(held_keys):
        if k in KEY_DIRS:
            return KEY_DIRS[k]
    return (0, 0)


# ------------------------------------------------------------
# حالت‌های بازی
# ------------------------------------------------------------
MENU, PLAYING, LEVEL_CLEAR, PAUSED, GAME_COMPLETE = range(5)

state = MENU
level_num = 1
level = None
level_start_time = 0.0
total_start_time = 0.0
level_clear_timer = 0.0
pause_entered_at = 0.0
best_total_time = None


def new_game():
    global level_num, level, total_start_time
    level_num = 1
    level = Level(level_num)
    total_start_time = pygame.time.get_ticks() / 1000.0
    start_level_timer()


def start_level_timer():
    global level_start_time
    level_start_time = pygame.time.get_ticks() / 1000.0


def toggle_music():
    global music_on
    if not music_available:
        return
    music_on = not music_on
    if music_on:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()


# ------------------------------------------------------------
# حلقه‌ی اصلی بازی
# ------------------------------------------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    dt = min(dt, 0.05)  # جلوگیری از پرش حرکت هنگام لگ یا جابه‌جایی پنجره
    now = pygame.time.get_ticks() / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in KEY_DIRS and event.key not in held_keys:
                held_keys.append(event.key)

            if event.key == pygame.K_ESCAPE:
                if state == PLAYING:
                    state = PAUSED
                    pause_entered_at = now
                elif state == PAUSED:
                    paused_for = now - pause_entered_at
                    level_start_time += paused_for
                    total_start_time += paused_for
                    state = PLAYING
                else:
                    running = False

            if event.key == pygame.K_m:
                toggle_music()

            if state == MENU and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                new_game()
                state = PLAYING

            elif state == PAUSED and event.key == pygame.K_p:
                paused_for = now - pause_entered_at
                level_start_time += paused_for
                total_start_time += paused_for
                state = PLAYING

            elif state == PLAYING and event.key == pygame.K_p:
                state = PAUSED
                pause_entered_at = now

            elif state == PLAYING and event.key == pygame.K_r:
                level = Level(level_num)
                start_level_timer()

            elif state == GAME_COMPLETE and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                new_game()
                state = PLAYING

            elif state == PAUSED and event.key == pygame.K_r:
                new_game()
                state = PLAYING

        elif event.type == pygame.KEYUP:
            if event.key in held_keys:
                held_keys.remove(event.key)

    # ---------------- به‌روزرسانی وضعیت ----------------
    if state == PLAYING:
        desired = current_desired_dir()
        level.update(dt, desired)

        if level.finished:
            if level_num >= MAX_LEVEL:
                state = GAME_COMPLETE
                total_time = now - total_start_time
                if best_total_time is None or total_time < best_total_time:
                    best_total_time = total_time
            else:
                state = LEVEL_CLEAR
                level_clear_timer = now

    elif state == LEVEL_CLEAR:
        if now - level_clear_timer > 1.1:
            level_num += 1
            level = Level(level_num)
            start_level_timer()
            held_keys.clear()
            state = PLAYING

    # ---------------- رسم ----------------
    screen.fill(BG_DARK)

    if state == MENU:
        draw_text_center(screen, "HAZARTOO", FONT_XL, TEXT_COLOR, WIN_H // 2 - 130)
        draw_text_center(screen, "یک ماز تصادفی و بی‌پایان", FONT_MD, MUTED_COLOR, WIN_H // 2 - 70)
        draw_text_center(screen, "برای شروع SPACE یا ENTER را بزنید", FONT_LG, ACCENT_COLOR, WIN_H // 2)
        draw_text_center(screen, "حرکت: کلیدهای جهت‌دار یا W A S D  (نگه دارید تا پیوسته حرکت کند)",
                          FONT_SM, MUTED_COLOR, WIN_H // 2 + 60)
        draw_text_center(screen, "P = توقف موقت      R = ری‌استارت مرحله      M = قطع/وصل موزیک      ESC = خروج",
                          FONT_SM, MUTED_COLOR, WIN_H // 2 + 90)

    elif state in (PLAYING, PAUSED, LEVEL_CLEAR):
        level.draw(screen, pause_entered_at if state == PAUSED else now)

        # نوار بالای صفحه: اطلاعات مرحله
        hud = pygame.Surface((WIN_W, 46), pygame.SRCALPHA)
        hud.fill((8, 9, 15, 190))
        screen.blit(hud, (0, 0))
        clock_now = pause_entered_at if state == PAUSED else now
        level_elapsed = clock_now - level_start_time
        total_elapsed = clock_now - total_start_time
        info = f"Level {level_num}/{MAX_LEVEL}      Time {format_time(level_elapsed)}      Total {format_time(total_elapsed)}"
        img = FONT_SM.render(info, True, TEXT_COLOR)
        screen.blit(img, (16, 13))

        hint = FONT_SM.render("P  توقف   |   R  شروع دوباره‌ی مرحله   |   M  موزیک", True, MUTED_COLOR)
        screen.blit(hint, (WIN_W - hint.get_width() - 16, 13))

        if state == PAUSED:
            draw_overlay()
            draw_text_center(screen, "توقف موقت", FONT_XL, TEXT_COLOR, WIN_H // 2 - 40)
            draw_text_center(screen, "برای ادامه P یا ESC را بزنید   |   R برای شروع دوباره از مرحله ۱",
                              FONT_SM, MUTED_COLOR, WIN_H // 2 + 30)

        if state == LEVEL_CLEAR:
            draw_overlay()
            draw_text_center(screen, f"مرحله {level_num} تمام شد!", FONT_XL, ACCENT_COLOR, WIN_H // 2 - 20)
            draw_text_center(screen, "مرحله بعدی در حال ساخت...", FONT_SM, MUTED_COLOR, WIN_H // 2 + 40)

    elif state == GAME_COMPLETE:
        draw_text_center(screen, "شما بازی را کامل کردید!", FONT_XL, ACCENT_COLOR, WIN_H // 2 - 90)
        draw_text_center(screen, f"زمان کل: {format_time(now - total_start_time)}", FONT_LG, TEXT_COLOR, WIN_H // 2 - 20)
        if best_total_time is not None:
            draw_text_center(screen, f"بهترین زمان این نشست: {format_time(best_total_time)}",
                              FONT_SM, MUTED_COLOR, WIN_H // 2 + 25)
        draw_text_center(screen, "برای بازی دوباره SPACE را بزنید", FONT_MD, TEXT_COLOR, WIN_H // 2 + 90)

    pygame.display.flip()

pygame.quit()
sys.exit()
