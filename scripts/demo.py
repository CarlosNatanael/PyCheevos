# demo_full.py
# PyCheevos Comprehensive Demo
# This script demonstrates every feature available in the library.

from models.set import AchievementSet
from models.achievement import Achievement
from models.leaderboard import Leaderboard
from models.rich_presence import RichPresence

from core.helpers import (
    byte, word, dword, bit0, bit7, float32,  # Memory sizes helpers
    prior, delta, bcd, invert, recall,       # Value modifiers
    bitcount                                 # Special functions
)
from core.constants import Flag, LeaderboardFormat
from core.condition import Condition

# =======================================================================
# 1. SETUP THE SET
# =======================================================================
# Initialize the achievement set container.
# 'game_id' must match the ID on RetroAchievements.org.
game_set = AchievementSet(game_id=12345, title="PyCheevos Demo Game")


# =======================================================================
# 2. DEFINING MEMORY ADDRESSES
# =======================================================================
# It is best practice to map memory addresses to variable names first.
# This makes the logic much easier to read and maintain.
mem_state       = byte(0x00A1)   # Game State (e.g., 0=Menu, 1=Ingame)
mem_score       = dword(0x00B0)  # 32-bit Score value
mem_health      = byte(0x00C0)   # 8-bit Health value
mem_stage       = byte(0x00D0)   # Current Stage ID
mem_timer       = word(0x00E0)   # Timer (e.g., in seconds or frames)
base_pointer    = dword(0x1000)  # Base address for a pointer structure


# =======================================================================
# 3. CREATING AN ACHIEVEMENT (BASIC LOGIC)
# =======================================================================
# Achievement: "Survivor"
# Goal: Finish Stage 1 with full health (100).
ach_survivor = Achievement(
    title="Survivor",
    description="Finish Stage 1 with full health.",
    points=5,
    id=111000001,
    badge="12345"
)

# Trigger Logic: The event happens when the stage changes FROM 1 (Delta) TO something else.
# We use a list to group these conditions.
cond_complete_trigger = [
    (mem_stage.delta() == 1),  # Previous frame, stage was 1
    (mem_stage > 1)            # Current frame, stage is greater than 1 (completed)
]

# Core Group: Conditions that must ALL be true.
ach_survivor.add_core([
    (mem_stage == 1),          # Must be in Stage 1
    (mem_state == 1),          # Must be Ingame
    (mem_health == 100)        # Health must be full
])

# Add the trigger logic to the core group as well.
ach_survivor.add_core(cond_complete_trigger)

# Register the achievement to the set.
game_set.add_achievement(ach_survivor)


# =======================================================================
# 4. ADVANCED ACHIEVEMENT (POINTERS, HITS, RESETS, ALTS)
# =======================================================================
# Achievement: "Treasure Hunter"
# Goal: Collect 50 coins in the Forest OR 50 coins in the Cave without taking damage.
ach_treasure = Achievement(
    title="Treasure Hunter",
    description="Collect 50 coins in Forest or Cave without taking damage.",
    points=10,
    id=111000002
)

# POINTER LOGIC (AddAddress):
# The '>>' operator creates a pointer chain.
# Logic: Read address at 'base_pointer', add offset 0x20, then read that final address.
# Generates: I:0xX001000_0xH000020 (Dynamic Coin Address)
dynamic_coins = (base_pointer >> byte(0x20))

# RESET LOGIC (ResetIf):
# The achievement resets if the player takes damage.
# Logic: Current Health < Previous Health (Prior).
reset_damage = (mem_health < prior(mem_health))
reset_damage.flag = Flag.RESET_IF  # Mark this condition as a Reset

# HIT COUNT LOGIC:
# We track how many times the coin count increased.
# Logic: Dynamic Coins > Previous Dynamic Coins (Delta).
# .with_hits(50) requires this to happen 50 times to trigger.
collect_count = (dynamic_coins > dynamic_coins.delta()).with_hits(50)

# CORE GROUP:
# Contains the logic that applies to both paths (Reset & Hit Count).
ach_treasure.add_core([reset_damage, collect_count])

# ALT GROUPS (OR Logic):
# Path A: The player is in the Forest (ID 5).
ach_treasure.add_alt(mem_stage == 5)

# Path B: The player is in the Cave (ID 6).
ach_treasure.add_alt(mem_stage == 6)

game_set.add_achievement(ach_treasure)


# =======================================================================
# 6. LEADERBOARDS (START, CANCEL, SUBMIT, VALUE)
# =======================================================================
# Leaderboard: "Speedrun Stage 1"
# Logic: Track time while in Stage 1. Submit the time when Stage 1 is cleared.
lb_speedrun = Leaderboard(
    title="Stage 1 Speedrun",
    description="Fastest time for Stage 1",
    id=111000004,
    format=LeaderboardFormat.MILLISECS, # Display format (e.g., MM:SS.mm)
    lower_is_better=True                # Lower value is a better score
)

# START: Start the timer when we enter Stage 1.
# Logic: Current Stage is 1 AND Previous Stage was NOT 1.
lb_start = [(mem_stage == 1), (mem_stage.prior() != 1)]

# CANCEL: Cancel the attempt if we return to the Menu (State 0).
lb_cancel = [(mem_state == 0)]

# SUBMIT: Submit the score when the stage changes to 2 (Completed).
lb_submit = [(mem_stage == 1), (mem_stage.delta() == 2)]

# VALUE: The actual value to track and submit.
# Must use the MEASURED flag (M:) on the value condition.
# Note: 'Condition()' wrapper is used to apply flags to a raw memory value.
lb_value = Condition(mem_timer, flag=Flag.MEASURED)

# Assign logic groups to the leaderboard
lb_speedrun.set_start(lb_start)
lb_speedrun.set_cancel(lb_cancel)
lb_speedrun.set_submit(lb_submit)
lb_speedrun.set_value(lb_value) 

game_set.add_leaderboard(lb_speedrun)


# =======================================================================
# 8. EXPORT EVERYTHING
# =======================================================================
# Saves the data to '12345-User.txt' in the current directory.
# You can then move this file to your emulator's 'RACache/Data' folder.
game_set.save()

print("Demo script executed successfully! Check the output files.")