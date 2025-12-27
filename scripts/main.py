from models.set import AchievementSet
from models.rich_presence import RichPresence
from core.helpers import byte, recall
from core.constants import Flag

mem_pista_id = byte(0x0013de)
mem_estado   = byte(0x00009e)
mem_volta    = byte(0x0000a9)
mem_dano     = byte(0x000076)

mem_min = byte(0x0000ad)
mem_seg = byte(0x0000ae)
mem_cen = byte(0x0000b0)

rp = RichPresence()
rp.add_lookup("NomePista", {
    0: "Treino",
    13: "Brasil",
    14: "Mônaco",
    15: "Itália",
})

rp.add_display(
    condition=(mem_estado != 0), 
    text="No Menu Principal 🚗"
)

texto_corrida = (
    f"{rp.lookup('NomePista', mem_pista_id)} "
    f"• Volta {rp.value(mem_volta)} "
    f"• {rp.value(mem_min)}:{rp.value(mem_seg, 'SECS')}.{rp.value(mem_cen)} "
    f"• Dano: {rp.value(mem_dano)}"
)

rp.add_display(condition="True", text=texto_corrida)
meu_set = AchievementSet(game_id=23121, title="Racing Game - Final Set")
meu_set.add_rich_presence(rp)
meu_set.save()