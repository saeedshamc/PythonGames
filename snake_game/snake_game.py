import pygame
import random
import sys
import json
import os
import datetime

# ---------- Settings ----------
CELL_SIZE = 15
GRID_WIDTH = 70
GRID_HEIGHT = 46
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS_START = 10          # starting game speed
FPS_INCREASE_EVERY = 5  # every N points, speed up a bit
MAX_FPS = 25             # cap so it doesn't get impossibly fast
DATA_FILE = "snake_data.json"  # File to store high score and statistics

# Colors
BLACK = (15, 15, 15)
GREEN = (50, 205, 50)
DARK_GREEN = (30, 140, 30)
RED = (220, 50, 50)
WHITE = (240, 240, 240)
GRAY = (60, 60, 60)
GRID_LINE = (35, 35, 35)
GOLD = (255, 215, 0)
BLUE = (50, 100, 220)
PURPLE = (147, 112, 219)
CYAN = (0, 200, 200)


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 48, bold=True)
        self.high_score = self.load_high_score()
        self.state = "menu"  # menu, game, pause, settings, high_scores
        self.menu_options = ["Start Game", "Settings", "High Scores", "Quit"]
        self.menu_selected = 0
        
        # Settings
        self.settings = self.load_settings()
        self.settings_options = ["Difficulty", "Snake Color", "Wrap-Around", "Game Mode", "Back"]
        self.settings_selected = 0
        
        # Difficulty options
        self.difficulty_options = ["Easy", "Medium", "Hard"]
        self.difficulty_selected = 0
        
        # Color themes
        self.color_themes = ["Green", "Blue", "Purple", "Red"]
        self.color_selected = 0
        
        # Wrap-around toggle
        self.wrap_around = self.settings.get("wrap_around", True)
        
        # Game modes
        self.game_modes = ["Classic", "Wall", "Obstacles"]
        self.game_mode_selected = 0
        
        # Initialize game state attributes before reset
        self.obstacles = []
        self.power_up = None
        self.power_up_type = None
        self.power_up_timer = 0
        self.base_fps = FPS_START
        
        # Statistics
        self.stats = self.load_stats()
        self.game_start_time = None
        
        self.reset()

    def reset(self):
        # Snake starts in the middle of the screen with an initial length of 3
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)   # moving right
        self.next_direction = self.direction
        self.score = 0
        self.food = self.spawn_food()
        self.game_over = False
        self.fps = self.get_difficulty_fps()
        self.obstacles = self.generate_obstacles()
        
        # Power-ups
        self.power_up = None
        self.power_up_type = None
        self.power_up_timer = 0
        self.base_fps = self.fps

    def load_high_score(self):
        """Load high score from JSON file."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
            except (json.JSONDecodeError, IOError):
                return 0
        return 0

    def save_high_score(self):
        """Save high score to JSON file."""
        data = {'high_score': self.high_score}
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f)
        except IOError:
            pass

    def load_settings(self):
        """Load settings from JSON file."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('settings', {})
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def load_stats(self):
        """Load statistics from JSON file."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('stats', {
                        'games_played': 0,
                        'total_score': 0,
                        'best_time': 0,
                        'leaderboard': []
                    })
            except (json.JSONDecodeError, IOError):
                return {'games_played': 0, 'total_score': 0, 'best_time': 0, 'leaderboard': []}
        return {'games_played': 0, 'total_score': 0, 'best_time': 0, 'leaderboard': []}

    def save_stats(self):
        """Save statistics to JSON file."""
        data = {
            'high_score': self.high_score,
            'settings': {
                'difficulty': self.difficulty_options[self.difficulty_selected],
                'snake_color': self.color_themes[self.color_selected],
                'wrap_around': self.wrap_around,
                'game_mode': self.game_modes[self.game_mode_selected]
            },
            'stats': self.stats
        }
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f)
        except IOError:
            pass

    def save_settings(self):
        """Save settings to JSON file."""
        self.save_stats()

    def get_snake_colors(self):
        """Get snake colors based on selected theme and score progression."""
        theme = self.color_themes[self.color_selected]
        
        # Base colors from theme
        if theme == "Green":
            base_color = GREEN
            dark_base = DARK_GREEN
        elif theme == "Blue":
            base_color = BLUE
            dark_base = (30, 60, 140)
        elif theme == "Purple":
            base_color = PURPLE
            dark_base = (100, 80, 160)
        elif theme == "Red":
            base_color = RED
            dark_base = (180, 30, 30)
        else:
            base_color = GREEN
            dark_base = DARK_GREEN
        
        # Apply score-based color progression
        return self.get_progressive_colors(base_color, dark_base)

    def get_progressive_colors(self, base_color, dark_base):
        """Return colors that shift based on score progression."""
        # Color progression levels based on score
        if self.score < 50:
            return base_color, dark_base
        elif self.score < 100:
            # Shift towards cyan
            return self.blend_colors(base_color, CYAN, 0.3), self.blend_colors(dark_base, CYAN, 0.3)
        elif self.score < 200:
            # More cyan
            return self.blend_colors(base_color, CYAN, 0.5), self.blend_colors(dark_base, CYAN, 0.5)
        elif self.score < 300:
            # Shift towards gold
            return self.blend_colors(base_color, GOLD, 0.4), self.blend_colors(dark_base, GOLD, 0.4)
        elif self.score < 500:
            # More gold
            return self.blend_colors(base_color, GOLD, 0.6), self.blend_colors(dark_base, GOLD, 0.6)
        elif self.score < 750:
            # Shift towards bright orange
            return self.blend_colors(base_color, (255, 165, 0), 0.5), self.blend_colors(dark_base, (255, 165, 0), 0.5)
        elif self.score < 1000:
            # Bright orange
            return self.blend_colors(base_color, (255, 140, 0), 0.7), self.blend_colors(dark_base, (255, 140, 0), 0.7)
        else:
            # Rainbow effect for very high scores (1000+)
            # Cycle through colors based on score
            hue_shift = (self.score // 50) % 6
            rainbow_colors = [
                (255, 0, 0),    # Red
                (255, 165, 0),  # Orange
                (255, 255, 0),  # Yellow
                (0, 255, 0),    # Green
                (0, 0, 255),    # Blue
                (128, 0, 128)   # Purple
            ]
            target_color = rainbow_colors[hue_shift]
            return self.blend_colors(base_color, target_color, 0.8), self.blend_colors(dark_base, target_color, 0.8)

    def blend_colors(self, color1, color2, factor):
        """Blend two colors by a factor (0-1)."""
        r = int(color1[0] + (color2[0] - color1[0]) * factor)
        g = int(color1[1] + (color2[1] - color1[1]) * factor)
        b = int(color1[2] + (color2[2] - color1[2]) * factor)
        return (r, g, b)

    def get_difficulty_fps(self):
        """Get starting FPS based on difficulty."""
        difficulty = self.difficulty_options[self.difficulty_selected]
        if difficulty == "Easy":
            return 8
        elif difficulty == "Medium":
            return 10
        elif difficulty == "Hard":
            return 15
        return FPS_START

    def update_game_stats(self):
        """Update game statistics when game ends."""
        if self.game_start_time:
            game_time = (pygame.time.get_ticks() - self.game_start_time) / 1000  # Convert to seconds
            
            self.stats['games_played'] += 1
            self.stats['total_score'] += self.score
            
            if game_time > self.stats['best_time']:
                self.stats['best_time'] = game_time
            
            # Update leaderboard (top 10 scores)
            entry = {
                'score': self.score,
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'mode': self.game_modes[self.game_mode_selected]
            }
            self.stats['leaderboard'].append(entry)
            self.stats['leaderboard'].sort(key=lambda x: x['score'], reverse=True)
            self.stats['leaderboard'] = self.stats['leaderboard'][:10]  # Keep top 10
            
            if self.score > self.high_score:
                self.high_score = self.score
            
            self.save_stats()

    def generate_obstacles(self):
        """Generate random obstacles for Obstacles mode."""
        mode = self.game_modes[self.game_mode_selected]
        if mode != "Obstacles":
            return []
        
        obstacles = []
        num_obstacles = 15  # Number of obstacles
        
        for _ in range(num_obstacles):
            while True:
                pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                # Don't place obstacles on snake starting position or too close
                start_x, start_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
                if abs(pos[0] - start_x) > 5 or abs(pos[1] - start_y) > 5:
                    if pos not in obstacles:
                        obstacles.append(pos)
                        break
        
        return obstacles

    def spawn_food(self):
        """Places food on a random empty cell."""
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake and pos not in self.obstacles and pos != self.power_up:
                return pos

    def spawn_power_up(self):
        """Randomly spawn a power-up with increased chance at higher scores."""
        if self.power_up is not None:
            return
        
        # Spawn rate increases with score: 10% base + 0.5% per 10 points
        spawn_chance = 0.1 + (self.score / 2000)  # Up to 35% at 500 points
        spawn_chance = min(spawn_chance, 0.35)  # Cap at 35%
        
        if random.random() < spawn_chance:
            power_up_types = ['golden', 'blue', 'purple']
            self.power_up_type = random.choice(power_up_types)
            
            while True:
                pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                if pos not in self.snake and pos not in self.obstacles and pos != self.food:
                    self.power_up = pos
                    break

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    self.handle_menu_input(event.key)
                elif self.state == "game":
                    self.handle_game_input(event.key)
                elif self.state == "pause":
                    self.handle_pause_input(event.key)
                elif self.state == "settings":
                    self.handle_settings_input(event.key)
                elif self.state == "high_scores":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"

    def handle_menu_input(self, key):
        if key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN:
            if self.menu_options[self.menu_selected] == "Start Game":
                self.reset()
                self.game_start_time = pygame.time.get_ticks()
                self.state = "game"
            elif self.menu_options[self.menu_selected] == "Settings":
                self.state = "settings"
            elif self.menu_options[self.menu_selected] == "High Scores":
                self.state = "high_scores"
            elif self.menu_options[self.menu_selected] == "Quit":
                pygame.quit()
                sys.exit()

    def handle_game_input(self, key):
        if key in (pygame.K_UP, pygame.K_w) and self.direction != (0, 1):
            self.next_direction = (0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s) and self.direction != (0, -1):
            self.next_direction = (0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a) and self.direction != (1, 0):
            self.next_direction = (-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d) and self.direction != (-1, 0):
            self.next_direction = (1, 0)
        elif key == pygame.K_r and self.game_over:
            self.reset()
        elif key in (pygame.K_SPACE, pygame.K_p) and not self.game_over:
            self.state = "pause"
        elif key == pygame.K_ESCAPE:
            self.state = "menu"

    def handle_pause_input(self, key):
        if key == pygame.K_ESCAPE or key == pygame.K_SPACE or key == pygame.K_p:
            self.state = "game"
        elif key == pygame.K_r:
            self.reset()
            self.state = "game"
        elif key == pygame.K_q:
            self.state = "menu"

    def handle_settings_input(self, key):
        if key == pygame.K_ESCAPE:
            self.save_settings()
            self.state = "menu"
        elif key == pygame.K_UP:
            self.settings_selected = (self.settings_selected - 1) % len(self.settings_options)
        elif key == pygame.K_DOWN:
            self.settings_selected = (self.settings_selected + 1) % len(self.settings_options)
        elif key == pygame.K_LEFT:
            if self.settings_options[self.settings_selected] == "Difficulty":
                self.difficulty_selected = (self.difficulty_selected - 1) % len(self.difficulty_options)
            elif self.settings_options[self.settings_selected] == "Snake Color":
                self.color_selected = (self.color_selected - 1) % len(self.color_themes)
            elif self.settings_options[self.settings_selected] == "Wrap-Around":
                self.wrap_around = not self.wrap_around
            elif self.settings_options[self.settings_selected] == "Game Mode":
                self.game_mode_selected = (self.game_mode_selected - 1) % len(self.game_modes)
        elif key == pygame.K_RIGHT:
            if self.settings_options[self.settings_selected] == "Difficulty":
                self.difficulty_selected = (self.difficulty_selected + 1) % len(self.difficulty_options)
            elif self.settings_options[self.settings_selected] == "Snake Color":
                self.color_selected = (self.color_selected + 1) % len(self.color_themes)
            elif self.settings_options[self.settings_selected] == "Wrap-Around":
                self.wrap_around = not self.wrap_around
            elif self.settings_options[self.settings_selected] == "Game Mode":
                self.game_mode_selected = (self.game_mode_selected + 1) % len(self.game_modes)
        elif key == pygame.K_RETURN:
            if self.settings_options[self.settings_selected] == "Back":
                self.save_settings()
                self.state = "menu"

    def update(self):
        if self.state != "game":
            return
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        # Calculate new head position
        if self.wrap_around:
            # Wrap around: going off one edge brings you back in on the opposite side
            new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        else:
            # Wall mode: hitting wall causes game over
            new_head = (head_x + dx, head_y + dy)
            if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                return

        # Colliding with itself -> game over
        if new_head in self.snake:
            self.game_over = True
            self.update_game_stats()
            return

        # Colliding with obstacles -> game over
        if new_head in self.obstacles:
            self.game_over = True
            self.update_game_stats()
            return

        self.snake.insert(0, new_head)

        # Eating food -> grow and score
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
            self.spawn_power_up()
            # Speed up a little every few points (more challenge as the snake grows)
            if self.score % (FPS_INCREASE_EVERY * 10) == 0 and self.fps < MAX_FPS:
                self.fps += 1
                self.base_fps = self.fps
        else:
            # No food eaten, remove the tail so length stays the same
            self.snake.pop()

        # Eating power-up
        if new_head == self.power_up:
            if self.power_up_type == 'golden':
                self.score += 20  # Double points
            elif self.power_up_type == 'blue':
                # Slow down temporarily
                self.fps = max(5, self.base_fps - 5)
                self.power_up_timer = 300  # 5 seconds at 60 FPS
            elif self.power_up_type == 'purple':
                # Speed up temporarily
                self.fps = min(MAX_FPS + 5, self.base_fps + 5)
                self.power_up_timer = 300
            
            self.power_up = None
            self.power_up_type = None

        # Handle power-up timer
        if self.power_up_timer > 0:
            self.power_up_timer -= 1
            if self.power_up_timer == 0:
                self.fps = self.base_fps  # Reset to base speed

    def draw_cell(self, pos, color):
        rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_grid(self):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (0, y), (WIDTH, y))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "game":
            self.draw_game()
        elif self.state == "pause":
            self.draw_game()
            self.draw_pause()
        elif self.state == "settings":
            self.draw_settings()
        elif self.state == "high_scores":
            self.draw_high_scores()

        pygame.display.flip()

    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title = self.big_font.render("SNAKE GAME", True, GREEN)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        for i, option in enumerate(self.menu_options):
            color = GREEN if i == self.menu_selected else WHITE
            text = self.font.render(option, True, color)
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50)))

        hint = self.font.render("Use UP/DOWN arrows and ENTER to select", True, GRAY)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 50)))

    def draw_game(self):
        self.screen.fill(BLACK)
        self.draw_grid()

        # Get snake colors from selected theme
        snake_color, head_color = self.get_snake_colors()

        # Draw obstacles
        for obstacle in self.obstacles:
            self.draw_cell(obstacle, GRAY)

        # Draw snake (head in a different color)
        for i, segment in enumerate(self.snake):
            color = head_color if i == 0 else snake_color
            self.draw_cell(segment, color)

        # Draw food
        self.draw_cell(self.food, RED)

        # Draw power-up
        if self.power_up:
            if self.power_up_type == 'golden':
                self.draw_cell(self.power_up, GOLD)
            elif self.power_up_type == 'blue':
                self.draw_cell(self.power_up, BLUE)
            elif self.power_up_type == 'purple':
                self.draw_cell(self.power_up, PURPLE)

        # Show score
        score_text = self.font.render(
            f"Score: {self.score}   Length: {len(self.snake)}   Best: {self.high_score}",
            True, WHITE
        )
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            over_text = self.big_font.render("Game Over!", True, RED)
            info_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to restart", True, GRAY)
            menu_text = self.font.render("Press ESC for menu", True, GRAY)

            self.screen.blit(over_text, over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
            self.screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))
            self.screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))
            self.screen.blit(menu_text, menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.big_font.render("PAUSED", True, CYAN)
        resume_text = self.font.render("Press SPACE/P to resume", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, GRAY)
        menu_text = self.font.render("Press Q for menu", True, GRAY)

        self.screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
        self.screen.blit(resume_text, resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))
        self.screen.blit(menu_text, menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))

    def draw_settings(self):
        self.screen.fill(BLACK)
        
        title = self.big_font.render("SETTINGS", True, GREEN)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 6)))

        for i, option in enumerate(self.settings_options):
            color = GREEN if i == self.settings_selected else WHITE
            option_text = self.font.render(option, True, color)
            self.screen.blit(option_text, option_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 60)))
            
            # Show current value for each setting
            if option == "Difficulty":
                value = self.difficulty_options[self.difficulty_selected]
                value_text = self.font.render(f"< {value} >", True, CYAN)
                self.screen.blit(value_text, value_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 60 + 30)))
            elif option == "Snake Color":
                value = self.color_themes[self.color_selected]
                value_text = self.font.render(f"< {value} >", True, CYAN)
                self.screen.blit(value_text, value_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 60 + 30)))
            elif option == "Wrap-Around":
                value = "ON" if self.wrap_around else "OFF"
                value_text = self.font.render(f"< {value} >", True, CYAN)
                self.screen.blit(value_text, value_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 60 + 30)))
            elif option == "Game Mode":
                value = self.game_modes[self.game_mode_selected]
                value_text = self.font.render(f"< {value} >", True, CYAN)
                self.screen.blit(value_text, value_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 60 + 30)))

        hint = self.font.render("Use UP/DOWN to select, LEFT/RIGHT to change, ENTER/ESC to save", True, GRAY)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 50)))

    def draw_high_scores(self):
        self.screen.fill(BLACK)
        
        title = self.big_font.render("HIGH SCORES & STATS", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))

        # Statistics
        stats_y = 120
        games_text = self.font.render(f"Games Played: {self.stats['games_played']}", True, WHITE)
        total_text = self.font.render(f"Total Score: {self.stats['total_score']}", True, WHITE)
        avg_text = self.font.render(f"Avg Score: {self.stats['total_score'] // max(1, self.stats['games_played'])}", True, WHITE)
        time_text = self.font.render(f"Best Time: {self.stats['best_time']:.1f}s", True, WHITE)
        
        self.screen.blit(games_text, games_text.get_rect(center=(WIDTH // 2, stats_y)))
        self.screen.blit(total_text, total_text.get_rect(center=(WIDTH // 2, stats_y + 30)))
        self.screen.blit(avg_text, avg_text.get_rect(center=(WIDTH // 2, stats_y + 60)))
        self.screen.blit(time_text, time_text.get_rect(center=(WIDTH // 2, stats_y + 90)))

        # Leaderboard
        leaderboard_title = self.font.render("TOP 10 SCORES", True, CYAN)
        self.screen.blit(leaderboard_title, leaderboard_title.get_rect(center=(WIDTH // 2, stats_y + 140)))

        for i, entry in enumerate(self.stats['leaderboard']):
            if i >= 10:
                break
            entry_text = self.font.render(
                f"{i+1}. {entry['score']} - {entry['date']} ({entry['mode']})",
                True, WHITE
            )
            self.screen.blit(entry_text, entry_text.get_rect(center=(WIDTH // 2, stats_y + 170 + i * 25)))

        hint = self.font.render("Press ESC to return", True, GRAY)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.fps)


def main():
    """Entry point for the game when installed as a package."""
    game = SnakeGame()
    game.run()

if __name__ == "__main__":
    main()