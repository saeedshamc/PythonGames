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
    
    # Add some extra passages to reduce dead ends and make maze more interesting
    # This creates loops and alternative paths
    extra_passages = (width * height) // 50  # Add about 2% extra passages
    for _ in range(extra_passages):
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if grid[y][x] == 1:
            # Check if removing this wall would connect two open cells
            open_neighbors = 0
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == 0:
                    open_neighbors += 1
            if open_neighbors >= 2:  # Only remove if it connects paths
                grid[y][x] = 0

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
    
    # Random exit on outer walls (not corners)
    possible_exits = []
    
    # Top and bottom walls (excluding corners)
    for x in range(2, w - 2):
        if grid[1][x] == 0:  # Top wall
            possible_exits.append((x, 0))
        if grid[h - 2][x] == 0:  # Bottom wall
            possible_exits.append((x, h - 1))
    
    # Left and right walls (excluding corners)
    for y in range(2, h - 2):
        if grid[y][1] == 0:  # Left wall
            possible_exits.append((0, y))
        if grid[y][w - 2] == 0:  # Right wall
            possible_exits.append((w - 1, y))
    
    # If no exits found, create one by breaking a random wall
    if not possible_exits:
        # Pick a random edge cell and make it an exit
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            x = random.randint(2, w - 2)
            goal = (x, 0)
            grid[0][x] = 0
        elif edge == 'bottom':
            x = random.randint(2, w - 2)
            goal = (x, h - 1)
            grid[h - 1][x] = 0
        elif edge == 'left':
            y = random.randint(2, h - 2)
            goal = (0, y)
            grid[y][0] = 0
        else:  # right
            y = random.randint(2, h - 2)
            goal = (w - 1, y)
            grid[y][w - 1] = 0
    else:
        goal = random.choice(possible_exits)
        # Ensure the goal cell is open
        grid[goal[1]][goal[0]] = 0

    path = bfs_path(grid, start, goal)
    attempts = 0
    while not path and attempts < 10:
        grid = generate_maze(width, height)
        # Recreate exit
        possible_exits = []
        for x in range(2, w - 2):
            if grid[1][x] == 0:
                possible_exits.append((x, 0))
            if grid[h - 2][x] == 0:
                possible_exits.append((x, h - 1))
        for y in range(2, h - 2):
            if grid[y][1] == 0:
                possible_exits.append((0, y))
            if grid[y][w - 2] == 0:
                possible_exits.append((w - 1, y))
        
        if possible_exits:
            goal = random.choice(possible_exits)
            grid[goal[1]][goal[0]] = 0
        else:
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            if edge == 'top':
                x = random.randint(2, w - 2)
                goal = (x, 0)
                grid[0][x] = 0
            elif edge == 'bottom':
                x = random.randint(2, w - 2)
                goal = (x, h - 1)
                grid[h - 1][x] = 0
            elif edge == 'left':
                y = random.randint(2, h - 2)
                goal = (0, y)
                grid[y][0] = 0
            else:
                y = random.randint(2, h - 2)
                goal = (w - 1, y)
                grid[y][w - 1] = 0
        
        path = bfs_path(grid, start, goal)
        attempts += 1

    return grid, start, goal
