import sys
import pygame

from .config import (
    CELL_SIZE, FPS, HUD_HEIGHT,
    COLOR_BG, COLOR_WALL, COLOR_WALL_EDGE, COLOR_PATH,
    COLOR_PLAYER, COLOR_PLAYER_GLOW, COLOR_GOAL, COLOR_DANGER,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_ACCENT,
    STATE_MENU, STATE_PLAYING, STATE_WIN, STATE_LOSE, STATE_GAME_COMPLETE,
)
from .levels import FIXED_MAZE_LEVEL_1, LEVEL_CONFIGS, TOTAL_LEVELS
from .maze import generate_solvable_maze
from .audio import SoundManager


class Game:
    def __init__(self):
        pygame.init()
        self.sound = SoundManager()

        max_w = max(cfg[0] for cfg in LEVEL_CONFIGS if cfg)
        max_h = max(cfg[1] for cfg in LEVEL_CONFIGS if cfg)
        max_w = max(max_w, len(FIXED_MAZE_LEVEL_1[0]))
        max_h = max(max_h, len(FIXED_MAZE_LEVEL_1))

        self.hud_height = HUD_HEIGHT
        self.width = max_w * CELL_SIZE
        self.height = max_h * CELL_SIZE + self.hud_height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Maze Runner")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("arial", 42, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("arial", 18)

        self.state = STATE_MENU
        self.level_num = 1
        self.grid = None
        self.player = (1, 1)
        self.goal = (1, 1)
        self.move_count = 0
        self.start_ticks = 0
        self.time_limit = 999
        self.elapsed = 0
        self.trail = []
        self.anim_t = 0.0

    def load_level(self, level_num):
        self.level_num = level_num
        self.move_count = 0
        self.trail = []

        if level_num == 1:
            self.grid = [row[:] for row in FIXED_MAZE_LEVEL_1]
            self.player = (1, 1)
            self.goal = (len(self.grid[0]) - 2, len(self.grid) - 2)
            self.time_limit = LEVEL_CONFIGS[1][2]
        else:
            w, h, time_limit = LEVEL_CONFIGS[level_num]
            grid, start, goal = generate_solvable_maze(w, h)
            self.grid = grid
            self.player = start
            self.goal = goal
            self.time_limit = time_limit

        self.start_ticks = pygame.time.get_ticks()
        self.state = STATE_PLAYING

    def try_move(self, dx, dy):
        x, y = self.player
        nx, ny = x + dx, y + dy
        h = len(self.grid)
        w = len(self.grid[0])
        if 0 <= nx < w and 0 <= ny < h and self.grid[ny][nx] == 0:
            self.trail.append((x, y, 1.0))
            self.player = (nx, ny)
            self.move_count += 1
            self.sound.play("move")
            if self.player == self.goal:
                self.on_win()
        else:
            self.sound.play("wall")

    def on_win(self):
        self.sound.play("win")
        if self.level_num >= TOTAL_LEVELS:
            self.state = STATE_GAME_COMPLETE
        else:
            self.state = STATE_WIN

    def on_time_up(self):
        self.sound.play("time_up")
        self.state = STATE_LOSE

    def update(self):
        self.anim_t += 1
        if self.state != STATE_PLAYING:
            return

        now = pygame.time.get_ticks()
        self.elapsed = (now - self.start_ticks) / 1000.0

        if self.elapsed >= self.time_limit:
            self.on_time_up()
            return

        self.trail = [(x, y, a - 0.03) for (x, y, a) in self.trail if a - 0.03 > 0]

    def draw_maze(self):
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                rect = pygame.Rect(x * CELL_SIZE, self.hud_height + y * CELL_SIZE,
                                    CELL_SIZE, CELL_SIZE)
                if val == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                    pygame.draw.rect(self.screen, COLOR_WALL_EDGE, rect, 1)
                else:
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)

        for (x, y, a) in self.trail:
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = self.hud_height + y * CELL_SIZE + CELL_SIZE // 2
            radius = int(CELL_SIZE * 0.15 * a) + 1
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*COLOR_PLAYER, int(120 * a)),
                                (CELL_SIZE // 2, CELL_SIZE // 2), radius)
            self.screen.blit(surf, (cx - CELL_SIZE // 2, cy - CELL_SIZE // 2))

        gx, gy = self.goal
        pulse = 3 + 2 * abs((self.anim_t % 60) - 30) / 30
        gcx = gx * CELL_SIZE + CELL_SIZE // 2
        gcy = self.hud_height + gy * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, COLOR_GOAL, (gcx, gcy), CELL_SIZE // 2 - 2)
        pygame.draw.circle(self.screen, (255, 255, 255), (gcx, gcy),
                            int(CELL_SIZE // 2 - 2 + pulse), 2)

        px, py = self.player
        pcx = px * CELL_SIZE + CELL_SIZE // 2
        pcy = self.hud_height + py * CELL_SIZE + CELL_SIZE // 2
        glow_r = CELL_SIZE // 2 + 4 + int(2 * abs((self.anim_t % 40) - 20) / 20)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLOR_PLAYER_GLOW, 70), (glow_r, glow_r), glow_r)
        self.screen.blit(glow_surf, (pcx - glow_r, pcy - glow_r))
        pygame.draw.circle(self.screen, COLOR_PLAYER, (pcx, pcy), CELL_SIZE // 2 - 3)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (12, 12, 18), (0, 0, self.width, self.hud_height))
        pygame.draw.line(self.screen, COLOR_ACCENT, (0, self.hud_height),
                          (self.width, self.hud_height), 2)

        level_txt = self.font_medium.render(f"Level {self.level_num}/{TOTAL_LEVELS}", True, COLOR_TEXT)
        self.screen.blit(level_txt, (16, 16))

        moves_txt = self.font_small.render(f"Moves: {self.move_count}", True, COLOR_TEXT_DIM)
        self.screen.blit(moves_txt, (200, 20))

        remaining = max(0, self.time_limit - self.elapsed)
        time_color = COLOR_TEXT_DIM if remaining > 10 else COLOR_DANGER
        time_txt = self.font_small.render(f"Time: {remaining:0.1f}s", True, time_color)
        self.screen.blit(time_txt, (self.width - 160, 20))

    def draw_center_message(self, title, subtitle, color):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 200))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.font_big.render(title, True, color)
        self.screen.blit(title_surf,
                          (self.width // 2 - title_surf.get_width() // 2, self.height // 2 - 60))

        sub_surf = self.font_medium.render(subtitle, True, COLOR_TEXT_DIM)
        self.screen.blit(sub_surf,
                          (self.width // 2 - sub_surf.get_width() // 2, self.height // 2))

    def draw_menu(self):
        self.screen.fill(COLOR_BG)
        title = self.font_big.render("Maze Runner", True, COLOR_ACCENT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 80))

        lines = [
            "Move with Arrow Keys or WASD",
            "Reach the yellow exit before time runs out",
            "Each level is bigger and harder than the last",
            "",
            "Press ENTER to start",
            "Press ESC to quit",
        ]
        y = 200
        for line in lines:
            surf = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(surf, (self.width // 2 - surf.get_width() // 2, y))
            y += 32

    def draw(self):
        if self.state == STATE_MENU:
            self.draw_menu()
            pygame.display.flip()
            return

        self.screen.fill(COLOR_BG)
        self.draw_maze()
        self.draw_hud()

        if self.state == STATE_WIN:
            self.draw_center_message(
                "You Win!", "ENTER for next level   |   R to replay", COLOR_GOAL)
        elif self.state == STATE_LOSE:
            self.draw_center_message(
                "Time's Up!", "R to try again   |   ESC to quit", COLOR_DANGER)
        elif self.state == STATE_GAME_COMPLETE:
            self.draw_center_message(
                "Congratulations! You beat all levels", "R to restart from level 1", COLOR_GOAL)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif self.state == STATE_MENU:
                        if event.key == pygame.K_RETURN:
                            self.load_level(1)

                    elif self.state == STATE_PLAYING:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.try_move(0, -1)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.try_move(0, 1)
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            self.try_move(-1, 0)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.try_move(1, 0)

                    elif self.state == STATE_WIN:
                        if event.key == pygame.K_RETURN:
                            self.load_level(self.level_num + 1)
                        elif event.key == pygame.K_r:
                            self.load_level(self.level_num)

                    elif self.state == STATE_LOSE:
                        if event.key == pygame.K_r:
                            self.load_level(self.level_num)

                    elif self.state == STATE_GAME_COMPLETE:
                        if event.key == pygame.K_r:
                            self.load_level(1)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
