# PyCheevos 🏆

A Python library for generating RetroAchievements achievement sets programmatically.
Inspired by **RATools** and **Cruncheevos**, but focused on the simplicity and power of the Python ecosystem.

## 🚀 Getting Started

1.  Clone this repository.
2.  Create a Python script (e.g., `my_game.py`) in the root directory.
3.  Import the modules and start coding!

## 🛠️ Quick Guide

### 1. Memory Access
Use *helpers* to define memory addresses. You don't need to worry about hexadecimal prefixes (`0xH`, `0x `, `0xX`); the library handles them for you.

```python
from core.helpers import byte, word, dword, bit0, float32

# Definitions
coins  = byte(0x1234)        # 8-bit
time   = word(0x5678)        # 16-bit
score  = dword(0x9ABC)       # 32-bit
flag   = bit0(0x0001)        # Specific Bit
pos_x  = float32(0x3333)     # Float 32-bit
```
### 2. Modifiers (Delta, Prior, BCD)
Chain methods or use helpers to access previous values or changes.

```python
from core.helpers import delta, prior, bcd

# Example: If coins increased
earned_coin = (coins > prior(coins))

# Example: If value changed (Delta)
value_changed = (time != delta(time))
```
### 3. Creating Achievements
Achievements support Core (Required) and Alts (OR Logic) groups.

```python
from models.set import AchievementSet
from models.achievement import Achievement

# Initialize the Set
my_set = AchievementSet(game_id=1111, title="My Game")

# Define the Achievement
ach = Achievement("Collector", "Collect 100 coins", points=5)

# Logic: Coins >= 100 AND Prev Coins < 100
logic = [
    (coins >= 100),
    (prior(coins) < 100)
]

ach.add_core(logic)
my_set.add_achievement(ach)
```

### 4. Memory Arithmetic
Complex additions and subtractions (AddSource, SubSource) are handled naturally.

```python
# A + B > 50
condition = (byte(0x10) + byte(0x20) > 50)
```

### 5. Leaderboards
Full support for Start, Cancel, Submit, and Value conditions.

```python
from models.leaderboard import Leaderboard
from core.constants import LeaderboardFormat

lb = Leaderboard(
    title="Time Attack",
    description="Finish fast",
    format=LeaderboardFormat.MILLISECS,
    lower_is_better=True
)

lb.set_start(byte(0x99) == 1)       # Race started
lb.set_cancel(byte(0x99) == 0)      # Left race
lb.set_submit(byte(0xAA) == 1)      # Finished
lb.set_value(dword(0xBB))           # Time value

my_set.add_leaderboard(lb)
```
### 6. Rich Presence

Create dynamic statuses for Discord and the RA website.

```python
from models.rich_presence import RichPresence

rp = RichPresence()
rp.add_lookup("Levels", {0: "Menu", 1: "Forest"})

# Conditional Display
rp.add_display(byte(0x10) == 0, "In Menu")
rp.add_display("True", "Level: @Levels(0x10) | Lives: @VALUE(0x12)")

my_set.add_rich_presence(rp)
```

### 7. Generating the File
Finally, save the file to your emulator's folder `(RACache/Data)`.

```python
my_set.save() 
# Generates: 1111-User.txt and 1111-Rich.txt
```