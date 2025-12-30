from typing import List, Optional
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
        self.next_free_id = 111001

    def add_achievement(self, achievement: Achievement):
        if achievement.id == 0:
            achievement.id = self.next_free_id
            self.next_free_id += 1
        else:
            if achievement.id >= self.next_free_id:
                self.next_free_id = achievement.id + 1
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
        Generates the User.txt and Rich.txt files.
        """
        if path is None:
            root = Path.cwd()
            output = root / "output" / f"{self.title} - {self.game_id}"
        else:
            output = Path(path)

        output.mkdir(parents=True, exist_ok=True)
        
        # 1. Saves Achievements/Leaderboards (User.txt)
        user_file = output / f"{self.game_id}-User.txt"
        with open(user_file, "w", encoding="utf-8") as f:
            f.write("1.0\n")
            f.write(f"{self.title}\n")

            for ach in self.achievements:
                try:
                    f.write(ach.render() + "\n")
                except Exception as e:
                    print(f"error in ID achievement {ach.id}: '{ach.title}'")
                    print(f" description: {ach.description}")
                    raise e
            
            for lb in self.leaderboards:
                try:
                    f.write(lb.render() + "\n")
                except Exception as e:
                    print(f"error in Leaderboard ID {lb.id}: '{lb.title}'")
                    raise e

        # 2. Saves Rich Presence (Rich.txt)
        if self.rich_presence:
            rp_file = output / f"{self.game_id}-Rich.txt"
            with open(rp_file, "w", encoding="utf-8") as f:
                f.write(self.rich_presence.render())
            print(f"Generated Rich Presence file: {rp_file}")