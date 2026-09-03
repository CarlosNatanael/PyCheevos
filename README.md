# PyCheevos

**PyCheevos** is a set of tools to generate [RetroAchievements](https://retroachievements.org/) achievement sets programmatically using Python.

Inspired by **RATools** and **Cruncheevos**, it allows you to leverage the full power of the Python ecosystem (loops, functions, classes) to build complex achievement logic with clean, readable code.

* **[Core](https://github.com/CarlosNatanael/PyCheevos/tree/main/pycheevos/core)**: Handles condition parsing, memory addresses, arithmetic (`byte`, `word`, `delta`) and logic helpers (`reset_if`, `measured`). Now supports logical operators (`&`, `|`, `~`) and **f-strings** for clean condition chaining and text formatting.
* **[Models](https://github.com/CarlosNatanael/PyCheevos/tree/main/pycheevos/models)**: Provides the structure for Sets, Achievements, Leaderboards, and **Rich Presence** (now supporting independent saving and tuple lookups).
* **[Utils](https://github.com/CarlosNatanael/PyCheevos/tree/main/pycheevos/utils)**: Contains the **Smart Importer** CLI that automatically maps Code Notes to Python variables, fetching data from local files or directly from the RetroAchievements server.

#

### Installation

You can install PyCheevos directly from PyPI:

```bash
pip install pycheevos
```
> [!NOTE]
> Since the library is under active development, it is recommended to pin the version in your project to avoid breaking changes: `pip install pycheevos==0.0.8`

### Usage
Using this library assumes familiarity with the [RetroAchievements](https://docs.retroachievements.org) workflow and memory inspection.

### Quick Start with the Smart Importer

PyCheevos now includes a powerful CLI tool to scaffold your sets instantly.

Run the importer from any folder in your terminal:

```bash
pycheevos-import
```

Select **Option 3 (Unified Import)** to perform a "Smart Sync":

1. **Downloads Code Notes** and generates a `notes.py` file.
2. **Downloads Achievements** and generates an `achievements.py` file.
3. **Auto-Mapping:** The generator automatically detects variable names from `notes.py` and uses them in your achievement logic (e.g., `health == 0x04` instead of `byte(0x1234) == value(4)`).

---

### Manual Scripting

Create a new `.py` file and import the library modules (`models` and `core`).

Run your script to generate an `output` folder containing your RA logic files (`[ID]-User.txt`).

You can change this output location by defining a path in the `.save()` function of `AchievementSet`.

#### Small Demo
```python
from pycheevos.models.set import AchievementSet
from pycheevos.models.achievement import Achievement
from pycheevos.core.helpers import byte, prior, value, reset_if
from pycheevos.core.constants import AchievementType

# Initialize the set
game_set = AchievementSet(game_id=1, title="Sonic the Hedgehog")

# Define Memory Addresses
mem_rings = byte(0xFE20)
mem_zone  = byte(0xFE10)

# Reusable Logic Function
def got_rings(amount):
    """Triggers when ring count increases to or past 'amount'."""
    # Use '&' for AND, '|' for OR, '~' for NOT
    # Use value() to wrap constant numbers safely (optional if comparing against memory)
    return (mem_rings >= value(amount)) & (prior(mem_rings) < value(amount))

# Create Achievement
ach = Achievement(
    title="Super Ring Collector", 
    description="Collect 1000 rings", 
    points=50, 
    id=111001,
    type=AchievementType.PROGRESSION # Use Enum for safety
)

# Apply Logic
# New Syntax: You can chain logic directly using operators
ach.add_core(
    got_rings(1000) & (mem_zone == 0) # Must be in Green Hill
)

# Add reset logic using the helper function
ach.add_core(
    reset_if(mem_rings == 0)
)

game_set.add_achievement(ach)

# Generate the user file (1-User.txt)
game_set.save()
```

### User Repositories

* [CarlosNatanael/RA-Scripts-py](https://github.com/CarlosNatanael/RA-Scripts-py)
* [Player1041/PyCheevos-Scripts](https://github.com/Player1041/PyCheevos-Scripts)
* [wormi-ra/RA-Scripts](https://github.com/wormi-ra/RA-Scripts)
* [blobdash/RASets](https://github.com/blobdash/RASets)

> [!IMPORTANT]
> **Your repo here?** *Make a PR and add it!*

### Contributing

You are welcome to ***report issues***. If you run into errors generating the script, please include your Python version and the traceback.

You are welcome to ***request features***. When doing so, please show how you would use the feature (pseudo-code) and what logic problem it solves.

The core library aims to be minimal. Complex logic specific to a single game should ideally be implemented in your own script using Python's flexibility, rather than hardcoded into the library core.

***Pull Requests*** are welcome, especially for documentation improvements or type hinting fixes.
