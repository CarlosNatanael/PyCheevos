# Project structure

```plaintext
pycheevos/
├── __init__.py
├── core/
│   ├── condition.py   # Individual condition logic
│   ├── constants.py   # Flags (PauseIf, ResetIf) and Sizes (8bit, 16bit)
│   ├── helpers.py     # Creation shortcuts (byte, word, delta, prior)
│   └── value.py       # Handles Addresses, Pointers, and Values
├── models/
│   ├── achievement.py # Achievement Class
│   ├── generic.py     # Base Class for Game Objects (OOP)
│   ├── leaderboard.py # Leaderboard Class
│   ├── rich_presence.py # Rich Presence Class
│   └── set.py         # Main grouper (Game ID, Title, Save)
└── utils/
    └── readme.md      # project structure
```