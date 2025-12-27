from models.set import AchievementSet
from models.leaderboard import Leaderboard
from core.condition import Condition
from core.helpers import byte, dword
from core.constants import Flag, LeaderboardFormat

# Mapeamento
mem_lap = byte(0x0000a9)
mem_temp_m = byte(0x0000ad)
mem_temp_s = byte(0x0000ae)
mem_temp_cs = byte(0x0000b0)

cond_delta = (mem_lap.delta() == 3)

cond_min = (mem_temp_m.bcd() * 6000)
cond_min.flag = Flag.ADD_SOURCE

cond_sec = (mem_temp_s.bcd() * 100)
cond_sec.flag = Flag.ADD_SOURCE

cond_ces = Condition(mem_temp_cs.bcd()) 
cond_ces.flag = Flag.MEASURED

meu_set = AchievementSet(game_id=23121, title="Racing game - Leaderboard")

lb = Leaderboard(
    title="Tempo total - Italia",
    description="Melhor tempo na Italia",
    id=11100001,
    format=LeaderboardFormat.MILLISECS,
    lower_is_better=True
)

start_cond = [
    (byte(0x0007dd) == 13),
    (byte(0x0013de) == 0),
    (byte(0x0000a9) == 4),
    (cond_delta)
]

cancel_cond = [
    Condition(0, "=", 1)
]

submit_cond = [
    Condition(0, "=", 1)
]
value_cond = [
    cond_min,
    cond_sec,
    cond_ces
]

lb.set_start(start_cond)
lb.set_cancel(cancel_cond)
lb.set_submit(submit_cond)
lb.set_value(value_cond)

meu_set.add_leaderboard(lb)
meu_set.save()