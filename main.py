# main.py
from core.helpers import byte, word, bit7

mario_state = byte(0x0750)
powerup_type = byte(0x0756)

condicao1 = (mario_state == 1)
condicao2 = (powerup_type != 0)

print(f"Condição 1: {condicao1.render()}")
print(f"Condição 2: {condicao2.render()}")

fase_concluida = (bit7(0x001F) == 1)
print(f"Fase Concluída: {fase_concluida.render()}")