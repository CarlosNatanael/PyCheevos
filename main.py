from core .constants import MemorySize, Flag
from core .value import MemoryValue, ConstantValue
from core .condition import Condition

vida = MemoryValue(0x0055, MemorySize.BIT8)

morto = ConstantValue(0)

condicao = Condition(
    lvalue=vida,
    cmp="=",
    rvalue=morto,
    flag=Flag.RESET_IF
)
print(f"string gerada: {condicao.render()}")