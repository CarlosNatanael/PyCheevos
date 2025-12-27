from typing import List, Union
from .constants import MemorySize, MemoryType, Flag

class MemoryExpression:
    def __init__(self, start_term, start_flag=Flag.ADD_SOURCE): 
        self.terms = [(start_term, start_flag)]

    def __add__(self, other):
        self.terms.append((other, Flag.ADD_SOURCE))
        return self
    
    def __sub__(self, other):
        self.terms.append((other, Flag.SUB_SOURCE))
        return self
    
    def __rshift__(self, other):
        last_term, _ = self.terms.pop()
        self.terms.append((last_term, Flag.ADD_ADDRESS))
        self.terms.append((other, Flag.ADD_SOURCE))
        return self

    def _apply_modifier(self, method_name):
        new_expr = MemoryExpression(self.terms[0][0], self.terms[0][1])
        new_expr.terms = self.terms[:-1]
        
        last_val, last_flag = self.terms[-1]
        if hasattr(last_val, method_name):
            new_val = getattr(last_val, method_name)()
            new_expr.terms.append((new_val, last_flag))
        else:
            new_expr.terms.append((last_val, last_flag))
            
        return new_expr

    def delta(self): return self._apply_modifier("delta")
    def prior(self): return self._apply_modifier("prior")
    def bcd(self):   return self._apply_modifier("bcd")

    def _build_conditions(self, cmp: str, rvalue) -> List:
        from .condition import Condition
        from .value import ConstantValue

        conditions = []

        for i in range(len(self.terms) - 1):
            val, flag = self.terms[i]
            conditions.append(Condition(val, flag=flag))

        last_val, last_flag = self.terms[-1]
        
        if last_flag == Flag.SUB_SOURCE:
            conditions.append(Condition(last_val, flag=Flag.SUB_SOURCE))
            conditions.append(Condition(ConstantValue(0), cmp, rvalue))
        else:
            conditions.append(Condition(last_val, cmp=cmp, rvalue=rvalue))

        return conditions
    
    def __eq__(self, other): return self._build_conditions("=", other) # type: ignore[override]
    def __ne__(self, other): return self._build_conditions("!=", other) # type: ignore[override]
    def __gt__(self, other): return self._build_conditions(">", other)
    def __ge__(self, other): return self._build_conditions(">=", other)
    def __lt__(self, other): return self._build_conditions("<", other)
    def __le__(self, other): return self._build_conditions("<=", other)

class MemoryValue:
    def __init__(self, address: int, size: MemorySize = MemorySize.BIT8, mtype: MemoryType = MemoryType.MEM):
        self.address = address
        self.size = size
        self.mtype = mtype

    def __rshift__(self, other):
        expr = MemoryExpression(self, start_flag=Flag.ADD_ADDRESS)
        expr.terms.append((other, Flag.ADD_SOURCE))
        return expr

    def __mul__(self, other):
        from .condition import Condition
        return Condition(self, "*", other)

    def __truediv__(self, other):
        from .condition import Condition
        return Condition(self, "/", other)

    def __mod__(self, other):
        from .condition import Condition
        return Condition(self, "%", other)

    def __and__(self, other):
        from .condition import Condition
        return Condition(self, "&", other)
    
    def __xor__(self, other):
        from .condition import Condition
        return Condition(self, "^", other)

    def __add__(self, other):
        expr = MemoryExpression(self)
        return expr + other
    
    def __sub__(self, other):
        expr = MemoryExpression(self) 
        return expr + other

    def prior(self): return MemoryValue(self.address, self.size, MemoryType.PRIOR)
    def delta(self): return MemoryValue(self.address, self.size, MemoryType.DELTA)
    def bcd(self):   return MemoryValue(self.address, self.size, MemoryType.BCD)
    def invert(self):return MemoryValue(self.address, self.size, MemoryType.INVERT)

    def __eq__(self, other):return self._cond("=", other) # type: ignore[override]
    def __ne__(self, other):return self._cond("!=", other) # type: ignore[override]
    def __gt__(self, other):return self._cond(">", other)
    def __ge__(self, other):return self._cond(">=", other)
    def __lt__(self, other):return self._cond("<", other)
    def __le__(self, other):return self._cond("<=", other)

    def _cond(self, cmp, other):
        from .condition import Condition
        return Condition(self, cmp, other)

    def render(self) -> str:
        if self.mtype == MemoryType.RECALL:
            return "{recall}"

        hex_addr = f"{self.address:04x}"
        
        if self.size.value.startswith('f') or self.size.value == 'K':
            return f"{self.mtype.value}{self.size.value}{hex_addr}"
        
        return f"{self.mtype.value}0x{self.size.value}{hex_addr}"

class RecallValue(MemoryValue):
    def __init__(self):
        super().__init__(0, MemorySize.BIT8, MemoryType.RECALL)
class ConstantValue:
    def __init__(self, value: int):
        self.value = value
    def render(self) -> str:
        return str(self.value)