from .constants import MemorySize, MemoryType

class MemoryValue:
    def __init__(self, address: int, size: MemorySize = MemorySize.BIT8, mtype: MemoryType = MemoryType.MEM):
        self.address = address
        self.size = size
        self.mtype = mtype

    def prior(self):
        return MemoryValue(self.address, self.size, MemoryType.PRIOR)
    
    def delta(self):
        return MemoryValue(self.address, self.size, MemoryType.DELTA)
    
    def bcd(self):
        return MemoryValue(self.address, self.size, MemoryType.BCD)

    def __eq__(self, other):
        from .condition import Condition
        return Condition(self, "=", other)
    
    def __ne__(self, other):
        from .condition import Condition
        return Condition(self, "!=", other)
    
    def __gt__(self, other):
        from .condition import Condition
        return Condition(self, ">", other)
    
    def __ge__(self, other):
        from .condition import Condition
        return Condition(self, ">=", other)
    
    def __lt__(self, other):
        from .condition import Condition
        return Condition(self, "<", other)
    
    def __le__(self, other):
        from .condition import Condition
        return Condition(self, "<=", other)

    def render(self) -> str:
        hex_addr = f"{self.address:04x}"
        return f"{self.mtype.value}0x{self.size.value}{hex_addr}"
    
class ConstantValue:
    def __init__(self, value: int):
        self.value = value

    def render(self) -> str:
        return str(self.value)