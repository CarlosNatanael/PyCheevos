from .constants import Flag
from .value import MemoryValue, ConstantValue
from typing import Union

class Condition:
    def __init__(
            self,
            lvalue: Union[MemoryValue, ConstantValue],
            cmp: str = "=",
            rvalue: Union[MemoryValue, ConstantValue] = None,
            flag: Flag = Flag.NONE,
            hits: int = 0
    ):
        self.lvalue = lvalue
        self.cmp = cmp
        self.rvalue = rvalue
        self.flag = flag
        self.hits = hits
    
    def render(self) -> str:
        """Gera a string final que o RA entende"""
        
        parts = [self.flag.value]
        parts.append(self.lvalue.render())
        if self.rvalue:
            parts.append(self.cmp)
            parts.append(self.rvalue.render())

        if self.hits > 0:
            parts.append(f".{self.hits}.")
        
        return "".join(parts)
    
    def __str__(self):
        return self.render()