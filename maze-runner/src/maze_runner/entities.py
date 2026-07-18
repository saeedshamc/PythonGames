from .maze import bfs_path


class Enemy:
    def __init__(self, x, y, speed_ms):
        self.x = x
        self.y = y
        self.speed_ms = speed_ms
        self.last_move_time = 0
        self.pulse = 0.0

    def update(self, now, grid, player_pos, sound):
        self.pulse += 0.15
        if now - self.last_move_time < self.speed_ms:
            return
        self.last_move_time = now

        path = bfs_path(grid, (self.x, self.y), player_pos)
        if len(path) > 1:
            self.x, self.y = path[1]
            sound.play("step_enemy")
