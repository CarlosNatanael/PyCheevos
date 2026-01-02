from .constants import Flag
from .value import MemoryValue, ConstantValue
from typing import Union, Optional

class Condition:
    def __init__(
            self,
            lvalue: Union[MemoryValue, ConstantValue, int, float],
            cmp: str = "=",
            rvalue: Optional[Union[MemoryValue, ConstantValue, int, float]] = None,
            flag: Flag = Flag.NONE,
            hits: int = 0
    ):
        if isinstance(lvalue, (int, float)): lvalue = ConstantValue(lvalue)
        if isinstance(rvalue, (int, float)): rvalue = ConstantValue(rvalue)

        self.lvalue = lvalue
        self.cmp = cmp
        self.rvalue = rvalue
        self.flag = flag
        self.hits = hits
    
    def _copy(self):
        return Condition(self.lvalue, self.cmp, self.rvalue, self.flag, self.hits)

    def with_hits(self, hits: int):
        new_cond = self._copy()
        new_cond.hits = hits
        return new_cond

    def with_flag(self, flag: Flag):
        new_cond = self._copy()
        new_cond.flag = flag
        return new_cond

    def _validate(self):        
        boolean_flags = [Flag.TRIGGER, Flag.RESET_IF, Flag.PAUSE_IF]

        if self.flag in boolean_flags:
            if self.rvalue is None:
                raise ValueError(
                    f"\nLOGIC ERROR DETECTED!\n"
                    f"The flag '{self.flag.name}' (Trigger/Reset/Pause) requires a comparison.\n"
                    f"You wrote something like: (memory).with_flag({self.flag.name})\n"
                    f"The correct way would be: (memoria != 0).with_flag({self.flag.name})\n"
                    f"Problematic address/value: {self.lvalue.render()}"
                )

    def render(self) -> str:

        self._validate() 

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