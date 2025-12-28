from enum import Enum
class MemorySize(Enum):
    BIT0        =   "M"
    BIT1        =   "N"
    BIT2        =   "O"
    BIT3        =   "P"
    BIT4        =   "Q"
    BIT5        =   "R"
    BIT6        =   "S"
    BIT7        =   "T"
    BIT8        =   "H"
    BIT16       =   " "
    BIT24       =   "W"
    BIT32       =   "X"
    BIT16_BE    =   "I"
    BIT24_BE    =   "J"
    BIT32_BE    =   "G"
    LOWER4      =   "L"
    UPPER4      =   "U"
    BITCOUNT    =   "K"
    FLOAT       =   "fF"
    FLOAT_BE    =   "fB"
    DOUBLE32    =   "fH"
    DOUBLE32_BE =   "fI"
    MBF32       =   "fM"
    MBF32_LE    =   "fL"

class MemoryType(Enum):
    MEM     = ""
    DELTA   = "d"
    PRIOR   = "p"
    BCD     = "b"
    INVERT  = "~"
    RECALL  = "{recall}"

class Flag(Enum):
    NONE              = ""
    PAUSE_IF          = "P:"
    RESET_IF          = "R:"
    RESET_NEXT_IF     = "Z:"
    ADD_HITS          = "C:"
    SUB_HITS          = "D:"
    ADD_SOURCE        = "A:"
    SUB_SOURCE        = "B:"
    ADD_ADDRESS       = "I:"
    MEASURED          = "M:"
    TRIGGER           = "T:"
    AND_NEXT          = "N:"
    OR_NEXT           = "O:"
    MEASURED_PERCENT  = "G:"
    MEASURED_IF       = "Q:"
    REMEMBER          = "K:"

class LeaderboardFormat(Enum):
    SCORE           = "SCORE"
    FRAMES          = "FRAMES"
    MILLISECS       = "MILLISECS"
    SECS            = "SECS"
    MINUTES         = "MINUTES"
    SECS_AS_MINS    = "SECS_AS_MINS"
    VALUE           = "VALUE"
    UNSIGNED        = "UNSIGNED"
    TENS            = "TENS"
    HUNDREDS        = "HUNDREDS"
    THOUSANDS       = "THOUSANDS"
    FIXED1          = "FIXED1"
    FIXED2          = "FIXED2"
    FIXED3          = "FIXED3"
    FLOAT1          = "FLOAT1"
    FLOAT2          = "FLOAT2"
    FLOAT3          = "FLOAT3"
    FLOAT4          = "FLOAT4"
    FLOAT5          = "FLOAT5"
    FLOAT6          = "FLOAT6"



# EXPORTING FLAGS (UPPERCASE - Constants Style)

NONE              = Flag.NONE
PAUSE_IF          = Flag.PAUSE_IF
RESET_IF          = Flag.RESET_IF
RESET_NEXT_IF     = Flag.RESET_NEXT_IF
ADD_HITS          = Flag.ADD_HITS
SUB_HITS          = Flag.SUB_HITS
ADD_SOURCE        = Flag.ADD_SOURCE
SUB_SOURCE        = Flag.SUB_SOURCE
ADD_ADDRESS       = Flag.ADD_ADDRESS
MEASURED          = Flag.MEASURED
TRIGGER           = Flag.TRIGGER
AND_NEXT          = Flag.AND_NEXT
OR_NEXT           = Flag.OR_NEXT
MEASURED_PERCENT  = Flag.MEASURED_PERCENT
MEASURED_IF       = Flag.MEASURED_IF
REMEMBER          = Flag.REMEMBER


# EXPORTING FLAGS (LOWERCASE - Pythonic Style)

pause_if          = Flag.PAUSE_IF
reset_if          = Flag.RESET_IF
reset_next_if     = Flag.RESET_NEXT_IF
add_hits          = Flag.ADD_HITS
sub_hits          = Flag.SUB_HITS
add_source        = Flag.ADD_SOURCE
sub_source        = Flag.SUB_SOURCE
add_address       = Flag.ADD_ADDRESS
measured          = Flag.MEASURED
trigger           = Flag.TRIGGER
and_next          = Flag.AND_NEXT
or_next           = Flag.OR_NEXT
measured_percent  = Flag.MEASURED_PERCENT
measured_if       = Flag.MEASURED_IF
remember          = Flag.REMEMBER