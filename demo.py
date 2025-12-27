# demo_full.py
from models.set import AchievementSet
from models.achievement import Achievement
from models.leaderboard import Leaderboard
from models.rich_presence import RichPresence

from core.helpers import (
    byte, word, dword, bit0, bit7, float32,
    prior, delta, bcd, invert, recall,
    bitcount
)
from core.constants import Flag, LeaderboardFormat
from core.condition import Condition

# =======================================================================
# 1. SETUP
# =======================================================================
game_set = AchievementSet(game_id=12345, title="PyCheevos Demo Game")

# =======================================================================
# 2. MEMORY
# =======================================================================
mem_state       = byte(0x00A1)
mem_score       = dword(0x00B0)
mem_health      = byte(0x00C0)
mem_stage       = byte(0x00D0)
mem_timer       = word(0x00E0)
base_pointer    = dword(0x1000)

# =======================================================================
# 3. ACHIEVEMENT
# =======================================================================
ach_survivor = Achievement("Survivor", "Finish Stage 1 with full health.", 5, 111000001)

# CORREÇÃO 1: Removido o '&'. Usamos uma lista para múltiplas condições
# "Trigger" logic: The stage changed FROM 1 (Delta) TO something else
cond_complete_trigger = [
    (mem_stage.delta() == 1),
    (mem_stage > 1)
]

ach_survivor.add_core([
    (mem_stage == 1),
    (mem_state == 1),
    (mem_health == 100)
])
# Adicionamos a lista do trigger
ach_survivor.add_core(cond_complete_trigger)

game_set.add_achievement(ach_survivor)

# =======================================================================
# 4. POINTERS & ADVANCED
# =======================================================================
ach_treasure = Achievement("Treasure Hunter", "Collect 50 coins...", 10, 111000002)

# Pointer Logic (Funciona agora com a atualização do value.py)
dynamic_coins = (base_pointer >> byte(0x20))

reset_damage = (mem_health < prior(mem_health))
reset_damage.flag = Flag.RESET_IF

# Delta agora funciona em expressões (graças à atualização do value.py)
collect_count = (dynamic_coins > dynamic_coins.delta()).with_hits(50)

ach_treasure.add_core([reset_damage, collect_count])
ach_treasure.add_alt(mem_stage == 5)
ach_treasure.add_alt(mem_stage == 6)

game_set.add_achievement(ach_treasure)

# =======================================================================
# 6. LEADERBOARDS
# =======================================================================
lb_speedrun = Leaderboard("Stage 1 Speedrun", "Fastest time", 111000004, LeaderboardFormat.MILLISECS, True)

lb_start = [(mem_stage == 1), (mem_stage.prior() != 1)]
lb_cancel = [(mem_state == 0)]
lb_submit = [(mem_stage == 1), (mem_stage.delta() == 2)]

# CORREÇÃO 2 & 3: Definir flag Measured corretamente
# Não podemos fazer 'mem_timer.flag = ...' pois mem_timer é MemoryValue.
# Devemos criar uma Condição.
lb_value = Condition(mem_timer, flag=Flag.MEASURED)

lb_speedrun.set_start(lb_start)
lb_speedrun.set_cancel(lb_cancel)
lb_speedrun.set_submit(lb_submit)
lb_speedrun.set_value(lb_value) # Agora aceita porque é Condition

game_set.add_leaderboard(lb_speedrun)

# =======================================================================
# 8. EXPORT
# =======================================================================
game_set.save()
print("Demo script executed successfully!")