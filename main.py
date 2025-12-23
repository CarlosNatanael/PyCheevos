from core.helpers import byte
from core.constants import Flag
from models.achievement import Achievement

conquista = Achievement(
    id=558696,
    title="Vença sem usar nitro",
    description="vença a nitro sem usar nitro",
    points=10,
    badge="12345"
)

nitro = byte(0x0005c7)
evento = byte(0x0007dd)

cond_vitoria = (evento == 0x07)
conquista.add_condition(cond_vitoria)

cond_reset = (nitro < 0x04)
cond_reset.flag = Flag.RESET_IF

conquista.add_condition(cond_reset)

print("--- Sáida para o arquivo do RA ---")
print(f"\n{conquista.render()}")