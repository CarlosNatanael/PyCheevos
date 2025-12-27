### Imports ###
import pycheevos.core.helpers
from pycheevos.core.helpers import delta, prior, bcd
import pycheevos.core.constants as const
from pycheevos.models.set import AchievementSet
from pycheevos.models.achievement import Achievement

### Define Addresses ###

gameState = helpers.byte(0x0d4110)
#0x02 - Logos
#0x03 - Logos but rolled over from the main menu
#0x04 - Intro Cutscene
#0x05 - Win
#0x06 - Menus
#0x07 - In Game

hz = helpers.byte(0x0e1412)
#0x05 - 50hz
#0x06 - 60hz

loadingScreen = helpers.byte(0x0d4420)
#0x00 - No
#0x01 - Yes

raceOutcome = helpers.dword(0x03e378) # Pointer

### Functions ###

def coinCollectorLogic(race: int):
    return


### Initialize Set ###

def main():
    mySet = AchievementSet(game_id=6675, title="South Park Rally")
    
    ### Achievements ###
    
    intro = Achievement("Come on Up to South Park!", "Watch the whole South Park intro", 5)
    introCore = [
        (gameState.delta() == 0x02).with_flag(const.Flag.OR_NEXT),
        (gameState.delta() == 0x03).with_flag(const.Flag.RESET_IF),
        (gameState == 0x06)
    ]
    
    introAlt1 = [
        (hz == 0x05).with_flag(const.Flag.AND_NEXT),
        (loadingScreen == 0x00).with_flag(const.Flag.AND_NEXT),
        (gameState.delta() == 0x04).with_hits(1420)
    ]
    
    introAlt2 = [
        (hz == 0x06).with_flag(const.Flag.AND_NEXT),
        (loadingScreen == 0x00).with_flag(const.Flag.AND_NEXT),
        (gameState.delta() == 0x04).with_hits(1700)
    ]
    
    intro.add_core(introCore)
    intro.add_alt(introAlt1)
    intro.add_alt(introAlt2)
    mySet.add_achievement(intro)
    
    
    
    mySet.save()