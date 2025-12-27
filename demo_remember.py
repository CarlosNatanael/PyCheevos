from models.set import AchievementSet
from models.achievement import Achievement
from core.helpers import byte, recall
from core.constants import Flag
from core.condition import Condition

# Setup
game_set = AchievementSet(game_id=9999, title="Remember/Recall Demo")

# Memory
mem_coins = byte(0x00A1)
mem_state = byte(0x00FF)

# =======================================================================
# ACHIEVEMENT: "Hoarder"
# Logic: Have 50 MORE coins than you had at the start of the level.
# =======================================================================
ach_hoarder = Achievement("Hoarder", "Collect 50 coins in one run.", 10, 111000005)

# 1. REMEMBER (K:)
# We want to "Remember" the coin count.
# Since 'Remember' is just a flag applied to a memory address, we create a
# raw Condition and apply the flag.
# Generates: K:0xH00a1 (Stores current coins in the recall buffer)
store_coins = Condition(mem_coins).with_flag(Flag.REMEMBER)

# 2. RECALL ({recall})
# We compare the current coin count against the stored value ({recall}) + 50.
# Generates: 0xH00a1 >= {recall} + 50
check_gain = (mem_coins >= recall() + 50)

# 3. CONTEXT (Reset)
# If we go back to the menu (State 0), we stop/reset the logic.
# ResetIf: 0xH00ff = 0
reset_menu = (mem_state == 0).with_flag(Flag.RESET_IF)

# Combine them
ach_hoarder.add_core([
    reset_menu,   # Reset if in menu
    store_coins,  # K: Remember coins
    check_gain    # Check if Current >= Recall + 50
])

game_set.add_achievement(ach_hoarder)
game_set.save()