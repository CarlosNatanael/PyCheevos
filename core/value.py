from .constants import MemorySize

class MemoryValue:
    def __init__(self, address: int, size: MemorySize = MemorySize.BIT8):
        self.address = address
        self.size = size

    def render(self) -> str:
        # Formata o endereço em hexadecimal em caixa baixa sem o '0x' inicial
        hex_addr = f"{self.address:04x}"
        return f"0x{self.size.value}{hex_addr}"
    
class ConstantValue:
    def __init__(self, value: int):
        self.value = value

    def render(self) -> str:
        # apenas retorna o numero de string
        return str(self.value)