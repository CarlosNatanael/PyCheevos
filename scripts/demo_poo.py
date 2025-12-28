from models.set import AchievementSet
from models.achievement import Achievement
from models.generic import GameObject  # <--- Imports the class that was created, GameObject
from core.helpers import byte, delta   # Imports helpers needed for specific logic

#1. We define the Character's class (Specific to this game)
class SlyCooper(GameObject):
    def __init__(self, address):
        super().__init__(address)
        # We mapped the memory related to the beginning of the Sly object.
        self.key_count = self.offset(0x50, byte) 
        self.health    = self.offset(0x10, byte)

    def got_key(self, now=False):
        """
        Logic: Having the key
        now=True -> Got the key at THIS exact frame
        """
        logic = [self.key_count >= 1] # I have the key

        if now:
            # And it wasn't in the previous frame (delta)
            logic.append(delta(self.key_count) == 0)
            
        return logic

# 2. We begin the normal script.
my_set = AchievementSet(game_id=12345, title="Sly Cooper")

# We instantiate the object (Assuming Sly is at address 0x00F000)
player = SlyCooper(0x00F000)

# We created the achievement
ach = Achievement("Mestre das Chaves", "Pegue uma chave", 5)

# We use the smart method.
ach.add_core(player.got_key(now=True))

my_set.add_achievement(ach)
my_set.save()