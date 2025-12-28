from models.set import AchievementSet
from models.achievement import Achievement
from core.helpers import byte
from core.constants import reset_if, trigger

def damage_car():
    mem_damage = byte(0x000076)
    mem_event = byte(0x0007dd)
    mem_green = byte(0x00009e)
    mem_position = byte(0x0007d9)
    mem_circuit = byte(0x0013de)

    # 1. Start Condition: Green Light (0) for 1 frame
    cond_start = (mem_green == 0).with_hits(1)
    
    # 2. Track & Rank requirements
    circuit_monaco = (mem_circuit == 14)
    cond_first = (mem_position == 0)

    # 3. Trigger: Event changed to 7 (Victory)
    victory_cond = (mem_event == 7)
    victory_cond.with_flag(trigger)

    # 4. Delta Check: Event was 13 previously
    delta_circuit = (mem_event.delta() == 13)

    core = [
        cond_start,
        circuit_monaco,
        cond_first,
        victory_cond,
        delta_circuit
    ]

    # 5. Reset: If Damage > 0
    cond_reset = (mem_damage > 0)
    cond_reset.with_flag(reset_if)

    alt_damage = [cond_reset]

    return core, alt_damage

# Setup
my_set = AchievementSet(game_id=23121, title="Racing game")

monaco_damageless = Achievement(
    title="Untouchable",
    description="Win a race at the Monaco circuit with zero damage to your car",
    points=25,
    badge="00000"
)

l_core, l_alt1 = damage_car()

monaco_damageless.add_core(l_core)
monaco_damageless.add_alt(l_alt1)

my_set.add_achievement(monaco_damageless)