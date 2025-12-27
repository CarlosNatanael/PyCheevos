from typing import List, Optional
from .achievement import Achievement
from .leaderboard import Leaderboard
from .rich_presence import RichPresence

class AchievementSet:
    def __init__(self, game_id: int, title: str):
        self.game_id = game_id
        self.title = title
        self.achievements: List[Achievement] = []
        self.leaderboards: List[Leaderboard] = []
        self.rich_presence: RichPresence = None #type: ignore

    def add_achievement(self, achievement: Achievement):
        self.achievements.append(achievement)
        return self
    
    def add_leaderboard(self, leaderboard: Leaderboard):
        self.leaderboards.append(leaderboard)
        return self
    
    def add_rich_presence(self, rp: RichPresence):
        self.rich_presence = rp
        return self

    def save(self, path: Optional[str] = None):
        """Gera o ficheiro User.txt para o emulador"""
        filename = path if path else f"{self.game_id}-User.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("1.0\n")
            f.write(f"{self.title}\n")
            for ach in self.achievements:
                f.write(ach.render() + "\n")
            for lb in self.leaderboards:
                f.write(lb.render() + "\n")
        print(f"Arquivo gerado: {filename}")

        if self.rich_presence:
            filename_rp = f"{self.game_id}-Rich.txt"
            with open(filename_rp, "w", encoding="utf-88") as f:
                f.write(self.rich_presence.render())
            print(f"Arquivo Rich Presence gerado: {filename_rp}")