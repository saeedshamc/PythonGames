import random
from collections import deque


def generate_maze(width, height):
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    grid = [[1 for _ in range(width)] for _ in range(height)]

    def neighbors(cx, cy):
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        result = []
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and grid[ny][nx] == 1:
                result.append((nx, ny, dx, dy))
        return result

    start_x, start_y = 1, 1
    grid[start_y][start_x] = 0
    stack = [(start_x, start_y)]

    while stack:
        cx, cy = stack[-1]
        options = neighbors(cx, cy)
        if options:
            nx, ny, dx, dy = options[0]
            grid[cy + dy // 2][cx + dx // 2] = 0
            grid[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()

    return grid


def bfs_path(grid, start, goal):
    height = len(grid)
    width = len(grid[0])

    if start == goal:
        return [start]

    visited = {start}
    queue = deque([start])
    came_from = {}

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                came_from[(nx, ny)] = (cx, cy)
                if (nx, ny) == goal:
                    path = [(nx, ny)]
                    cur = (cx, cy)
                    while cur != start:
                        path.append(cur)
                        cur = came_from[cur]
                    path.append(start)
                    path.reverse()
                    return path
                queue.append((nx, ny))

    return []


def generate_solvable_maze(width, height):
    grid = generate_maze(width, height)
    h = len(grid)
    w = len(grid[0])

    start = (1, 1)
    goal = (w - 2, h - 2)

    path = bfs_path(grid, start, goal)
    attempts = 0
    while not path and attempts < 5:
        grid = generate_maze(width, height)
        path = bfs_path(grid, start, goal)
        attempts += 1

    return grid, start, goal
