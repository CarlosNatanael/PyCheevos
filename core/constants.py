from enum import Enum
class MemorySize(Enum):
    BIT0        =   "M" # 0xM
    BIT1        =   "N" # 0xN   
    BIT2        =   "O" # 0xO
    BIT3        =   "P" # 0xP
    BIT4        =   "Q" # 0xQ
    BIT5        =   "R" # 0xR
    BIT6        =   "S" # 0xS
    BIT7        =   "T" # 0xT
    BIT8        =   "H" # 0xH
    BIT16       =   " " # 0x (Sem letra é 16-bit)
    BIT24       =   "W" # 0xW
    BIT32       =   "X" # 0xX
    BIT16_RE    =   "I" # Big Endian
    BIT24_RE    =   "J" 
    BIT32_RE    =   "G" 
    LOWER4      =   "L" # 0xL
    UPPER4      =   "U" # 0xU

class MemoryType(Enum):
    MEM     = ""
    DELTA   = "d"
    PRIOR   = "p"
    BCD     = "b"
    INVERT  = "~"

class Flag(Enum):
    NONE              = ""
    PAUSE_IF          = "P:"
    RESET_IF          = "R:"
    RESET_NEXT_IF     = "Z:"
    ADD_HITS          = "C:"
    SUB_HITS          = "B:"
    ADD_SOURCE        = "A:"
    SUB_SOURCE        = "B:"
    ADD_ADRESS        = "I:"
    MEASURED          = "M:"
    TRIGGER           = "T:"
    AND_NEXT          = "N:"
    OR_NETX           = "O:"
    MEASURED_PRECENT  = "G:"
    MEASURED_IF       = "Q:"
    REMEMBER          = "K:"
