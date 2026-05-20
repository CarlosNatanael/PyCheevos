from typing import List, Union, Dict, Optional
from pathlib import Path
from pycheevos.core.condition import Condition
from pycheevos.core.value import MemoryValue
from pycheevos.core.constants import LeaderboardFormat

class RichPresence:
    def __init__(self):
        self.lookups: Dict[str, Dict[Union[int, str], str]] = {}
        self.formats: Dict[str, str] = {}
        self.displays: List[tuple] = []
    
    def add_lookup(self, name: str, values: Dict[Union[int, tuple, list], str], default: Optional[str] = None):
        clean_dict = {}
        for key, label in values.items():
            if isinstance(key, (tuple, list)):
                for k in key:
                    clean_dict[k] = label
            else:
                clean_dict[key] = label
        
        if default is not None:
            clean_dict["*"] = default
        
        self.lookups[name] = clean_dict
        return self

    def add_format(self, name: str, format_type: str = "VALUE"):
        self.formats[name] = format_type
        return self
    
    def add_display(self, condition: Optional[Union[str, Condition, list]], text: str):
        if condition is None:
            cond_str = ""
        elif isinstance(condition, list):
            cond_str = "_".join([c.render() if hasattr(c, 'render') else str(c) for c in condition])
        elif hasattr(condition, 'render'):
            cond_str = condition.render() # type: ignore
        else:
            cond_str = str(condition)
            
        self.displays.append((cond_str, text))
        return self
    
    def render(self) -> str:
        lines = []

        # 1. Formats
        for name, fmt in self.formats.items():
            lines.append(f"Format:{name}")
            lines.append(f"FormatType={fmt}")
            lines.append("")

        # 2. Lookups
        for name, values in self.lookups.items():
            lines.append(f"Lookup:{name}")
            keys = [k for k in values.keys() if k != "*"]
            numeric_keys = sorted([k for k in keys if isinstance(k, int)])
            string_keys = sorted([k for k in keys if not isinstance(k, int)])
            
            sorted_keys = numeric_keys + string_keys
            
            for k in sorted_keys:
                key_str = f"0x{k:x}" if isinstance(k, int) else str(k)
                lines.append(f"{key_str}={values[k]}")
            
            if "*" in values:
                lines.append(f"*={values['*']}")
            lines.append("")

        # 3. Displays
        lines.append("Display:")
        
        conditional_displays = [d for d in self.displays if d[0]]
        default_display = [d for d in self.displays if not d[0]]

        for cond, text in conditional_displays:
            lines.append(f"?{cond}?{text}")
        
        for _, text in default_display:
            lines.append(text)
        
        return "\n".join(lines)
    
    def save(self, game_id: int, title: str = "Rich Presence", path: Optional[str] = None):
        if path is None:
            root = Path.cwd()
            output = root / "output" / f"{title} - {game_id}"
        else:
            output = Path(path)

        output.mkdir(parents=True, exist_ok=True)
        rp_file = output / f"{game_id}-Rich.txt"
        
        with open(rp_file, "w", encoding="utf-8") as f:
            f.write(self.render())
        
        print(f"Generated Rich Presence file: {rp_file}")

    def __str__(self):
        return self.render()
    
    def __repr__(self):
        return self.render()

    @staticmethod
    def lookup(name: str, memory) -> str:
        if isinstance(memory, str):
            return f"@{name}({memory})"
        return f"@{name}({memory.render()})"

    @staticmethod
    def value(memory, format_type: str = "VALUE") -> str:
        if isinstance(memory, str):
            return f"@{format_type}({memory})"
        return f"@{format_type}({memory.render()})"