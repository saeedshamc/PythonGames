import pygame
import random
import sys

# ---------- Settings ----------
CELL_SIZE = 15
GRID_WIDTH = 70
GRID_HEIGHT = 46
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS_START = 10          # starting game speed
FPS_INCREASE_EVERY = 5  # every N points, speed up a bit
MAX_FPS = 25             # cap so it doesn't get impossibly fast

# Colors
BLACK = (15, 15, 15)
GREEN = (50, 205, 50)
DARK_GREEN = (30, 140, 30)
RED = (220, 50, 50)
WHITE = (240, 240, 240)
GRAY = (60, 60, 60)
GRID_LINE = (35, 35, 35)


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 48, bold=True)
        self.high_score = 0
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
        self.fps = FPS_START

    def spawn_food(self):
        """Places food on a random empty cell."""
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                return pos

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and self.direction != (0, 1):
                    self.next_direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction != (0, -1):
                    self.next_direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction != (1, 0):
                    self.next_direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction != (-1, 0):
                    self.next_direction = (1, 0)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def update(self):
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        # Wrap around: going off one edge brings you back in on the opposite side
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)

        # Colliding with itself -> game over
        if new_head in self.snake:
            self.game_over = True
            self.high_score = max(self.high_score, self.score)
            return

        self.snake.insert(0, new_head)

        # Eating food -> grow and score
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
            # Speed up a little every few points (more challenge as the snake grows)
            if self.score % (FPS_INCREASE_EVERY * 10) == 0 and self.fps < MAX_FPS:
                self.fps += 1
        else:
            # No food eaten, remove the tail so length stays the same
            self.snake.pop()

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
        self.screen.fill(BLACK)
        self.draw_grid()

        # Draw snake (head in a different color)
        for i, segment in enumerate(self.snake):
            color = DARK_GREEN if i == 0 else GREEN
            self.draw_cell(segment, color)

        # Draw food
        self.draw_cell(self.food, RED)

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

            self.screen.blit(over_text, over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            self.screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
            self.screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    game = SnakeGame()
    game.run()