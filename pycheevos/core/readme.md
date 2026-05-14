# @pycheevos/core

The Core module is the engine of PyCheevos. It handles memory addressing, variable types, arithmetic operations, and condition generation.

While [`models`](https://github.com/CarlosNatanael/PyCheevos/tree/main/models) (Achievement, Set) handle the "structure", `core` handles the "logic".

### Table of Contents

- [@pycheevos/core](#pycheevoscore)
    - [Table of Contents](#table-of-contents)
    - [1. **Memory Helpers**](#1-memory-helpers)
      - [**Standard Sizes**](#standard-sizes)
      - [**Bits \& Nibbles**](#bits--nibbles)
      - [**Floating Point**](#floating-point)
    - [2. **Constants \& Safety (`value`)**](#2-constants--safety-value)
    - [3. **Enums \& Constants**](#3-enums--constants)
      - [**Achievement Types**](#achievement-types)
      - [**Leaderboard Formats**](#leaderboard-formats)
    - [4. **Value Modifiers**](#4-value-modifiers)
    - [5. Arithmetic \& Pointers](#5-arithmetic--pointers)
      - [**Basic Math**](#basic-math)
      - [**Pointer Chains** (`>>`)](#pointer-chains-)
    - [6. **Bitwise Operations (Memory)**](#6-bitwise-operations-memory)
    - [7. **Conditions, Flags \& Logic**](#7-conditions-flags--logic)
      - [**Logic Helpers (New Syntax)**](#logic-helpers-new-syntax)
      - [**Hit Counts (`.with_hits`)**](#hit-counts-with_hits)
      - [**Applying Flags (Manual)**](#applying-flags-manual)
      - [**Logical Operators (Chain)**](#logical-operators-chain)
    - [8. **Remember \& Recall**](#8-remember--recall)
    - [9. **Strings**](#9-strings)

---

### 1. **Memory Helpers**

Located in `core.helpers`, these functions are the primary way to define memory addresses.

#### **Standard Sizes**
| Function | Size | RA Syntax | Example |
|---|---|---|---|
| `byte(addr)` | 8-bit | `0xh...` | `byte(0x100)` |
| `word(addr)` | 16-bit | `0x ...` | `word(0x100)` |
| `dword(addr)` | 32-bit | `0xX...` | `dword(0x100)` |

#### **Bits & Nibbles**
| Function | Description | RA Syntax |
|---|---|---|
| `bit0(addr)`...`bit7(addr)` | Single Bit access | `0xM...` to `0xT...` |
| `lower(addr)` | Lower 4 bits (Nibble) | `0xL...` |
| `high4(addr)` | Upper 4 bits (Nibble) | `0xU...` |

#### **Floating Point**
| Function | Description | RA Syntax |
|---|---|---|
| `float32(addr)` | 32-bit Float | `fF...` |
| `float32be(addr)` | 32-bit Float (Big Endian) | `fB...` |
| `mbf32(addr)` | Microsoft Binary Format | `fM...` |

---

### 2. **Constants & Safety (`value`)**

Python evaluates mathematical comparisons immediately (`0 == 0` becomes `True`). To treat constant numbers as Logic Objects (so they can accept flags or be part of a generated condition), use `value()`.

```python
from pycheevos.core.helpers import value, measured

# BAD: Python calculates this as False, logic is lost
# measured(0 == 1)

# GOOD: PyCheevos treats this as a Condition object
measured(value(0) == value(1))

# Comparison with memory (Optional but recommended for clarity)
byte(0x1234) > value(10) 
```

---

### 3. **Enums & Constants**

Use these Enums from `core.constants` to ensure your scripts are typo-free and valid.

#### **Achievement Types**

Used in `Achievement(type=...)`.

* `AchievementType.STANDARD`: Default.
* `AchievementType.PROGRESSION`: Events that happen naturally (Level completion).
* `AchievementType.WIN_CONDITION`: Beating the game.
* `AchievementType.MISSABLE`: Events that can be missed.

#### **Leaderboard Formats**

Used in `Leaderboard(format=...)`.

* `LeaderboardFormat.VALUE`: Generic score.
* `LeaderboardFormat.SECS`: Seconds.
* `LeaderboardFormat.MILLISECS`: Milliseconds.
* `LeaderboardFormat.FRAMES`: Frames (converts to time).
* `LeaderboardFormat.SCORE`: Score points (000000).

---

### 4. **Value Modifiers**

These functions transform how the emulator reads a value relative to the previous frame.

* **`delta(memory)`**: Value from the **previous frame**.
* **`prior(memory)`**: Last **different** value.
* **`bcd(memory)`**: Interprets value as Binary-Coded Decimal.
* **`invert(memory)`**: Bitwise inversion (`~`).

```python
# Check if lives decreased
lives < prior(lives)
```

---

### 5. Arithmetic & Pointers

The `MemoryValue` objects support standard Python math operators.

#### **Basic Math**

```python
# Logic: (0xH100 + 0xH200) > 50
total_ammo = byte(0x100) + byte(0x200)
condition = (total_ammo > 50)
```

#### **Pointer Chains** (`>>`)

The right-shift operator (`>>`) is overloaded to handle **AddAddress** logic (pointers).

* **Syntax**: `Base >> Offset`

```python
player_base = dword(0x0800)
offset_hp   = byte(0x0040)

# Read [PlayerBase] + 0x40
current_hp = (player_base >> offset_hp)
```

---

### 6. **Bitwise Operations (Memory)**

You can perform bitwise logic between memory addresses or constants.

| Operator | Description | RA Operator |
| --- | --- | --- |
| `&` | Bitwise AND | `&` |
| `^` | Bitwise XOR | `^` |
| `*` | Multiply | `*` |
| `/` | Divide | `/` |

```python
# Check if flags has bits 0x03 set
is_active = ((flags & 0x03) == 0x03)
```

---

### 7. **Conditions, Flags & Logic**

#### **Logic Helpers (New Syntax)**

Instead of `.with_flag()`, you can now use wrapper functions. This is cleaner and easier to read.

```python
from pycheevos.core.helpers import reset_if, pause_if, measured

reset_if(level_id != 1)
pause_if(game_paused == 1)
measured(coins)
```

**Available Helpers:**
`reset_if`, `pause_if`, `measured`, `trigger`, `measured_if`, `add_source`, `sub_source`, `add_hits`, `sub_hits`, `add_address`, `remember`.

#### **Hit Counts (`.with_hits`)**

Requires the condition to be true `count` times for the achievement to trigger.

```python
# Trigger only after being in this state for 60 frames (1 second)
(state == 1).with_hits(60)
```

#### **Applying Flags (Manual)**

If you prefer the old syntax, you must import the **Uppercased** constants from `core.constants`.

```python
from pycheevos.core.constants import RESET_IF

(level_id != 1).with_flag(RESET_IF)
```

#### **Logical Operators (Chain)**

You can chain conditions using Python bitwise operators. This automatically generates `AND_NEXT` and `OR_NEXT` flags.

| Operator | Symbol | RA Flag | Description |
| --- | --- | --- | --- |
| **AND** | `&` | `AND_NEXT` | All conditions must be true. |
| **OR** | `\|` | `OR_NEXT` |
| **NOT** | `~` | N/A | Inverts comparison and logic. |

```python
# (In Game) AND (Level 1)
logic = (byte(0x10) == 1) & (byte(0x20) == 1)
```

---

### 8. **Remember & Recall**

Store a memory value and compare it later in the same frame.

1. **Remember**: `remember(condition)` function.
2. **Recall**: `recall()` helper to access that stored value.

```python
from pycheevos.core.helpers import recall, byte, remember

# Check if Ammo increased
logic = [
    remember(byte(0xAmmo)),
    byte(0xAmmo) > recall()
]
```

### 9. **Strings**

Use the helper method `string_equals` to generate string comparison conditions.

**Parameters:**
* `address`: (Required) Memory address to compare.
* `string`: (Required) String value to compare.
* `length`: Fixed string length in bytes, default to the full encoded length of `string`.
* `transform`: Any transform method or lambda that will be applied to the left value of each condition as such: `transform(lvalue)`.
* `endianness`: `"big"` or `"little"`, default to `"big"`.
* `encoding`: Any python-supported encoding such as `"utf-8"`, `"utf-16"`, `"shift-jis"`... default to `"ascii"`.

```python
from pycheevos.core.helpers import string_equals, delta

address = 0x1000
# Minimal Example
logic = string_equals(address, "Hello World")
# Full Example
logic = string_equals(address, "Hello World", 4, transform=delta, endianness="little", encoding="utf-8")
```

More examples at [`strings.md`](/pycheevos/examples/strings.md)
