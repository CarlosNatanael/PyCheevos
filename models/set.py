from typing import List
from .achievement import Achievement

class AchievementSet:
    def __init__(self, game_id: int, title: str):
        self.game_id = game_id
        self.title = title
        self.achievement: List[Achievement] = []

    def add_achievement(self, achievement: Achievement):
        self.achievement.append(achievement)
        return self
    
    def save(self, path: str = None):
        filename = path if path else f"{self.game_id}-User.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("1.0\n")
            f.write(f"{self.title}\n")

            for achievement in self.achievements:
                f.write(achievement.render() + "\n")
                
        print(f"Arquivo gerado com sucesso: {filename}")