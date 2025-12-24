from models.set import AchievementSet
from models.achievement import Achievement
from core.helpers import byte
from core.constants import Flag

def dano_carro():
    mem_dano = byte(0x000076)
    mem_evento = byte(0x0007dd)
    mem_verde = byte(0x00009e)
    mem_colocacao = byte(0x0007d9)
    mem_pista = byte(0x0013de)

    cond_iniciar = (mem_verde == 0).with_hits(1)
    pista_monaco = (mem_pista == 14)
    cond_primeiro = (mem_colocacao == 0)

    vitoria_cond = (mem_evento == 7)
    vitoria_cond.flag = Flag.TRIGGER

    delta_corrida = (mem_evento.delta() == 13)

    core = [
        cond_iniciar,
        pista_monaco,
        cond_primeiro,
        vitoria_cond,
        delta_corrida
    ]

    cond_reset = (mem_dano > 0)
    cond_reset.flag = Flag.RESET_IF

    alt_dano = [cond_reset]

    return core, alt_dano

meu_set = AchievementSet(game_id=23121, title="Racing game - No nitro")

conquista = Achievement(
    title="Dano Teste",
    description="Vença no circuito Monaco sem nenhum dano",
    points=25,
    badge="00000"
)

l_core, l_alt1 = dano_carro()

conquista.add_core(l_core)
conquista.add_alt(l_alt1)

meu_set.add_achievement(conquista)
meu_set.save()