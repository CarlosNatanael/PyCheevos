from .value import MemoryValue, RecallValue
from .constants import MemorySize

def byte(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT8)
def word(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT16)
def tbyte(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT24)
def dword(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT32)
def bit0(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT0)
def bit1(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT1)
def bit2(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT2)
def bit3(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT3)
def bit4(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT4)
def bit5(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT5)
def bit6(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT6)
def bit7(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT7)
def low4(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.LOWER4)
def high4(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.UPPER4)
def bitcount(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BITCOUNT)

def word_be(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT16_BE)
def tbyte_be(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT24_BE)
def dword_be(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.BIT32_BE)

def float(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.FLOAT)
def float_be(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.FLOAT_BE)

def mbf32(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.MBF32)
def mbf32_le(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.MBF32_LE)

def double32(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.DOUBLE32)
def double32_be(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.DOUBLE32_BE)


def prior(mem: MemoryValue) -> MemoryValue: return mem.prior()
def delta(mem: MemoryValue) -> MemoryValue: return mem.delta()
def bcd(mem: MemoryValue) -> MemoryValue:   return mem.bcd()
def invert(mem: MemoryValue) -> MemoryValue: return mem.invert()

def recall() -> RecallValue: return RecallValue()