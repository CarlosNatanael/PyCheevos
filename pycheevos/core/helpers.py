from typing import Callable, Literal, Union

from pycheevos.core.value import MemoryValue, RecallValue, ConstantValue
from pycheevos.core.constants import MemorySize, Flag
from pycheevos.core.condition import Condition, ConditionList

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

def float32(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.FLOAT)
def float32_be(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.FLOAT_BE)

def mbf32(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.MBF32)
def mbf32_le(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.MBF32_LE)

def double32(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.DOUBLE32)
def double32_be(address: int) -> MemoryValue: return MemoryValue(address, MemorySize.DOUBLE32_BE)


def prior(mem: MemoryValue) -> MemoryValue: return mem.prior()
def delta(mem: MemoryValue) -> MemoryValue: return mem.delta()
def bcd(mem: MemoryValue) -> MemoryValue:   return mem.bcd()
def invert(mem: MemoryValue) -> MemoryValue: return mem.invert()

def recall() -> RecallValue: return RecallValue()

def value(value: int) -> ConstantValue: return ConstantValue(value)

def group(*args) -> ConditionList: return ConditionList(args)

def always_true() -> Condition: return value(1) == value(1)
def always_false() -> Condition: return value(0) == value(1)

# --- New Flag Helper Functions ---
def pause_if(condition):         return condition.with_flag(Flag.PAUSE_IF)
def reset_if(condition):         return condition.with_flag(Flag.RESET_IF)
def reset_next_if(condition):    return condition.with_flag(Flag.RESET_NEXT_IF)
def add_hits(condition):         return condition.with_flag(Flag.ADD_HITS)
def sub_hits(condition):         return condition.with_flag(Flag.SUB_HITS)
def add_source(condition):       return condition.with_flag(Flag.ADD_SOURCE)
def sub_source(condition):       return condition.with_flag(Flag.SUB_SOURCE)
def add_address(condition):      return condition.with_flag(Flag.ADD_ADDRESS)
def measured(condition):         return condition.with_flag(Flag.MEASURED)
def measured_if(condition):      return condition.with_flag(Flag.MEASURED_IF)
def trigger(condition):          return condition.with_flag(Flag.TRIGGER)
def remember(condition):         return condition.with_flag(Flag.REMEMBER)
def and_next(condition):         return condition.with_flag(Flag.AND_NEXT)
def or_next(condition):          return condition.with_flag(Flag.OR_NEXT)
def measured_percent(condition): return condition.with_flag(Flag.MEASURED_PERCENT)

def string_equals(
    address: int,
    string: str,
    length: int = 0,
    transform: Union[Callable, None] = None,
    encoding: str = "ascii",
    endianness: Literal["little", "big"] = "big"
) -> ConditionList:
    conditions = ConditionList()
    if length == 0:
        b = string.encode(encoding)
        length = len(b)
    else:
        b = string.encode(encoding)[:length]
    for i in range(0, length, 4):
        chunk = b[i: i + 4]
        size = {
            "little": {
                1: byte,
                2: word,
                3: tbyte,
                4: dword,
            },
            "big": {
                1: byte,
                2: word_be,
                3: tbyte_be,
                4: dword_be,
            }
        }[endianness][len(chunk)]
        lvalue = size(address + i)
        if transform is not None:
            lvalue = transform(lvalue)
        rvalue = value(int.from_bytes(chunk, byteorder=endianness))
        conditions.append(and_next(lvalue == rvalue))
    conditions = conditions.with_flag(Flag.NONE)
    return conditions
