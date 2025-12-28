# @pycheevos/models

The **Models** module defines the structural components of a RetroAchievements set. While `core` handles the logic (memory, conditions), `models` handles the containers that organize that logic into exportable files.

### Table of Contents
1. [AchievementSet](#1-achievementset)
    - [Initialization](#initialization)
    - [Methods](#methods)
2. [Achievement](#2-achievement)
    - [Initialization](#initialization-1)
    - [Logic Methods](#logic-methods)
3. [Leaderboard](#3-leaderboard)
    - [Initialization](#initialization-2)
    - [Logic Components](#logic-components)
4. [Rich Presence](#4-rich-presence)
    - [Initialization](#initialization-3)
    - [Lookups](#lookups)
    - [Display](#displays)
5. [Game Objects](#5-game-objects-poo)
    - [Definig a Class](#defining-a-class)
    - [Static vs Dynamic](#usage-static-vs-dynamic)
6. [How it works](#5-under-the-hood-how-it-works)
    - [The code](#the-code)

### 1. **AchievementSet**
The `AchievementSet` is the main container for your project. It holds all achievements, leaderboards, and the rich presence script, and is responsible for exporting them to text files.

#### **Initialization**
```py
from models.set import AchievementSet

game_set = AchievementSet(game_id=12345, title="My Awesome Game")
```
- **game_id**: The unique ID of the game on RetroAchievements.org.
- **title**: The name of the game (used for folder/file naming).

#### **Methods**
- `add_achievement(achievement)`: Registers an achievement object.
- `add_leaderboard(leaderboard)`: Registers a leaderboard object.
- `add_rich_presence(rp)`: Registers the Rich Presence object.
- `save(path=None)`: Exports `[ID]-User.txt` and `[ID]-Rich.txt`.
    - If `path` is not provided, defaults to an `output/` folder next to the script file.
#

### 2. **Achievement**
Represents a single achievement. It manages the logic groups: Core (Required) and Alts (Alternative paths).

#### **Initialization**
```py
from models.achievement import Achievement

ach = Achievement(
    title="Master of Unlocking",
    description="Unlock 10 doors.",
    points=5,
    id=111000001,
    badge="12345"
)
```
#### **Logic Methods**
- `add_core(conditions)`: Adds conditions that **must always be true**.
- `add_alt(conditions)`: Adds an **alternative group**. The achievement triggers if Core is True AND (Alt 1 is True OR Alt 2 is True...).
- `add_condition(condition)`: Helper to add a single condition to the Core group.


#### **Example: Logic with Alts**
```py
# Logic: Level 5 AND (Health > 0 OR Cheats = 0)
ach.add_core(mem_level == 5)

# Alt Group 1
ach.add_alt(mem_health > 0)

# Alt Group 2
ach.add_alt(mem_cheats == 0)
```
#

### 3. **Leaderboard**
Represents a leaderboard (Speedrun, High Score). It consists of four distinct logic sections.

#### **Initialization**
```py
from models.leaderboard import Leaderboard
from core.constants import LeaderboardFormat

lb = Leaderboard(
    title="Green Hill Zone Act 1",
    description="Fastest time",
    id=111000002,
    format=LeaderboardFormat.MILLISECS,
    lower_is_better=True
)
```
#### **Logic Components**

- `set_start(conditions)`: **START**. When these conditions become true, the attempt begins.
- `set_cancel(conditions)`: **CANCEL**. If these become true during an attempt, it is invalidated.
- `set_submit(conditions)`: **SUBMIT**. When these become true, the current value is sent to the server.
- `set_value(conditions)`: **VALUE**. The memory expression that calculates the score/time.
    - Note: The condition passed here usually needs the `MEASURED` flag if it's not a raw value.
#
### 4. **Rich Presence**
Handles the dynamic status display (Rich Presence) seen on the website.

#### **Initialization**
```py
from models.rich_presence import RichPresence
rp = RichPresence()
```

#### **Lookups**
Lookups map integer values to text strings (e.g., Level IDs to Level Names).
```py
rp.add_lookup("Mode", {
    0: "Arcade",
    1: "Story",
    2: "Versus"
})
```

#### **Displays**
The **Display** string is evaluated top-to-bottom. The first condition that evaluates to true determines the text shown.

- `add_display(condition, text)`: Adds a conditional string.
- **Macros**: Use static methods to insert dynamic values into the text.
    - `RichPresence.lookup("Name", mem_addr)`: Inserts a mapped string.
    - `RichPresence.value(mem_addr, format)`: Inserts a number.

#

### 5. **Game Objects (POO)**
You can create reusable classes for game entities (like Player, Enemy, Inventory) using the `GameObject` base class. This allows you to define memory offsets once and reuse them for both static memory addresses and dynamic pointers.

#### **Defining a Class**
Inherit from `GameObject` and use `self.offset()` to map memory relative to the object's base.

```python
from models.generic import GameObject
from core.helpers import byte, word

class Player(GameObject):
    def __init__(self, address):
        super().__init__(address)
        # Define properties: self.offset(distance, type)
        self.health = self.offset(0x00, byte)
        self.coins  = self.offset(0x04, word)
    
    def is_dead(self):
        return self.health == 0
```

#### **Usage (Static vs Dynamic)**
The logic handles both integers (Static RAM) and MemoryValues (Pointers) automatically.

```python
from core.helpers import dword

# Scenario A: Player is always at 0x1000
p1 = Player(0x1000)

# Scenario B: Player is at the address pointed to by 0x5000
pointer = dword(0x5000)
p2 = Player(pointer)

# Using properties
ach.add_core(p1.is_dead())
ach.add_core(p2.coins >= 50)
```
#
### 6. **Under the Hood: How it works**
Here is a complete example showing the Python code and the exact string PyCheevos generates for RetroAchievements.

**The Scenario: "Untouchable"**

**Goal**: Complete Stage 1 with 50+ coins without taking damage.

#### **The Code**
```py
from models.set import AchievementSet
from models.achievement import Achievement
from core.helpers import byte
from core.constants import Flag

def damage_car():
    mem_damage = byte(0x000076)
    mem_event = byte(0x0007dd)
    mem_green = byte(0x00009e)
    mem_position = byte(0x0007d9)
    mem_circuit = byte(0x0013de)

    # 1. Start Condition: Green Light (0) for 1 frame
    cond_start = (mem_green == 0).with_hits(1)
    
    # 2. Track & Rank requirements
    circuit_monaco = (mem_circuit == 14)
    cond_first = (mem_position == 0)

    # 3. Trigger: Event changed to 7 (Victory)
    victory_cond = (mem_event == 7)
    victory_cond.flag = Flag.TRIGGER

    # 4. Delta Check: Event was 13 previously
    delta_circuit = (mem_event.delta() == 13)

    core = [
        cond_start,
        circuit_monaco,
        cond_first,
        victory_cond,
        delta_circuit
    ]

    # 5. Reset: If Damage > 0
    cond_reset = (mem_damage > 0)
    cond_reset.flag = Flag.RESET_IF

    alt_damage = [cond_reset]

    return core, alt_damage

# Setup
my_set = AchievementSet(game_id=23121, title="Racing game")

monaco_damageless = Achievement(
    title="Untouchable",
    description="Win a race at the Monaco circuit with zero damage to your car",
    points=25,
    badge="00000"
)

l_core, l_alt1 = damage_car()

monaco_damageless.add_core(l_core)
monaco_damageless.add_alt(l_alt1) # Adds Reset logic as an Alternate Group

my_set.add_achievement(monaco_damageless)
# my_set.save()
```

#### **The Generated Output**
This is the string written to `23121-User.txt`:
```plaintext
1:"0xH00009e=0.1._0xH0013de=14_0xH0007d9=0_T:0xH0007dd=7_d0xH0007dd=13SR:0xH000076>0":Untouchable:Win a race at the Monaco circuit with zero damage to your car::::PyCheevos:25:::::00000
```

#### **Decoding the String**

|python|Generated|Meaning|
|------|---------|-------|
|`(mem_green == 0).with_hits(1)`|`0xH00009e=0.1.`|Addr 0x9e must be 0 (Hit Count: 1).
|`mem_circuit == 14`|`0xH0013de=14`|Track ID must be 14 (Monaco).|
|`victory_cond` (Flag.TRIGGER)|`T:0xH0007dd=7`|Trigger icon when Event is 7.|
|`mem_event.delta() == 13`|`d0xH0007dd=13`|Previous Event value must be 13.
|`add_alt(...)`|`S`|Separator for Alternate Group.
|`cond_reset` (Flag.RESET_IF)|`R:0xH000076>0`|Reset if Damage is > 0.

