from models.set import AchievementSet
from models.achievement import Achievement
from core.helpers import byte
from core.constants import Flag

def logica_sem_nitro():
    mem_nitro = byte(0x0005c7)
    mem_evento = byte(0x0007dd)

    mem_pista = byte(0x0013de)

    reset_cond = (mem_nitro < 4)
    reset_cond.flag = Flag.RESET_IF

    vitoria_cond = (mem_evento == 0x07).with_hits(1)

    core = [vitoria_cond, reset_cond]

    alt_pista1 = [(mem_pista == 0x00)]
    alt_pista2 = [(mem_pista == 0x01)]

    return core, alt_pista1, alt_pista2

meu_set = AchievementSet(game_id=23121, title="Racing game - No nitro")

conquista = Achievement (
    title="Mestre da pista",
    description="Vença no circuito Italiano sem usar nitro",
    points=10,
    badge="00000"
)

l_core, l_pista1, l_pista2 = logica_sem_nitro()

conquista.add_core(l_core)
conquista.add_alt(l_pista1)
conquista.add_alt(l_pista2)

meu_set.add_achievement(conquista)
meu_set.save()