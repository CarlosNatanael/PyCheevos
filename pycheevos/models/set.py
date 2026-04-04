from typing import List, Optional
from pathlib import Path
from pycheevos.models.achievement import Achievement
from pycheevos.models.leaderboard import Leaderboard
from pycheevos.models.rich_presence import RichPresence

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
        json_file = output / f"{self.game_id}.json"

        if json_file.exists():
            try:
                import json
                with open(json_file, 'r', encoding='utf-8') as jf:
                    game_data = json.load(jf)

                    # --- Synchronize Achievements ---
                    server_achs = game_data.get('Achievements', [])
                    title_to_id, desc_to_id, mem_to_id = {}, {}, {}

                    for s_ach in server_achs:
                        a_id = s_ach.get('ID')
                        if not a_id: continue
                        
                        if 'Title' in s_ach: 
                            title_to_id[s_ach['Title'].lower().strip()] = a_id
                        if 'Description' in s_ach: 
                            desc_to_id[s_ach['Description'].lower().strip()] = a_id
                        if 'Mem' in s_ach: 
                            mem_to_id[s_ach['Mem']] = a_id
                    
                    for ach in self.achievements:
                        # Rebuilds the memory string for the logic fallback
                        core_string = ach._render_group(ach.core)
                        if ach.alts:
                            full_mem = core_string + "S" + "S".join([ach._render_group(alt) for alt in ach.alts])
                        else:
                            full_mem = core_string

                        # Variáveis seguras e minúsculas para a busca
                        safe_title = ach.title.lower().strip()
                        safe_desc = ach.description.lower().strip()

                        # The Smart Waterfall (agora case-insensitive)
                        if safe_title in title_to_id:
                            ach.id = int(title_to_id[safe_title])
                        elif safe_desc in desc_to_id:
                            ach.id = int(desc_to_id[safe_desc])
                        elif full_mem in mem_to_id:
                            ach.id = int(mem_to_id[full_mem])

                    # --- Synchronize Leaderboards ---
                    server_lbs = game_data.get('Leaderboards', [])
                    lb_title_to_id, lb_desc_to_id = {}, {}

                    for s_lb in server_lbs:
                        l_id = s_lb.get('ID')
                        if not l_id: continue
                        if 'Title' in s_lb: 
                            lb_title_to_id[s_lb['Title'].lower().strip()] = l_id
                        if 'Description' in s_lb: 
                            lb_desc_to_id[s_lb['Description'].lower().strip()] = l_id
                    
                    for lb in self.leaderboards:
                        safe_lb_title = lb.title.lower().strip()
                        safe_lb_desc = lb.description.lower().strip()
                        
                        if safe_lb_title in lb_title_to_id:
                            lb.id = int(lb_title_to_id[safe_lb_title])
                        elif safe_lb_desc in lb_desc_to_id:
                            lb.id = int(lb_desc_to_id[safe_lb_desc])

                    print(f"[SYNC] IDs successfully synced (Cascade) from {json_file.name}!")
            except Exception as e:
                print(f"[WARNING] Could not sync IDs from JSON: {e}")

        preserved_notes = []
        
        mode = "r+" if user_file.exists() else "w"
        with open(user_file, mode, encoding="utf-8", errors="ignore") as f:
            if mode == "r+":
                preserved_notes = [line.strip() for line in f if line.startswith("N0:")]
                f.seek(0)
                
            f.write("1.0\n")
            f.write(f"{self.title}\n")
            for ach in self.achievements:
                try:
                    f.write(ach.render() + "\n")
                except Exception as e:
                    print(f"Error in ID achievement {ach.id}: '{ach.title}'\n description: {ach.description}")
                    raise e
            for lb in self.leaderboards:
                try:
                    f.write(lb.render() + "\n")
                except Exception as e:
                    print(f"error in Leaderboard ID {lb.id}: '{lb.title}'")
                    raise e
            for note in preserved_notes:
                f.write(note + "\n")
            if mode == "r+":
                f.truncate()
        print(f"Generated User file: {user_file}")

        # 2. Saves Rich Presence (Rich.txt)
        if self.rich_presence:
            rp_file = output / f"{self.game_id}-Rich.txt"
            with open(rp_file, "w", encoding="utf-8") as f:
                f.write(self.rich_presence.render())
            print(f"Generated Rich Presence file: {rp_file}")