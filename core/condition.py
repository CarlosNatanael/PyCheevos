from .constants import Flag
from .value import MemoryValue, ConstantValue
from typing import Union, Optional

class Condition:
    def __init__(
            self,
            lvalue: Union[MemoryValue, ConstantValue, int],
            cmp: str = "=",
            rvalue: Optional[Union[MemoryValue, ConstantValue, int]] = None,
            flag: Flag = Flag.NONE,
            hits: int = 0
    ):
        if isinstance(lvalue, int): lvalue = ConstantValue(lvalue)
        if isinstance(rvalue, int): rvalue = ConstantValue(rvalue)

        self.lvalue = lvalue
        self.cmp = cmp
        self.rvalue = rvalue
        self.flag = flag
        self.hits = hits
    
    def with_hits(self, hits: int):
        self.hits = hits
        return self

    def with_flag(self, flag: Flag):
        self.flag = flag
        return self

    def render(self) -> str:
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