from pycheevos.core.condition import Condition
from pycheevos.core.constants import MemoryType, MemorySize
from pycheevos.core.helpers import Flag
from pycheevos.core.value import MemoryValue, RecallValue, ConstantValue
from tabulate import tabulate

FLAG_MAPPING = {
    Flag.NONE: "",
    Flag.PAUSE_IF: "PauseIf",
    Flag.RESET_IF: "ResetIf",
    Flag.RESET_NEXT_IF: "ResetNextIf",
    Flag.ADD_HITS: "AddHits",
    Flag.SUB_HITS: "SubHits",
    Flag.ADD_SOURCE: "AddSource",
    Flag.SUB_SOURCE: "SubSource",
    Flag.ADD_ADDRESS: "AddAddress",
    Flag.MEASURED: "Measured",
    Flag.TRIGGER: "Trigger",
    Flag.AND_NEXT: "AndNext",
    Flag.OR_NEXT: "OrNext",
    Flag.MEASURED_PERCENT: "Measured%",
    Flag.MEASURED_IF: "MeasuredIf",
    Flag.REMEMBER: "Remember",
}

SIZE_MAPPING = {
    MemorySize.BIT0: "Bit0",
    MemorySize.BIT1: "Bit1",
    MemorySize.BIT2: "Bit2",
    MemorySize.BIT3: "Bit3",
    MemorySize.BIT4: "Bit4",
    MemorySize.BIT5: "Bit5",
    MemorySize.BIT6: "Bit6",
    MemorySize.BIT7: "Bit7",
    MemorySize.BIT8: "8-bit",
    MemorySize.BIT16: "16-bit",
    MemorySize.BIT24: "24-bit",
    MemorySize.BIT32: "32-bit",
    MemorySize.BIT16_BE: "16-bit BE",
    MemorySize.BIT24_BE: "24-bit BE",
    MemorySize.BIT32_BE: "32-bit BE",
    MemorySize.LOWER4: "Lower4",
    MemorySize.UPPER4: "Upper4",
    MemorySize.BITCOUNT: "Bitcount",
    MemorySize.FLOAT: "Float",
    MemorySize.FLOAT_BE: "Float BE",
    MemorySize.DOUBLE32: "Double32",
    MemorySize.DOUBLE32_BE: "Double32 BE",
    MemorySize.MBF32: "MBF32",
    MemorySize.MBF32_LE: "MBF32 LE",
}

TYPE_MAPPING = {
    MemoryType.MEM: "Mem",
    MemoryType.DELTA: "Delta",
    MemoryType.PRIOR: "Prior",
    MemoryType.INVERT: "Invert",
    MemoryType.BCD: "BCD",
    MemoryType.RECALL: "Recall",
}

def format_type(value: MemoryValue | ConstantValue | RecallValue | None):
    if isinstance(value, ConstantValue):
        return "Value"
    elif isinstance(value, RecallValue):
        return "Recall"
    elif isinstance(value, MemoryValue):
        return TYPE_MAPPING[value.mtype]
    else:
        ""

def format_size(value: MemoryValue | ConstantValue | RecallValue | None):
    if isinstance(value, MemoryValue):
        return SIZE_MAPPING[value.size]
    else:
        return ""
    
def format_value(value: MemoryValue | ConstantValue | RecallValue | None):
    if isinstance(value, ConstantValue):
        if isinstance(value.value, float):
            return f"{value.value:.3f}f"
        return hex(value.value)
    elif isinstance(value, RecallValue):
        return "{recall}"
    elif isinstance(value, MemoryValue):
        return hex(value.address)
    else:
        ""

def format_hits(hits: int):
    if hits == 0:
        return ""
    return f"({hits})"

def format_markdown(logic: list[Condition]):
    data = [
        {
            "#": i + 1,
            "Flag": FLAG_MAPPING[cond.flag],
            "LType": format_type(cond.lvalue),
            "LSize": format_size(cond.lvalue),
            "LValue": format_value(cond.lvalue),
            "Op": cond.cmp,
            "RType": format_type(cond.rvalue),
            "RSize": format_size(cond.rvalue),
            "RValue": format_value(cond.rvalue),
            "Hits": format_hits(cond.hits)
        }
        for i, cond in enumerate(logic)
    ]
    return tabulate(
        data,
        tablefmt="pipe",
        headers="keys",
    )

def display_markdown(logic: list[Condition]):
    print(format_markdown(logic))
    print()
