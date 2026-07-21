import sys
import random
import pygame

from .config import (
    CELL_SIZE, FPS, HUD_HEIGHT,
    COLOR_BG, COLOR_WALL, COLOR_WALL_EDGE, COLOR_PATH,
    COLOR_PLAYER, COLOR_PLAYER_GLOW, COLOR_GOAL,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_ACCENT,
    COLOR_BG_DARK, COLOR_WALL_DARK, COLOR_WALL_EDGE_DARK, COLOR_PATH_DARK,
    COLOR_PLAYER_DARK, COLOR_PLAYER_GLOW_DARK, COLOR_GOAL_DARK,
    COLOR_TEXT_DARK, COLOR_TEXT_DIM_DARK, COLOR_ACCENT_DARK,
    COLOR_BG_LIGHT, COLOR_WALL_LIGHT, COLOR_WALL_EDGE_LIGHT, COLOR_PATH_LIGHT,
    COLOR_PLAYER_LIGHT, COLOR_PLAYER_GLOW_LIGHT, COLOR_GOAL_LIGHT,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DIM_LIGHT, COLOR_ACCENT_LIGHT,
    STATE_MENU, STATE_PLAYING, STATE_WIN,
)
from .maze import generate_solvable_maze
from .audio import SoundManager
from .save_manager import SaveManager
from .localization import get_text


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
        
        # Set HUD height first
        self.hud_height = HUD_HEIGHT
        
        # Get screen info for responsive sizing
        self.screen_info = pygame.display.Info()
        self.max_screen_width = self.screen_info.current_w - 100
        self.max_screen_height = self.screen_info.current_h - 100
        
        # Calculate initial window size based on current level and screen
        base_size = 15
        size_increase = (self.level_num - 1) * 2
        maze_size = base_size + size_increase
        
        # Calculate responsive cell size
        max_maze_pixels = min(self.max_screen_width, self.max_screen_height - self.hud_height)
        self.cell_size = max(20, min(40, max_maze_pixels // maze_size))
        
        self.width = maze_size * self.cell_size
        self.height = maze_size * self.cell_size + self.hud_height

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Maze Runner")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("arial", 42, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("arial", 18)
        
        # Try to load Persian-compatible font with RTL support
        self.persian_font = None
        possible_fonts = ["Tahoma", "Arial", "Segoe UI", "Microsoft Sans Serif", "DejaVu Sans"]
        for font_name in possible_fonts:
            try:
                self.persian_font = pygame.font.SysFont(font_name, 24)
                break
            except:
                continue
        
        # Mouse movement variables
        self.mouse_target = None
        self.mouse_speed = 3
        
        # Menu system
        self.menu_state = "main"  # main, settings, about
        self.menu_buttons = []
        self.selected_button = 0
        self.hovered_button = -1

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
        
        # Smooth movement variables
        self.player_pixel_pos = [self.cell_size // 2, self.cell_size // 2]
        self.player_velocity = [0, 0]
        self.move_speed = 4  # pixels per frame
        
        # Theme and language settings
        self.dark_mode = True
        self.language = "en"  # "en" or "fa"
        
        # Load theme/language from save
        settings = self.save_manager.load_settings()
        if settings:
            self.dark_mode = settings.get("dark_mode", True)
            self.language = settings.get("language", "en")
        
        self.apply_theme()

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
        
        # Resize window to fit current maze with responsive sizing
        maze_size = len(self.grid)
        max_maze_pixels = min(self.max_screen_width, self.max_screen_height - self.hud_height)
        self.cell_size = max(20, min(40, max_maze_pixels // maze_size))
        
        self.width = maze_size * self.cell_size
        self.height = maze_size * self.cell_size + self.hud_height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        
        # Reset player pixel position to center of starting cell
        self.player_pixel_pos = [
            self.player[0] * self.cell_size + self.cell_size // 2,
            self.player[1] * self.cell_size + self.cell_size // 2
        ]
        self.player_velocity = [0, 0]

        self.start_ticks = pygame.time.get_ticks()
        self.state = STATE_PLAYING

    def apply_theme(self):
        """Apply current theme colors"""
        global COLOR_BG, COLOR_WALL, COLOR_WALL_EDGE, COLOR_PATH
        global COLOR_PLAYER, COLOR_PLAYER_GLOW, COLOR_GOAL
        global COLOR_TEXT, COLOR_TEXT_DIM, COLOR_ACCENT
        
        if self.dark_mode:
            COLOR_BG = COLOR_BG_DARK
            COLOR_WALL = COLOR_WALL_DARK
            COLOR_WALL_EDGE = COLOR_WALL_EDGE_DARK
            COLOR_PATH = COLOR_PATH_DARK
            COLOR_PLAYER = COLOR_PLAYER_DARK
            COLOR_PLAYER_GLOW = COLOR_PLAYER_GLOW_DARK
            COLOR_GOAL = COLOR_GOAL_DARK
            COLOR_TEXT = COLOR_TEXT_DARK
            COLOR_TEXT_DIM = COLOR_TEXT_DIM_DARK
            COLOR_ACCENT = COLOR_ACCENT_DARK
        else:
            COLOR_BG = COLOR_BG_LIGHT
            COLOR_WALL = COLOR_WALL_LIGHT
            COLOR_WALL_EDGE = COLOR_WALL_EDGE_LIGHT
            COLOR_PATH = COLOR_PATH_LIGHT
            COLOR_PLAYER = COLOR_PLAYER_LIGHT
            COLOR_PLAYER_GLOW = COLOR_PLAYER_GLOW_LIGHT
            COLOR_GOAL = COLOR_GOAL_LIGHT
            COLOR_TEXT = COLOR_TEXT_LIGHT
            COLOR_TEXT_DIM = COLOR_TEXT_DIM_LIGHT
            COLOR_ACCENT = COLOR_ACCENT_LIGHT
    
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.save_manager.save_settings(self.dark_mode, self.language)
    
    def toggle_language(self):
        """Toggle between English and Persian"""
        self.language = "fa" if self.language == "en" else "en"
        self.save_manager.save_settings(self.dark_mode, self.language)
    
    def t(self, key):
        """Get translated text"""
        text = get_text(key, self.language)
        # Handle RTL for Persian text
        if self.language == "fa":
            text = self.rtl_text(text)
        return text
    
    def rtl_text(self, text):
        """Reverse text for RTL languages like Persian"""
        # Simple reversal - for proper RTL, you'd need a library like arabic-reshaper
        # This is a basic implementation for Pygame
        return text[::-1]
    
    def try_move(self, dx, dy):
        # Set velocity based on input
        self.player_velocity = [dx * self.move_speed, dy * self.move_speed]
    
    def update_player_position(self):
        if self.state != STATE_PLAYING:
            return
        
        # Handle mouse movement
        if self.mouse_target:
            target_x, target_y = self.mouse_target
            dx = target_x - self.player_pixel_pos[0]
            dy = target_y - self.player_pixel_pos[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance > self.mouse_speed:
                # Move towards target
                self.player_velocity = [
                    (dx / distance) * self.mouse_speed,
                    (dy / distance) * self.mouse_speed
                ]
            else:
                # Reached target
                self.player_pixel_pos = [target_x, target_y]
                self.player_velocity = [0, 0]
                self.mouse_target = None
        
        # Calculate new position
        new_x = self.player_pixel_pos[0] + self.player_velocity[0]
        new_y = self.player_pixel_pos[1] + self.player_velocity[1]
        
        # Collision detection with walls
        player_radius = self.cell_size // 2 - 3
        
        # Check horizontal movement
        if self.player_velocity[0] != 0:
            # Check left and right edges of player
            left_edge = new_x - player_radius
            right_edge = new_x + player_radius
            
            # Convert to grid coordinates
            left_cell = int(left_edge // self.cell_size)
            right_cell = int(right_edge // self.cell_size)
            current_cell_y = int(self.player_pixel_pos[1] // self.cell_size)
            
            can_move = True
            if left_cell >= 0 and self.grid[current_cell_y][left_cell] == 1:
                can_move = False
                new_x = (left_cell + 1) * self.cell_size + player_radius
            if right_cell < len(self.grid[0]) and self.grid[current_cell_y][right_cell] == 1:
                can_move = False
                new_x = right_cell * self.cell_size - player_radius - 1
            
            if can_move:
                self.player_pixel_pos[0] = new_x
            else:
                self.player_pixel_pos[0] = new_x
        
        # Check vertical movement
        if self.player_velocity[1] != 0:
            top_edge = new_y - player_radius
            bottom_edge = new_y + player_radius
            
            top_cell = int(top_edge // self.cell_size)
            bottom_cell = int(bottom_edge // self.cell_size)
            current_cell_x = int(self.player_pixel_pos[0] // self.cell_size)
            
            can_move = True
            if top_cell >= 0 and self.grid[top_cell][current_cell_x] == 1:
                can_move = False
                new_y = (top_cell + 1) * self.cell_size + player_radius
            if bottom_cell < len(self.grid) and self.grid[bottom_cell][current_cell_x] == 1:
                can_move = False
                new_y = bottom_cell * self.cell_size - player_radius - 1
            
            if can_move:
                self.player_pixel_pos[1] = new_y
            else:
                self.player_pixel_pos[1] = new_y
        
        # Update grid position for game logic
        self.player = (
            int(self.player_pixel_pos[0] // self.cell_size),
            int(self.player_pixel_pos[1] // self.cell_size)
        )
        
        # Check if reached goal
        if self.player == self.goal:
            self.on_win()
        
        # Add trail occasionally
        if int(self.anim_t) % 10 == 0:
            self.trail.append((self.player[0], self.player[1], 1.0))

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
        
        # Update smooth player movement
        self.update_player_position()
        
        # Count moves based on position changes
        if int(self.anim_t) % 30 == 0 and (self.player_velocity[0] != 0 or self.player_velocity[1] != 0):
            self.move_count += 1
            self.sound.play("move")

        self.trail = [(x, y, a - 0.03) for (x, y, a) in self.trail if a - 0.03 > 0]

    def draw_maze(self):
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                rect = pygame.Rect(x * self.cell_size, self.hud_height + y * self.cell_size,
                                    self.cell_size, self.cell_size)
                if val == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                    # Smooth anti-aliased edges
                    pygame.draw.rect(self.screen, COLOR_WALL_EDGE, rect, 1, border_radius=1)
                else:
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)

        for (x, y, a) in self.trail:
            cx = x * self.cell_size + self.cell_size // 2
            cy = self.hud_height + y * self.cell_size + self.cell_size // 2
            radius = int(self.cell_size * 0.15 * a) + 1
            # Anti-aliased circles
            surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*COLOR_PLAYER, int(120 * a)),
                                (self.cell_size // 2, self.cell_size // 2), radius)
            self.screen.blit(surf, (cx - self.cell_size // 2, cy - self.cell_size // 2))

        # Goal is hidden - no visual indicator
        # Player must find the exit by exploring

        px, py = self.player_pixel_pos
        pcx = px
        pcy = self.hud_height + py
        glow_r = self.cell_size // 2 + 4 + int(2 * abs((self.anim_t % 40) - 20) / 20)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        # Anti-aliased glow
        pygame.draw.circle(glow_surf, (*COLOR_PLAYER_GLOW, 70), (glow_r, glow_r), glow_r)
        self.screen.blit(glow_surf, (pcx - glow_r, pcy - glow_r))
        pygame.draw.circle(self.screen, COLOR_PLAYER, (pcx, pcy), self.cell_size // 2 - 3)

    def draw_hud(self):
        # Smooth gradient background for HUD
        hud_color = (12, 12, 18) if self.dark_mode else (230, 230, 240)
        pygame.draw.rect(self.screen, hud_color, (0, 0, self.width, self.hud_height), border_radius=0)
        # Anti-aliased divider line
        pygame.draw.aaline(self.screen, COLOR_ACCENT, (0, self.hud_height), (self.width, self.hud_height))
        pygame.draw.line(self.screen, COLOR_ACCENT, (0, self.hud_height), (self.width, self.hud_height), 2)

        font = self.persian_font if self.language == "fa" else self.font_medium
        level_txt = font.render(f"{self.t('level')} {self.level_num}", True, COLOR_TEXT)
        self.screen.blit(level_txt, (16, 16))

        font_small = self.persian_font if self.language == "fa" else self.font_small
        moves_txt = font_small.render(f"{self.t('moves')}: {self.move_count}", True, COLOR_TEXT_DIM)
        self.screen.blit(moves_txt, (200, 20))

        time_txt = font_small.render(f"{self.t('time')}: {self.elapsed:0.1f}s", True, COLOR_TEXT_DIM)
        self.screen.blit(time_txt, (self.width - 160, 20))
        
        best_time = self.best_times.get(self.level_num)
        best_str = f"{best_time:0.1f}s" if best_time is not None else "--"
        best_txt = font_small.render(f"{self.t('best')}: {best_str}", True, COLOR_TEXT_DIM)
        self.screen.blit(best_txt, (self.width - 160, 40))
        
        leaderboard = self.save_manager.load_leaderboard()
        if leaderboard:
            rank_txt = font_small.render(f"{self.t('rank')}: {self.get_player_rank(leaderboard)}", True, COLOR_TEXT_DIM)
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

    def handle_menu_action(self, action):
        """Handle menu button actions"""
        if action == "play":
            # Load from saved level or start fresh
            saved_data = self.save_manager.load_progress()
            self.level_num = saved_data["current_level"]
            self.best_times = saved_data["best_times"]
            self.total_play_time = saved_data["total_play_time"]
            self.load_level(self.level_num)
            self.menu_buttons = []  # Clear buttons for next menu
        elif action == "theme":
            self.toggle_theme()
            self.menu_buttons = []  # Recreate buttons with updated text
        elif action == "lang":
            self.toggle_language()
            self.menu_buttons = []  # Recreate buttons with updated text
        elif action == "clear":
            # Clear progress and restart
            self.save_manager.clear_progress()
            self.level_num = 1
            self.best_times = {}
            self.total_play_time = 0
            self.menu_buttons = []
        elif action == "quit":
            pygame.quit()
            sys.exit()
        elif action == "back":
            self.menu_state = "main"
            self.selected_button = 0
            self.menu_buttons = []
    
    def create_menu_buttons(self):
        """Create button definitions for current menu state"""
        self.menu_buttons = []
        button_width = 280
        button_height = 50
        center_x = self.width // 2
        start_y = 180
        spacing = 60
        
        if self.menu_state == "main":
            buttons = [
                {"text": self.t("press_enter"), "action": "play", "icon": "▶"},
                {"text": self.t("toggle_theme"), "action": "theme", "icon": "◐"},
                {"text": self.t("toggle_lang"), "action": "lang", "icon": "🌐"},
                {"text": self.t("press_clear"), "action": "clear", "icon": "✖"},
                {"text": self.t("press_quit"), "action": "quit", "icon": "✕"},
            ]
        elif self.menu_state == "settings":
            buttons = [
                {"text": self.t("toggle_theme"), "action": "theme", "icon": "◐"},
                {"text": self.t("toggle_lang"), "action": "lang", "icon": "🌐"},
                {"text": "Back", "action": "back", "icon": "◀"},
            ]
        elif self.menu_state == "about":
            buttons = [
                {"text": "Back", "action": "back", "icon": "◀"},
            ]
        
        for i, btn in enumerate(buttons):
            rect = pygame.Rect(
                center_x - button_width // 2,
                start_y + i * spacing,
                button_width,
                button_height
            )
            self.menu_buttons.append({
                "rect": rect,
                "text": btn["text"],
                "action": btn["action"],
                "icon": btn["icon"],
                "index": i
            })
    
    def draw_button(self, button, is_hovered, is_selected):
        """Draw a single menu button with effects"""
        rect = button["rect"]
        
        # Determine colors based on state
        if is_selected:
            bg_color = COLOR_ACCENT
            text_color = (255, 255, 255)
            glow_intensity = 15
        elif is_hovered:
            bg_color = tuple(min(c + 30, 255) for c in COLOR_WALL)
            text_color = COLOR_TEXT
            glow_intensity = 8
        else:
            bg_color = COLOR_WALL
            text_color = COLOR_TEXT_DIM
            glow_intensity = 0
        
        # Draw button background with rounded corners
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=12)
        
        # Draw glow effect if selected or hovered
        if glow_intensity > 0:
            glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*COLOR_ACCENT, glow_intensity), 
                           (10, 10, rect.width, rect.height), border_radius=15)
            self.screen.blit(glow_surf, (rect.x - 10, rect.y - 10))
        
        # Draw border
        border_color = COLOR_ACCENT if is_selected else COLOR_WALL_EDGE
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=12)
        
        # Draw icon
        font = self.persian_font if self.language == "fa" else self.font_medium
        icon_surf = font.render(button["icon"], True, text_color)
        icon_x = rect.x + 20
        icon_y = rect.centery - icon_surf.get_height() // 2
        self.screen.blit(icon_surf, (icon_x, icon_y))
        
        # Draw text
        text_surf = font.render(button["text"], True, text_color)
        text_x = rect.centerx - text_surf.get_width() // 2
        text_y = rect.centery - text_surf.get_height() // 2
        self.screen.blit(text_surf, (text_x, text_y))
    
    def draw_menu(self):
        self.screen.fill(COLOR_BG)
        
        # Create buttons if not exists or window resized
        if not self.menu_buttons:
            self.create_menu_buttons()
        
        # Draw title with glow effect
        title = self.font_big.render(self.t("title"), True, COLOR_ACCENT)
        title_x = self.width // 2 - title.get_width() // 2
        title_y = 60
        
        # Title glow
        glow_surf = pygame.Surface((title.get_width() + 40, title.get_height() + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*COLOR_ACCENT, 20), (20, 20, title.get_width(), title.get_height()), border_radius=20)
        self.screen.blit(glow_surf, (title_x - 20, title_y - 20))
        
        self.screen.blit(title, (title_x, title_y))
        
        # Draw stats section
        stats_bg = pygame.Rect(self.width // 2 - 150, 120, 300, 40)
        pygame.draw.rect(self.screen, COLOR_WALL, stats_bg, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_WALL_EDGE, stats_bg, 1, border_radius=10)
        
        stats_text = f"{self.t('level')} {self.level_num} | {self.t('levels_completed')}: {len([t for t in self.best_times.values() if t > 0])}"
        font_small = self.persian_font if self.language == "fa" else self.font_small
        stats_surf = font_small.render(stats_text, True, COLOR_TEXT)
        self.screen.blit(stats_surf, (stats_bg.centerx - stats_surf.get_width() // 2, stats_bg.centery - stats_surf.get_height() // 2))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_button = -1
        
        for i, button in enumerate(self.menu_buttons):
            is_hovered = button["rect"].collidepoint(mouse_pos)
            is_selected = (i == self.selected_button)
            
            if is_hovered:
                self.hovered_button = i
            
            self.draw_button(button, is_hovered, is_selected)
        
        # Draw instructions at bottom
        instructions = self.t("menu_move") + " | " + self.t("menu_find_exit")
        inst_surf = font_small.render(instructions, True, COLOR_TEXT_DIM)
        self.screen.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, self.height - 40))

    def draw(self):
        if self.state == STATE_MENU:
            self.draw_menu()
            pygame.display.flip()
            return

        self.screen.fill(COLOR_BG)
        self.draw_maze()
        self.draw_hud()

        if self.state == STATE_WIN:
            font = self.persian_font if self.language == "fa" else self.font_big
            title_surf = font.render(f"{self.t('level_complete')} Time: {self.elapsed:.1f}s", True, COLOR_GOAL)
            self.screen.blit(title_surf,
                          (self.width // 2 - title_surf.get_width() // 2, self.height // 2 - 60))
            
            font_sub = self.persian_font if self.language == "fa" else self.font_medium
            sub_surf = font_sub.render(self.t("next_replay_menu"), True, COLOR_TEXT_DIM)
            self.screen.blit(sub_surf,
                          (self.width // 2 - sub_surf.get_width() // 2, self.height // 2))
        
        # Draw quit button in corner
        font_small = self.persian_font if self.language == "fa" else self.font_small
        quit_btn = font_small.render(self.t("quit_menu"), True, COLOR_TEXT_DIM)
        self.screen.blit(quit_btn, (10, self.height - 30))

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
                        # Keyboard navigation
                        if event.key == pygame.K_UP:
                            self.selected_button = (self.selected_button - 1) % len(self.menu_buttons)
                        elif event.key == pygame.K_DOWN:
                            self.selected_button = (self.selected_button + 1) % len(self.menu_buttons)
                        elif event.key == pygame.K_RETURN:
                            if self.menu_buttons:
                                self.handle_menu_action(self.menu_buttons[self.selected_button]["action"])
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.state == STATE_MENU:
                            mouse_pos = pygame.mouse.get_pos()
                            for button in self.menu_buttons:
                                if button["rect"].collidepoint(mouse_pos):
                                    self.handle_menu_action(button["action"])
                                    self.selected_button = button["index"]
                                    break

                    elif self.state == STATE_PLAYING:
                        if event.key == pygame.K_q:
                            self.state = STATE_MENU
                        else:
                            keys = pygame.key.get_pressed()
                            dx, dy = 0, 0
                            if keys[pygame.K_UP] or keys[pygame.K_w]:
                                dy = -1
                            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                                dy = 1
                            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                                dx = -1
                            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                                dx = 1
                            self.try_move(dx, dy)

                    elif self.state == STATE_WIN:
                        if event.key == pygame.K_RETURN:
                            self.load_level(self.level_num + 1)
                        elif event.key == pygame.K_r:
                            self.load_level(self.level_num)
                        elif event.key == pygame.K_q:
                            self.state = STATE_MENU
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.state == STATE_MENU:
                            mouse_pos = pygame.mouse.get_pos()
                            for button in self.menu_buttons:
                                if button["rect"].collidepoint(mouse_pos):
                                    self.handle_menu_action(button["action"])
                                    self.selected_button = button["index"]
                                    break
                        elif self.state == STATE_PLAYING:
                            # Handle mouse click for movement
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            # Convert to game coordinates (minus HUD)
                            game_y = mouse_y - self.hud_height
                            if game_y > 0:
                                self.mouse_target = (mouse_x, game_y)
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize
                    self.width, self.height = event.w, event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE | pygame.DOUBLEBUF)
                    self.menu_buttons = []  # Recreate buttons on resize


            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
