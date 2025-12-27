# PyCheevos

**PyCheevos** is a set of tools to generate [RetroAchievements](https://retroachievements.org/) achievement sets programmatically using Python.

Inspired by **RATools** and **Cruncheevos**, it allows you to leverage the full power of the Python ecosystem (loops, functions, classes) to build complex achievement logic with clean, readable code.

- **Core**: Handles condition parsing, memory addresses, and arithmetic logic (`byte`, `word`, `delta`, `prior`).

- **Models**: Provides the structure for Sets, Achievements, Leaderboards, and Rich Presence.

### Usage
Using this library assumes familiarity with the [RetroAchievements](https://docs.retroachievements.org) workflow and memory inspection.

#### Small Demo
``` Python
from models.set import AchievementSet
from models.achievement import Achievement
from core.helpers import byte, prior

# Initialize the set
game_set = AchievementSet(game_id=1, title="Sonic the Hedgehog")

# Define Memory Addresses
mem_rings = byte(0xFE20)
mem_zone  = byte(0xFE10)

# Reusable Logic Function
def got_rings(amount):
    """Triggers when ring count increases to or past 'amount'."""
    return [
        mem_rings >= amount,       # Current rings >= amount
        prior(mem_rings) < amount  # Previous rings < amount
    ]

# Create Achievement
ach = Achievement(
    title="Super Ring Collector", 
    description="Collect 1000 rings", 
    points=50, 
    id=111001
)

# Apply Logic
ach.add_core(got_rings(1000))
ach.add_condition(mem_zone == 0) # Extra condition: Must be in Green Hill

game_set.add_achievement(ach)

# Generate the user file (1-User.txt)
game_set.save()
```

### Contributing
You are welcome to ***report issues***. If you run into errors generating the script, please include your Python version and the traceback.

You are welcome to ***request features***. When doing so, please show how you would use the feature (pseudo-code) and what logic problem it solves.

The core library aims to be minimal. Complex logic specific to a single game should ideally be implemented in your own script using Python's flexibility, rather than hardcoded into the library core.

***Pull Requests*** are welcome, especially for documentation improvements or type hinting fixes.

#