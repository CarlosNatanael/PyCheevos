from typing import List, Union, Dict
from core.condition import Condition
from core.value import MemoryValue
from core.constants import LeaderboardFormat

class RichPresence:
    def __init__(self):
        self.lookups: Dict[str, Dict[int, str]] = {}
        self.displays: List[tuple] = []
    
    def add_lookup(self, name: str, value: Dict[int, str]):
        self.lookups[name] = value
        return self
    
    def add_display(self, condition: Union[str, Condition], text: str):
        if hasattr(condition, 'render'):
            cond_str = condition.render() # type: ignore
        else:
            cond_str = str(condition)
            
        self.displays.append((cond_str, text))
        return self
    
    def render(self) -> str:
        lines = []

        for name, values in self.lookups.items():
            lines.append(f"Lookup:{name}")
            for k, v in values.items():
                lines.append(f"{k}={v}")
            lines.append("")

        lines.append("Display:")
        for cond, text in self.displays:
            if not cond or cond == "True":
                lines.append(text)
            else:
                lines.append(f"?{cond}?{text}")
        
        return "\n".join(lines)
    
    @staticmethod
    def lookup(name: str, memory: MemoryValue) -> str:
        return f"@{name}(0x{memory.address:x})"
    
    @staticmethod
    def value(memory: MemoryValue, format: str = "VALUE") -> str:
        return f"@{format}(0x{memory.address:x})"