from typing import List, Optional, Union
from pathlib import Path
from .achievement import Achievement
from .leaderboard import Leaderboard
from .rich_presence import RichPresence

class AchievementSet:
    def __init__(self, game_id: int, title: str):
        self.game_id = game_id
        self.title = title
        self.achievements: List[Achievement] = []
        self.leaderboards: List[Leaderboard] = []
        self.rich_presence: Optional[RichPresence] = None

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
        """
        Gera os arquivos User.txt e Rich.txt.
        Se path não for informado, salva em: /output/Titulo - ID/
        """
        if path is None:
            root = Path(__file__).resolve().parent.parent
            output = root / "output" / f"{self.title} - {self.game_id}"
        else:
            output = Path(path)

        output.mkdir(parents=True, exist_ok=True)
        
        user_file = output / f"{self.game_id}-User.txt"
        
        with open(user_file, "w", encoding="utf-8") as f:
            f.write("1.0\n")
            f.write(f"{self.title}\n")
            for ach in self.achievements:
                f.write(ach.render() + "\n")
            for lb in self.leaderboards:
                f.write(lb.render() + "\n")
        
        print(f"Generated User file: {user_file}")

        if self.rich_presence:
            rp_file = output / f"{self.game_id}-Rich.txt"
            with open(rp_file, "w", encoding="utf-8") as f:
                f.write(self.rich_presence.render())
            
            print(f"Generated Rich Presence file: {rp_file}")