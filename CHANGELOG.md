# Changelog
## [0.0.8] - 20/05/2026

### Added
- **Markdown Documentation Generator:**
    - Added option `[6] Export Achievements to Markdown (Documentation)` to the CLI Importer (`pycheevos-import`).
    - This feature automatically loads generated Python scripts and exports fully formatted, highly readable Markdown tables (`README_[ID].md`) representing the entire `Core` and `Alts` logic structure of a set.
- **New Functional Helpers (PR #18):**
    - Added `always_true()` and `always_false()` logic constants.
    - Added `group()` as a functional shortcut to instantiate a `ConditionList`.
    - Added `string_equals()` helper to handle byte-by-byte string comparison in memory, automatically managing character encoding (e.g., UTF-8, Shift-JIS) and endianness for modern consoles.

### Changed
- **Rich Presence Upgrade (Fixes #19):**
    - Refactored `RichPresence.add_lookup` to natively accept grouped `tuple` and `range` objects as dictionary keys instead of flattening them prematurely.
    - Optimized `RichPresence.render()` to dynamically detect grouped keys and output RetroAchievements' shortened lookup syntax (e.g., `0x4,0x8,0xc=Label` and inclusive ranges like `0x100-0x1ff=Label`).
- **ConditionList Enhancement (PR #18):**
    - Implemented a native `render()` method inside `ConditionList`, unlocking clean integration with Python f-strings for formatting complex condition chains inside Rich Presence displays.

### Fixed
- **Type Hinting (PR #18):** Fixed multiple structural type errors in `value.py` to improve linter compatibility and core predictability.
- **Markdown Logic Rendering:** Fixed `markdown.py` missing explicit return statements in mapping fallback conditions to avoid implicit `None` boundaries inside `tabulate`.
---

## [0.0.7] - 17/02/2026

### Added
- **Documentation Tool:**
    - Added a new option `[5] Dump Code Notes to TXT` to the CLI Importer (`pycheevos-import`).
    - This tool exports formatted, readable text files of Code Notes to a `notes_dump/` folder for offline reference.
    - Uses the "Smart Sync" logic to automatically choose the most recent notes between Local files and the RA Server.
- **Rich Presence Upgrade:**
    - Added `add_format(name, type)` method to easily register value formats (e.g., Money, Points).
    - Added `default` parameter to `add_lookup` to streamline defining fallback values (`*`).
    - Implemented `__str__` and `__repr__` methods, allowing users to simply `print(rp)` to see the generated script output.

### Changed
- **Importer Architecture:** Modularized `import_notes.py` to expose synchronization logic (`get_best_notes`), allowing the new Dump tool to reuse the connection and comparison strategies.
- **Rich Presence Rendering:** Improved the sorting logic for Lookups in the generated output. It now prioritizes Numeric keys, followed by String keys, ensuring the Default key (`*`) is always placed at the end.

---

## [0.0.6] - 26/01/2026

### Added
- **Leaderboards Upgrade:**
    - Added support for **Alt Groups** in Leaderboards logic (Start, Cancel, Submit, Value). The `set_*` methods now accept multiple arguments (`core, alt1, alt2...`).
    - The Importer now correctly parses and generates Python code for Leaderboards with multiple condition groups (separated by `S`).
- **Leaderboard Formats:** Added explicit mapping for RA formats (e.g., `TIME` -> `FRAMES`) to ensure valid enum generation in imported scripts.

### Fixed
- **RecallValue Bug:** Fixed `RecallValue` (and `MemoryValue` of type `RECALL`) rendering as `"0"` instead of `"{recall}"`, which broke memory logic dependent on remembered values. (Fixes #12)
- **Subtraction Operator:** Corrected a typo in `MemoryValue.__sub__` where the subtraction operator (`-`) was incorrectly performing addition (`+`). (Fixes #13)
- **Logic Optimization:** Implemented intelligent operand reordering in `MemoryExpression`. Subtractions (`A - B`) are now automatically reordered to `SubSource B`, `AddSource A` to avoid generating redundant `0 == Target` conditions.
- **Remember Logic:** Fixed `remember()` helper incorrectly converting subtractions into additions. It now properly handles negative terms by reordering or appending a zero-check where necessary.

---

## [0.0.5] - 15/01/2026

### Added
- **Command Line Interface:** Added `pycheevos-import` command for quick access to the importer tools from any directory.
- **Smart Importer:** Introduced a unified import flow (Option 3) that downloads notes and generates achievement scripts using variable names (e.g., `health == 0x04`) instead of raw addresses.
    - Automatic mapping of Code Notes to Python variables.
    - Integer constants in generated scripts now use Hexadecimal formatting (e.g., `0x10`) for better readability.
- **Rich Presence Improvements:**
    - `add_lookup`: Now supports tuples/lists as keys (e.g., `{(1, 2): "Level A"}`).
    - `add_display`: Now supports `ConditionList` and complex logic chains (joined automatically by `_`).
    - `save()`: Added method to save Rich Presence scripts independently of the Achievement Set.
    - `f-strings`: Enabled f-string formatting for memory objects (e.g., `f"Score: @VALUE({mem_score})"`) by implementing `__str__` and `__repr__`.
- **Core Safety:** Added safe modifier methods (`delta`, `prior`, `bcd`, `invert`) to `ConstantValue`. This prevents crashes in generated scripts when modifiers are applied to constant numbers (e.g., `value(0).delta()`).

### Changed
- **Refactor:** Unified `ConditionList` logic into `core/condition.py`, resolving circular dependency issues between `value.py` and `condition.py`.
- **Importer Output:** Generated scripts now save to the user's current working directory (`os.getcwd()`) instead of the library installation folder.
- **Dependency:** Updated `project.scripts` in `pyproject.toml` to expose the CLI tool.

---

## [0.0.4] - 12/01/2026
### Fixed
- **Pip Installation:** Fixed `ModuleNotFoundError` when using the library installed via pip. Internal imports in `models` were converted to absolute paths (`from pycheevos.core...`) to ensure correct resolution.
- **Note Parser:** Fixed an issue where literal `\r\n` escape sequences in note files were not parsed correctly, causing malformed variable names and merged comments.
- **Wildcard Imports:** Removed unsafe wildcard imports (`import *`) from internal modules to improve code safety and linter compatibility.

### Changed
- **Variable Naming:** Improved conflict resolution in `import_notes`. Duplicate variable names now use a clean sequential counter (e.g., `health_2`) instead of appending raw memory addresses.

### Added
- **Documentation:** Added an `Installation` section to the README with specific instructions for `pip` and how to execute utility scripts using the `python -m` module flag.

---

## [0.0.3] - 11/01/2026

### Added
- **Helper Functions:** Added functional helpers for flags in `core.helpers` (e.g., `reset_if()`, `measured()`, `pause_if()`) for cleaner syntax.
- **AchievementType:** Added `AchievementType` Enum in `core.constants` (`PROGRESSION`, `WIN_CONDITION`, `MISSABLE`) to support achievement classification.
- **Logical Operators:** Added explicit support for `and_next()` and `or_next()` helpers, alongside pythonic `&` and `|` operators.

### Fixed
- **Emulator Parsing Error:** Fixed `User.txt` generation where titles containing colons (`:`) would break the parser. Titles and descriptions are now quoted.
- **Memory Formatting:**
    - Fixed extra space in Word addresses (`0x 1234` -> `0x1234`).
    - Fixed invalid `0x` prefix appearing on Float (`fF`) and Bitcount (`K`) memory types.
- **Recall Logic:** Fixed `RecallValue` rendering `{recall}` string instead of `0`, which caused emulator syntax errors.

### Changed
- **Breaking Change:** Removed lowercase flag constants (e.g., `reset_if`) from `core.constants` to avoid naming conflicts with the new helper functions. Please use the new functions or the uppercase constants (`Flag.RESET_IF`).

---

## [0.0.2] - 08/01/2026

**Hybrid Importers, Logical Operators, and Security Improvements**

This update brings a complete overhaul to the import tools, making them hybrid (Local + Server). It also introduces a new fluent syntax for creating achievement logic and strengthens type safety in the Core.

### New Features (Core)

##### **Logical Operators (`ConditionList`):**
* It's now possible to chain conditions using native Python operators:
    * `&` (AND) generates the `AND_NEXT` flag.
    * `|` (OR) generates the `OR_NEXT` flag.
    * `~` (NOT) inverts comparison logic and toggles flags.
* Implemented in `core/condition.py`.

##### **Helper `value()`:**
* New helper to encapsulate numeric constants, preventing Python from prematurely resolving comparisons (e.g., `0 == 0` becoming `True`).
* Added to `core/helpers.py` and `core/value.py`.

##### **Logic Validation:**
* The `render()` method now prevents generating broken scripts if it detects flags like `Trigger`, `Reset`, or `Pause` without a valid comparison.

### Import Tools (Utils)

##### **Hybrid System (Local + Cloud):**
* `import_notes.py` and `import_achievements.py` now first search for local files (`.txt`/`.json`). If not found, they connect to the RetroAchievements server (with secure login and credential caching) to download the data.

##### **Notes Importer (`import_notes.py`):**
* **Pointer Generation:** Detects offset hierarchy (`+`, `++`) in notes and automatically generates the pointer logic (`AddAddress`).
* **Sanitization:** Automatic cleanup of variable names to ensure valid Python syntax.

##### **Achievements Importer (`import_achievements.py`):**
* **Robust Parser:** Enhanced support for Bitmasks (converts `addr&mask` to Hexadecimal) and Floats.
* **Smart Translation:** Automatically converts "loose" numbers to `value()` and applies flags correctly.
* Fixes empty address syntax errors (`0x` -> `0x0`).

### Bug Fixes

* Fixed `Achievement._flatten` to support nested lists (resolving the need to use `*` excessively).
* Fixed the value parser to avoid confusing numeric inputs with memory types (Word).
