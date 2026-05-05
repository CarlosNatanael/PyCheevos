from typing import List, Union
from pycheevos.core.constants import MemorySize, MemoryType, Flag

class MemoryExpression:
    def __init__(self, start_term, start_flag=Flag.ADD_SOURCE): 
        self.terms = [(start_term, start_flag)]

    def _copy(self):
        new_expr = MemoryExpression(self.terms[0][0], self.terms[0][1])
        new_expr.terms = self.terms[:]
        return new_expr

    def __add__(self, other):
        new_expr = self._copy()
        new_expr.terms.append((other, Flag.ADD_SOURCE))
        return new_expr
    
    def __sub__(self, other):
        new_expr = self._copy()
        new_expr.terms.append((other, Flag.SUB_SOURCE))
        return new_expr 
    
    def __rshift__(self, other):
        new_expr = self._copy()
        last_term, _ = new_expr.terms.pop()
        new_expr.terms.append((last_term, Flag.ADD_ADDRESS))
        new_expr.terms.append((other, Flag.ADD_SOURCE))
        return new_expr
    

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

    def with_flag(self, flag: Flag):
        from .condition import Condition, ConditionList
        from .value import ConstantValue 
        
        optimized_terms = self.terms[:]
        
        if optimized_terms[-1][1] == Flag.SUB_SOURCE:
            for i in range(len(optimized_terms) - 2, -1, -1):
                if optimized_terms[i][1] == Flag.ADD_SOURCE:
                    positive_term = optimized_terms.pop(i)
                    optimized_terms.append(positive_term)
                    break

        conditions = []
        
        for i in range(len(optimized_terms) - 1):
            val, term_flag = optimized_terms[i]
            conditions.append(Condition(val, flag=term_flag))
        last_val, last_flag = optimized_terms[-1]
        
        if last_flag == Flag.SUB_SOURCE:
            conditions.append(Condition(last_val, flag=Flag.SUB_SOURCE))
            conditions.append(Condition(ConstantValue(0), flag=flag))
        else:
            conditions.append(Condition(last_val, flag=flag))
            
        return ConditionList(conditions)

    def _build_conditions(self, cmp: str, rvalue):
        from .condition import Condition, ConditionList
        from .value import ConstantValue
        
        optimized_terms = self.terms[:]
        
        if optimized_terms[-1][1] == Flag.SUB_SOURCE:
            for i in range(len(optimized_terms) - 2, -1, -1):
                if optimized_terms[i][1] == Flag.ADD_SOURCE:
                    positive_term = optimized_terms.pop(i)
                    optimized_terms.append(positive_term)
                    break
        
        conditions = []

        for i in range(len(optimized_terms) - 1):
            val, flag = optimized_terms[i]
            conditions.append(Condition(val, flag=flag))

        last_val, last_flag = optimized_terms[-1]
        
        if last_flag == Flag.SUB_SOURCE:
            conditions.append(Condition(last_val, flag=Flag.SUB_SOURCE))
            conditions.append(Condition(ConstantValue(0), cmp, rvalue))
        else:
            conditions.append(Condition(last_val, cmp=cmp, rvalue=rvalue))

        return ConditionList(conditions)
    
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
    
    @property
    def raw_address(self) -> int:
        return self.address
    
    def with_flag(self, flag: Flag):
        from .condition import Condition
        return Condition(self, flag=flag)

    def __rshift__(self, other):
        expr = MemoryExpression(self, start_flag=Flag.ADD_ADDRESS)
        expr.terms.append((other, Flag.ADD_SOURCE))
        return expr

    def __mul__(self, other):
        from .condition import Condition
        return Condition(self, "*", other)
    
    def __rmul__(self, other):
        return self.__mul__(other)

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
        return expr - other

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
        size_str = self.size.value

        if size_str == " ":
            size_str = ""

        if size_str.startswith('f'):
            return f"{self.mtype.value}{size_str}{hex_addr}"
        return f"{self.mtype.value}0x{size_str}{hex_addr}"
    
    def __str__(self):
        return self.render()
    
    def __repr__(self):
        return self.render()

class RecallValue(MemoryValue):
    def __init__(self):
        super().__init__(0, MemorySize.BIT8, MemoryType.RECALL)
    
    def render(self) -> str:
        return "{recall}"
    
    def __rshift__(self, other): # type: ignore
        from .condition import Condition, ConditionList
        # other is already a Condition or ConditionList — prepend recall as ADD_ADDRESS
        addr_condition = Condition(self, flag=Flag.ADD_ADDRESS)
        if isinstance(other, ConditionList):
            return ConditionList([addr_condition] + other)
        elif isinstance(other, Condition):
            return ConditionList([addr_condition, other])
        else:
            # fall back to base behaviour for MemoryValue chains
            return super().__rshift__(other)
    
    def __str__(self):
        return self.render()
    
    def __repr__(self):
        return self.render()

class ConstantValue:
    def __init__(self, value: Union[int, float]):
        self.value = value

    def render(self) -> str:
        if isinstance(self.value, float):
            return f"f{self.value}"
        return str(self.value)
    
    def delta(self): return self
    def prior(self): return self
    def bcd(self): return self
    
    def invert(self):
        if isinstance(self.value, int):
            return ConstantValue(~self.value)
        return self
    
    def with_flag(self, flag: Flag):
        from .condition import Condition
        return Condition(self, flag=flag)
    
    def __eq__(self, other): return self._cond("=", other) # type: ignore
    def __ne__(self, other): return self._cond("!=", other) # type: ignore
    def __gt__(self, other): return self._cond(">", other)
    def __ge__(self, other): return self._cond(">=", other)
    def __lt__(self, other): return self._cond("<", other)
    def __le__(self, other): return self._cond("<=", other)

    def _cond(self, cmp, other):
        from .condition import Condition
        return Condition(self, cmp, other)
    
    def __str__(self):
        return self.render()
    
    def __repr__(self):
        return self.render()
    
    def __mul__(self, other):
        from .condition import Condition
        return Condition(self, "*", other)

    def __rmul__(self, other):
        return self.__mul__(other)