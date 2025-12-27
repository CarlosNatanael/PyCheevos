# @pycheevos/core

The Core module is the engine of PyCheevos. It handles memory addressing, variable types, arithmetic operations, and condition generation.

While `models` (Achievement, Set) handle the "structure", `core` handles the "logic".

### Table of Contents

1. [Memory Helpers](#1-memory-helpers)
    - [Standard Sizes](#standard-sizes)
    - [Bits & Nibbles](#bits--nibbles)
    - [Floating Point](#floating-point)
2. [Value Modifiers](#2-value-modifiers)
3. [Arithmetic & Pointers](#3-arithmetic--pointers)
    - [Basic Math](#basic-math)
    - [Pointer Chains](#pointer-chains-)
4. [Bitwise Operations](#4-bitwise-operations)
5. [Conditions & Flags](#5-conditions--flags)
6. [Remember & Recall](#6-remember--recall)

#

### 1. **Memory Helpers**

Located in `core.helpers`, these functions are the primary way to define memory addresses. You generally do not need to import `MemoryValue` directly.

#### **Standard Sizes**

|function | size | RA Syntax | Example|
|---------|------|-----------|--------|
|`byte(addr)`| 8-bit| `0xh...`|`byte(0x100)`|
|`word(addr)`| 16-bit|`0x ...`|`word(0x100)`|
|`dword(addr)`| 32-bit|`0xX...`|`dword(0x100)`|

#### **Bits & Nibbles**

|function | Description | RA Syntax|
|---------|-------------|----------|
|`bit0(addr)`...`bit7(addr)`|Single Bit access| `0xM...` to `0xT...`|
|`lower(addr)`|Lower 4 bits (Nibble)| `0xL...`|
|`high4(addr)`|Upper 4 bits (Nibble)| `0xU...`|


#### **Floating Point**

|function | Description | RA Syntax|
|---------|-------------|----------|
|`float32(addr)`|32-bit Float |`fF...`|
|`float32be(addr)`|32-bit Float (Big Endian)|`fB...`
|`double32(addr)`|32-bit Double|`fH...`
|`mbf32(addr)`|Microsoft Binary Format|`fM...`


#### **Usage Example**:
```python
from core.helpers import byte, word, bit0

level_id = byte(0x00A1)
timer    = word(0x00B0)
is_active = bit0(0x00F0)
```

### 2. **Value Modifiers**

These functions transform how the emulator reads a value relative to the previous frame.

`prior(memory)`

Returns the value the memory had in the **previous frame**.
- **Use case**: Detecting changes or strictly increasing values.
- **Example**: `coins > prior(coins)` (Coins increased).

`delta(memory)`

Similar to `prior`, but strictly used for change detection logic in [RAIntegration](https://github.com/RetroAchievements/RAIntegration/).
- **Use case**: `level_id != delta(level_id)` (Level ID changed).

`bcd(memory)`

Interprets the memory value as Binary-Coded Decimal.
- **Use case**: Games that store "10" lives as `0x10` instead of `0x0A`.

`invert(memory)`

Returns the bitwise inversion of the value (`~`).

#### **Usage Example**:
```python
from core.helpers import byte, prior, bcd

lives = byte(0x1234)

# Check if lives decreased
lost_life = lives < prior(lives)

# Compare BCD value
has_10_lives = bcd(lives) == 10
```

### 3. Arithmetic & Pointers
The `MemoryValue` objects support standard Python math operators. These are compiled into `AddSource` and `SubSource` chains.

#### **Basic Math**
You can add, subtract, multiply, and divide memory addresses and constants.
```python
# Logic: (0xH100 + 0xH200) > 50
total_ammo = byte(0x100) + byte(0x200)
condition = (total_ammo > 50)
```

#### **Pointer Chains** (`>>`)
The right-shift operator (`>>`) is overloaded to handle **AddAddress** logic (pointers). It reads the value on the left, adds it as an offset to the value on the right.
- **Syntax**: `Base >> Offset`
- **RA Logic**: `I:Base_Offset`

```python
player_base = dword(0x0800)
offset_hp   = byte(0x0040)

# Read [PlayerBase] + 0x40
current_hp = (player_base >> offset_hp)
```
### 4. **Bitwise Operations**
You can perform bitwise logic between memory addresses or constants.

|Operator|Description|RA Operator|
|--------|-----------|-----------|
|`&`|	Bitwise AND	|`&`|
|`^`|	Bitwise XOR	|`^`|
|`*`|	Multiply	|`*`|
|`/`|	Divide	|`/`|
|`%`|	Modulo	|`%`|


```python
flags = byte(0x5000)

# Check if flags has bits 0x03 (0000 0011) set
masked = (flags & 0x03)
is_active = (masked == 0x03)
```

### 5. **Conditions & Flags**
A `Condition` is generated when you compare a `MemoryValue` (e.g., `==`, `>`, `<=`). You can attach special behaviors to these conditions.

`.with_hits(count)`

Requires the condition to be true `count` times for the achievement to trigger.

```python
# Trigger only after being in this state for 60 frames (1 second)
(state == 1).with_hits(60)
```


`.with_flag(Flag)`

Applies logic flags like Reset, Pause, or Measured. Available flags in `core.constants.Flag`:
- `Flag.RESET_IF`: Resets the achievement progress if true.
- `Flag.PAUSE_IF`: Pauses hit counting if true.
- `Flag.TRIGGER`: Explicit trigger condition.
- `Flag.MEASURED`: Shows a progress bar in the overlay.

#### **Usage Example:**
```python
from core.constants import Flag

# Reset if player dies
reset = (lives == 0).with_flag(Flag.RESET_IF)

# Show progress bar for 100 coins
measure = (coins >= 100).with_flag(Flag.MEASURED)
```
### 6. **Remember & Recall**
This system allows you to store a memory value and compare it against itself later in the same frame evaluation.

1. **Remember**: Use `.with_flag(Flag.REMEMBER)` on a condition (usually `addr`) to store its value.
2. **Recall**: Use `recall()` helper to access that stored value.

#### **Example: Check if Ammo increased by exactly 5**
```python
from core.helpers import recall
from core.constants import Flag

# 1. Store 'Ammo' into the Recall buffer
store = Condition(mem_ammo).with_flag(Flag.REMEMBER)

# 2. Check if Current Ammo == Stored Ammo + 5
check = (mem_ammo == recall() + 5)

achievement.add_core([store, check])
```

Logic generated: `K:0xH1234_0xH1234={recall}+5`