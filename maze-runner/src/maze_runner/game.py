import sys
import random
import pygame

from .config import (
    CELL_SIZE, FPS, HUD_HEIGHT,
    COLOR_BG, COLOR_WALL, COLOR_WALL_EDGE, COLOR_PATH,
    COLOR_PLAYER, COLOR_PLAYER_GLOW, COLOR_GOAL,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_ACCENT,
    STATE_MENU, STATE_PLAYING, STATE_WIN,
)
from .maze import generate_solvable_maze
from .audio import SoundManager
from .save_manager import SaveManager


class Game:
    def __init__(self):
        pygame.init()
        self.sound = SoundManager()

        # Load saved progress first to determine initial level
        self.save_manager = SaveManager()
        saved_data = self.save_manager.load_progress()
        self.level_num = saved_data["current_level"]
        self.best_times = saved_data["best_times"]
        self.total_play_time = saved_data["total_play_time"]
        
        # Calculate initial window size based on current level
        base_size = 15
        size_increase = (self.level_num - 1) * 2
        maze_size = base_size + size_increase
        
        self.hud_height = HUD_HEIGHT
        self.width = maze_size * CELL_SIZE
        self.height = maze_size * CELL_SIZE + self.hud_height

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
        self.elapsed = 0
        self.trail = []
        self.anim_t = 0.0

    def load_level(self, level_num):
        self.level_num = level_num
        self.move_count = 0
        self.trail = []

        # Check if this level has a saved map
        saved_level = self.save_manager.load_level_map(level_num)
        if saved_level:
            self.grid = saved_level["grid"]
            self.player = tuple(saved_level["player"])
            self.goal = tuple(saved_level["goal"])
        else:
            # Infinite level generation - maze size increases with level
            base_size = 15
            size_increase = (level_num - 1) * 2
            maze_size = base_size + size_increase
            
            grid, start, goal = generate_solvable_maze(maze_size, maze_size)
            self.grid = grid
            self.player = start
            self.goal = goal
            
            # Save this level's map for future replay
            self.save_manager.save_level_map(level_num, grid, start, goal)
        
        # Resize window to fit current maze
        maze_size = len(self.grid)
        self.width = maze_size * CELL_SIZE
        self.height = maze_size * CELL_SIZE + self.hud_height
        self.screen = pygame.display.set_mode((self.width, self.height))

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
        # Save best time for this level
        if self.level_num not in self.best_times or self.elapsed < self.best_times[self.level_num]:
            self.best_times[self.level_num] = self.elapsed
        self.total_play_time += self.elapsed
        # Add to leaderboard
        self.save_manager.add_to_leaderboard(self.level_num, self.elapsed)
        # Save progress
        self.save_manager.save_progress(self.level_num + 1, self.best_times, self.total_play_time)
        self.state = STATE_WIN


    def update(self):
        self.anim_t += 1
        if self.state != STATE_PLAYING:
            return

        now = pygame.time.get_ticks()
        self.elapsed = (now - self.start_ticks) / 1000.0

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

        # Goal is hidden - no visual indicator
        # Player must find the exit by exploring

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

        level_txt = self.font_medium.render(f"Level {self.level_num}", True, COLOR_TEXT)
        self.screen.blit(level_txt, (16, 16))

        moves_txt = self.font_small.render(f"Moves: {self.move_count}", True, COLOR_TEXT_DIM)
        self.screen.blit(moves_txt, (200, 20))

        time_txt = self.font_small.render(f"Time: {self.elapsed:0.1f}s", True, COLOR_TEXT_DIM)
        self.screen.blit(time_txt, (self.width - 160, 20))
        
        best_time = self.best_times.get(self.level_num)
        best_str = f"{best_time:0.1f}s" if best_time is not None else "--"
        best_txt = self.font_small.render(f"Best: {best_str}", True, COLOR_TEXT_DIM)
        self.screen.blit(best_txt, (self.width - 160, 40))
        
        leaderboard = self.save_manager.load_leaderboard()
        if leaderboard:
            rank_txt = self.font_small.render(f"Rank: {self.get_player_rank(leaderboard)}", True, COLOR_TEXT_DIM)
            self.screen.blit(rank_txt, (self.width - 160, 60))

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

    def get_player_rank(self, leaderboard):
        # Find player's rank based on total levels completed and best times
        player_score = sum(1 for lvl, time in self.best_times.items() if time > 0)
        ranked_above = sum(1 for entry in leaderboard if entry["level"] > player_score)
        return ranked_above + 1

    def draw_menu(self):
        self.screen.fill(COLOR_BG)
        title = self.font_big.render("Maze Runner", True, COLOR_ACCENT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 80))

        lines = [
            "Move with Arrow Keys or WASD",
            "Find the hidden exit in the maze",
            "",
            f"Current Level: {self.level_num}",
            f"Total Play Time: {self.total_play_time:.1f}s",
            f"Levels Completed: {len([t for t in self.best_times.values() if t > 0])}",
            "",
            "Press ENTER to continue",
            "Press C to clear progress",
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
                f"Level Complete! Time: {self.elapsed:.1f}s", "ENTER for next level   |   R to replay", COLOR_GOAL)

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
                            # Load from saved level or start fresh
                            saved_data = self.save_manager.load_progress()
                            self.level_num = saved_data["current_level"]
                            self.best_times = saved_data["best_times"]
                            self.total_play_time = saved_data["total_play_time"]
                            self.load_level(self.level_num)
                        elif event.key == pygame.K_c:
                            # Clear progress and restart
                            self.save_manager.clear_progress()
                            self.level_num = 1
                            self.best_times = {}
                            self.total_play_time = 0

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


            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
