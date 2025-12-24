from .constants import MemorySize, MemoryType

class MemoryValue:
    def __init__(self, address: int, size: MemorySize = MemorySize.BIT8, mtype: MemoryType = MemoryType.MEM):
        self.address = address
        self.size = size
        self.mtype = mtype

    def prior(self): return MemoryValue(self.address, self.size, MemoryType.PRIOR)
    def delta(self): return MemoryValue(self.address, self.size, MemoryType.DELTA)
    def bcd(self):   return MemoryValue(self.address, self.size, MemoryType.BCD)
    def invert(self):return MemoryValue(self.address, self.size, MemoryType.INVERT)

    def __eq__(self, other):return self._cond("=", other)
    def __ne__(self, other):return self._cond("!=", other)
    def __gt__(self, other):return self._cond(">", other)
    def __ge__(self, other):return self._cond(">=", other)
    def __lt__(self, other):return self._cond("<", other)
    def __le__(self, other):return self._cond("<=", other)

    def _cond(self, cmp, other):
        from .condition import Condition
        return Condition(self, cmp, other)

    def render(self) -> str:
        hex_addr = f"{self.address:04x}"
        if self.size.value.startswith('f') or self.size.value == 'K':
            return f"{self.mtype.value}{self.size.value}{hex_addr}"
        return f"{self.mtype.value}0x{self.size.value}{hex_addr}"
    
class ConstantValue:
    def __init__(self, value: int):
        self.value = value

    def render(self) -> str:
        return str(self.value)