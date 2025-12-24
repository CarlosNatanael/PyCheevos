from models.set import AchievementSet
from models.achievement import Achievement
from core.helpers import byte
from core.constants import Flag

def logica_matematica():
    moedas_fase1 = byte(0x10)
    moedas_fase2 = byte(0x20)
    
    soma_cond = (moedas_fase1 + moedas_fase2 > 50)
    
    return [soma_cond]

meu_set = AchievementSet(game_id=23121, title="Racing game - No nitro")

conquista = Achievement(
    title="Dano Teste",
    description="Vença no circuito Monaco sem nenhum dano",
    points=25,
    badge="00000"
)

l_math = logica_matematica()
conquista.add_core(l_math)

meu_set.add_achievement(conquista)
meu_set.save()