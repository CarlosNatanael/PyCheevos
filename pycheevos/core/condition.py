from pycheevos.core.constants import Flag
from pycheevos.core.value import MemoryValue, ConstantValue
from typing import Union, Optional

INVERT_MAP = {
    '=': '!=', '!=': '=',
    '<': '>=', '>=': '<',
    '>': '<=', '<=': '>'
}

class ConditionList(list):
    def __init__(self, items=None):
        super().__init__(items or [])

    def __and__(self, other):
        if self:
            self[-1] = self[-1].with_flag(Flag.AND_NEXT)

        if isinstance(other, ConditionList):
            self.extend(other)
        elif isinstance(other, Condition):
            self.append(other)
        return self
    
    def __or__(self, other):
        if self:
            self[-1] = self[-1].with_flag(Flag.OR_NEXT)
        
        if isinstance(other, ConditionList):
            self.extend(other)
        elif isinstance(other, Condition):
            self.append(other)
        return self
    
    def __invert__(self):
        new_list = ConditionList()
        for i, cond in enumerate(self):
            inv_cond = ~cond

            if inv_cond.flag == Flag.AND_NEXT:
                inv_cond = inv_cond.with_flag(Flag.OR_NEXT)
            elif inv_cond.flag == Flag.OR_NEXT:
                inv_cond = inv_cond.with_flag(Flag.AND_NEXT)

            new_list.append(inv_cond)
        return new_list
    
    def with_flag(self, flag: Flag):
        if self:
            self[-1] = self[-1].with_flag(flag)
        return self

    def with_hits(self, hits: int):
        if self:
            self[-1] = self[-1].with_hits(hits)
        return self

    def render(self) -> str:
        return "_".join(map(str, self))
    
    def __str__(self):
        return self.render()
    
    def __repr__(self):
        return self.render()


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
    
    def __invert__(self):
        new_cmp = INVERT_MAP.get(self.cmp, self.cmp)
        return Condition(self.lvalue, new_cmp, self.rvalue, self.flag, self.hits)
    
    def __and__(self, other):
        cl = self.with_flag(Flag.AND_NEXT)
        return ConditionList([cl, other])
    
    def __or__(self, other):
        cl = self.with_flag(Flag.OR_NEXT)
        return ConditionList([cl, other])

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
    
    def __repr__(self):
        return self.render()
    
    def __rshift__(self, other):
        from pycheevos.core.value import MemoryExpression
        from pycheevos.core.constants import Flag
        
        expr = MemoryExpression(self, start_flag=Flag.ADD_ADDRESS)
        expr.terms.append((other, Flag.ADD_SOURCE))
        return expr