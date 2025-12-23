from models.set import AchievementSet
from models.achievement import Achievement
from core.helpers import byte
from core.constants import Flag

def condicoes_sem_nitro():

    mem_nitro = byte(0x0005c7)
    mem_evento = byte(0x0007dd)

    vitoria = (mem_evento == 0x07).with_hits(1)

    reset_nitro = (mem_nitro < 0x04)
    reset_nitro.flag = Flag.RESET_IF

    return [vitoria, reset_nitro]

meu_set = AchievementSet(game_id=23121, title="Racing Game - Custom set")

conquista_nitro = Achievement (
    title="Puro Braço",
    description="Vença a corrida sem usar nenhuma gota de nitro",
    points=10,
    badge="00000"
)

conquista_nitro.add_conditions(condicoes_sem_nitro())

meu_set.add_achievement(conquista_nitro)

meu_set.save()