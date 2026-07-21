import json
import os
from pathlib import Path
from datetime import datetime


class SaveManager:
    def __init__(self):
        self.save_dir = Path.home() / ".maze_runner"
        self.save_file = self.save_dir / "progress.json"
        self.leaderboard_file = self.save_dir / "leaderboard.json"
        self.levels_dir = self.save_dir / "levels"
        self.levels_dir.mkdir(exist_ok=True)
        self.save_dir.mkdir(exist_ok=True)
    
    def save_progress(self, current_level, best_times, total_play_time):
        data = {
            "current_level": current_level,
            "best_times": best_times,
            "total_play_time": total_play_time
        }
        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_progress(self):
        if not self.save_file.exists():
            return {
                "current_level": 1,
                "best_times": {},
                "total_play_time": 0
            }
        
        try:
            with open(self.save_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {
                "current_level": 1,
                "best_times": {},
                "total_play_time": 0
            }
    
    def clear_progress(self):
        if self.save_file.exists():
            self.save_file.unlink()
    
    def save_leaderboard(self, leaderboard):
        with open(self.leaderboard_file, 'w') as f:
            json.dump(leaderboard, f, indent=2)
    
    def load_leaderboard(self):
        if not self.leaderboard_file.exists():
            return []
        
        try:
            with open(self.leaderboard_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def add_to_leaderboard(self, level, time):
        leaderboard = self.load_leaderboard()
        entry = {
            "level": level,
            "time": time,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        leaderboard.append(entry)
        # Sort by level (descending), then by time (ascending)
        leaderboard.sort(key=lambda x: (-x["level"], x["time"]))
        # Keep only top 20
        leaderboard = leaderboard[:20]
        self.save_leaderboard(leaderboard)
        return leaderboard
    
    def save_level_map(self, level_num, grid, start, goal):
        level_file = self.levels_dir / f"level_{level_num}.json"
        data = {
            "level": level_num,
            "grid": grid,
            "player": list(start),
            "goal": list(goal)
        }
        with open(level_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_level_map(self, level_num):
        level_file = self.levels_dir / f"level_{level_num}.json"
        if not level_file.exists():
            return None
        
        try:
            with open(level_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def get_all_saved_levels(self):
        levels = []
        for file in self.levels_dir.glob("level_*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    levels.append(data)
            except (json.JSONDecodeError, IOError):
                continue
        return sorted(levels, key=lambda x: x["level"])
