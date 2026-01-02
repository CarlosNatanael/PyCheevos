### Imports ###
import core.helpers as helpers
from core.helpers import *
from core.constants import *
from core.condition import Condition
from models.set import AchievementSet
from models.achievement import Achievement

### Define Addresses ###

gameState = byte(0x0d4110)
#0x02 - Logos
#0x03 - Logos but rolled over from the main menu
#0x04 - Intro Cutscene
#0x05 - Win
#0x06 - Menus
#0x07 - In Game

hz = byte(0x0e1412)
#0x05 - 50hz
#0x06 - 60hz

loadingScreen = byte(0x0d4420)
#0x00 - No
#0x01 - Yes

raceOutcome = (tbyte(0x03e378) >> dword(0x00)).with_flag(remember)
raceData = (tbyte(0x1181a8) >> (tbyte(0x02A0)))

modeAddress = byte(0x0e3746)
demoAddress = byte(0x0e407c)

### Functions ###

demoCheck = (demoAddress == 0x00)
championship = (modeAddress == 0x00)
miniChampionship = (modeAddress == 0x01)
arcadeRace = (modeAddress == 0x02)

raceState = (raceData >> byte(0x38))
#0x00 - Loading
#0x01 - When set, resets race 
#0x02 - Flyover
#0x03 - Countdown
#0x04 - Racing
#0x05 - Win/Lose
#0x06 - Race result

character = byte(0x0e3415)
#-1 if not in Championship Mode after Mystery (Bebe becomes 0x0b, Shelly becomes 0x0c, etc)
#0x00 - Stan
#0x01 - Kyle
#0x02 - Cartman
#0x03 - Kenny
#0x04 - Wendy
#0x05 - Chef
#0x06 - Officer Barbrady
#0x07 - Uncle Jimbo
#0x08 - Random
#0x09 - Pip
#0x0a - Mr. Garrison
#0x0b - Mystery
#0x0c - Bebe
#0x0d - Shelly
#0x0e - Tweek
#0x0f - Mr. Mackey
#0x10 - Cartman Cop
#0x11 - Skuzzlebutt
#0x12 - Mrs. Broflovski
#0x13 - Ms. Cartman
#0x14 - Big Gay Al
#0x15 - Ike
#0x16 - Visitor
#0x17 - Ned
#0x18 - Mephesto
#0x19 - Death
#0x1a - Grandpa
#0x1b - Marvin
#0x1c - Jesus
#0x1d - Terrance & Phillip
#0x1e - Damien
#0x1f - Satan
#0x20 - Wimpy Stan
#0x21 - Kyle Vampire
#0x22 - Kenny Football
#0x23 - Cartman Homie
#0x24 - Chef Braveheart

playerWin = (raceData >> dword(0xa0)) == recall() 
playerFinish = (raceData >> dword(0xa0)) != 0x00

resetToCountdown = (raceState == 0x03).with_hits(1)

unlockTimers = (raceData >> float32(0xb0))

rallyDays2Checkpoint = (raceData >> byte(0x94))

raceIndicator = byte(0x0e3152)
def raceName(race: int):
    match race:
        case 0x00:
            return "Rally Race 1"
        case 0x01:
            return "Rally Race 2"
        case 0x02:
            return "Cow Day"
        case 0x03:
            return "Valentine's Day"
        case 0x04:
            return "Spring Cleaning"
        case 0x05:
            return "Read a Book Day"
        case 0x06:
            return "Easter Egg Hunt"
        case 0x07:
            return "Pink Lemonade Race"
        case 0x08:
            return "Memorial Day"
        case 0x09:
            return "Independence Day"
        case 0x0a:
            return "Halloween Rally"
        case 0x0b:
            return "Thanksgiving"
        case 0x0c:
            return "Christmas Day"
        case 0x0d:
            return "Millenium New Year's Eve"
        case 0x0e:
            return "Ass Battle"
        case 0x0f:
            return "Random"
        case _:
            return "Unknown"

def achievementTitle(id: str):
    match id:
        case "1_champ":
            return "Gentlemen, Start Your Profanity"
        case "2_champ":
            return "Trophy Transporter"
        case "3_champ":
            return "Moo?"
        case "4_champ":
            return "Be My Big Gay Al-Entine"
        case "5_champ":
            return "Give Me Back My Undies!"
        case "6_champ":
            return "Reading Is for Nerds"
        case "7_champ":
            return "Jesus, Take the Wheel"
        case "8_champ":
            return "When Life Gives You Lemons, Ram into Someone"
        case "9_champ":
            return "You're Breakin' My Balls Here, Officer!"
        case "10_champ":
            return "This Is America, Bro"
        case "11_champ":
            return "I'm Not Fat, I'm Big-Boned!"
        case "12_champ":
            return "That Turkey's Pissed Off!"
        case "13_champ":
            return "Howdy-Ho!"
        case "14_champ":
            return "We're Gonna Have to Blame Canada"

        # Mini Championship
        case "1_mini":
            return "Still Think the Rides Are Rigged?"
        case "2_mini":
            return "Big City Dreams"
        case "3_mini":
            return "This Place Hasn't Got Shit on Tegridy Farms"
        case "4_mini":
            return "Big Gay Al's Big Gay Mini Championship"
        case "5_mini":
            return "You Kids Better Wash Your Hands"
        case "6_mini":
            return "Go, Woodland Critter, Go!"
        case "7_mini":
            return "We're Huntin' for First Place!"
        case "8_mini":
            return "We Survived, Dude!"

        # Beat My Times
        case "1_dev":
            return "Now This Is Rigged"
        case "2_dev":
            return "City-Wide Fame If You Beat This"
        case "3_dev":
            return "Farming Dev Points from This Set"
        case "4_dev":
            return "Big Gay Al's Big Gay Dev Time"
        case "5_dev":
            return "This Track Has a Special Place in Hell for It"
        case "6_dev":
            return "Many Forest Fires Were Started While Boosting to Get This Time"
        case "7_dev":
            return "The Peak of Kart Racing"
        case "8_dev":
            return "I Hate Fireballs."

        # Character Unlocks
        case "pip":
            return "Lunchy Munchies, Hmmm?"
        case "mr_garrison":
            return "I Said HOW WOULD YOU LIKE TO SUCK MY BALLS, Mr Garrison"
        case "bebe":
            return "Did You SEE These Shoes, Wendy!?"
        case "shelly":
            return "Shut Up, Turd! I'm Playing RetroAchievements"
        case "tweek":
            return "Oh Man, This Is Way Too Much Pressure!"
        case "mr_mackey":
            return "Drugs Are Bad, Mkay?"
        case "cartman_cop":
            return "Respect Mah Authoritah!"
        case "skuzzlebutt":
            return "I Am Skuzzlebutt! Lord of the Mountains!"
        case "mrs_broflovski":
            return "Weeeeeell Kyle's Mom's a Bitch, She's a Big Fat Bitch"
        case "ms_cartman":
            return "Mom, More Cheesy Poofs, Less Talking!"
        case "big_gay_al":
            return "I'm Super! Thanks for Asking!"
        case "ike":
            return "Don't Kick the Baby!"
        case "visitor":
            return "Moo!"
        case "ned":
            return "I Don't Think Eight Year Old Kids Drink Beer, Mmm"
        case "mephesto":
            return "Oh My God, He Only Has One Ass! He's of No Use to Me..."
        case "death":
            return "You Killed Kenny! You Bastard!"
        case "grandpa":
            return "Pull the Trigger, You Little Pussy!"
        case "marvin":
            return "No Starvin' Marvin, That's My Pot Pie!"
        case "jesus":
            return "Happy Birthday to Me, Happy Birthday to Me..."
        case "terrance_phillip":
            return "But We're Not Gay Phillip... We're Not?"
        case "damien":
            return "Rectus... Dominus... Cheesy Poofs..."
        case "satan":
            return "I Have Had ENOUGH of You!"
        case "extra_skins":
            return "SCOTLAND FOREVER!"
        case "cheat_sheet":
            return "If You Cheat and Succeed, You're Savvy"

        # Credits
        case "1_cred":
            return "Hey, a Quarter!"
        case "2_cred":
            return "Hey, Another Quarter!"
        case "3_cred":
            return "This Quarter Stinks..."
        case "4_cred":
            return "A Penny for My Valentine"
        case "5_cred":
            return "I Found This in My Laundry"
        case "6_cred":
            return "I Read a Book and It Said to Search Toll Bridges for Quarters"
        case "7_cred":
            return "Usually It's Candy in the Easter Eggs"
        case "8_cred":
            return "I Said a Lime, Not a Dime"
        case "9_cred":
            return "Laser-Cut Quarter"
        case "10_cred":
            return "You Have the Right to Press Pennies"
        case "11_cred":
            return "What a Treat!"
        case "12_cred":
            return "Hey! That Turkey Gobbled My Change!"
        case "13_cred":
            return "Last Christmas, I Gave You My Coins"
        case "14_cred":
            return "I Saw the Millennium Change and All I Got Was This Lousy Quarter"

        # Challenges
        case "1_challenge":
            return "Home Sweet Home"
        case "2_challenge":
            return "That There's Some Good Hunting"
        case "3_challenge":
            return "Sewer-Based Anal Probe"
        case "4_challenge":
            return "Sir, Step out of the Car Please"
        case "5_challenge":
            return "Chicken, Gravy, and Freedom!"
        case "6_challenge":
            return "What Would Jesus Do?"
        case "7_challenge":
            return "Mom Said It's MY Turn with the Laser"
        case "8_challenge":
            return "Volcanic Trophy Giving Ceremony"
        case "9_challenge":
            return "Pine Fresh Undies"
        case "10_challenge":
            return "Lemonade! Fresh Lemonade!"
        case "11_challenge":
            return "In Memorium of Doing Super"
        case "12_challenge":
            return "Christmas in the Hills"
        case "13_challenge":
             return "Super Complicated Sewer Stuff"
        case "14_challenge":
            return "Magical Mystery Tour"

        # Extras
        case "intro":
            return "Come on Up to South Park!"
        case _:
            return f"Missing Name"

def commonLogic(race: int):
    return [
        demoCheck, 
        championship, 
        raceIndicator == race
        ]

def unlocks(race: int, con: int, conditionAddress: int, shouldMeasure: bool = False):
    address = (raceData >> byte(conditionAddress))
    logic = [
        (address.delta() == con - 1),
        raceState == 0x04
    ]
    if shouldMeasure:
        logic.insert(0, (demoCheck).with_flag(measured_if)) # type: ignore
        logic.insert(1, (championship).with_flag(measured_if)) # type: ignore
        logic.insert(2, (raceIndicator == race).with_flag(measured_if)) # type: ignore
        logic.insert(4, (address == con).with_flag(measured))
    else:
        logic.insert(0, demoCheck) # type: ignore
        logic.insert(1, championship) # type: ignore
        logic.insert(2, (raceIndicator == race)) # type: ignore
        logic.insert(4, (address == con))
    return logic

playerCheckpoint = (raceData >> byte(0xa4))
playerLap = (raceData >> byte(0xb4))

ai1Checkpoint = (raceData >> byte(0xd0))
ai1Lap = (raceData >> byte(0xe0))
ai2Checkpoint = (raceData >> byte(0xfc))
ai2Lap = (raceData >> byte(0x10c))
ai3Checkpoint = (raceData >> byte(0x128))
ai3Lap = (raceData >> byte(0x138))
ai4Checkpoint = (raceData >> byte(0x154))
ai4Lap = (raceData >> byte(0x164))
ai5Checkpoint = (raceData >> byte(0x180))
ai5Lap = (raceData >> byte(0x190))

def waitingOnWin():
    return [
        raceState.delta() == 0x04,
        (raceState == 0x05).with_flag(trigger)
    ]

credits = byte(0x0e3251)
creditIncrease = [
    Condition(credits.delta()).with_flag(add_source),
    Condition(0x01).with_flag(add_source),
    Condition(0x00 == credits).with_flag(trigger) 
]
### Initialize Set ###
mySet = AchievementSet(game_id=6675, title="South Park Rally")
### Achievements ###

# Championship
order = 1
for race in range(0x00, 0x0e):
    championshipAchievementLogic = [
        *commonLogic(race),
        raceOutcome,
        playerWin,
        raceState.delta() == 0x04,
        raceState == 0x05,
    ]

    champAchievement = Achievement(achievementTitle(f"{order}_champ"), f"Win the {raceName(race)} race in Championship mode", 1)
    champAchievement.add_core(championshipAchievementLogic)
    mySet.add_achievement(champAchievement)
    order += 1 

# Unlocks

# Garrison
def garrisonUnlock():
    garrisonUnlockLogic = [
        *commonLogic(0x01),
        raceOutcome,
        playerWin.with_flag(trigger),
        resetToCountdown
    ]

    for checkpoint in range(0x00, 0x03):
        bit_func = getattr(helpers, f"bit{checkpoint}")

        droveOverCheckpoint = (raceData >> bit_func(0xc0))
        garrisonUnlockLogic.append((droveOverCheckpoint == 0x00).with_flag(and_next))
        garrisonUnlockLogic.append((rallyDays2Checkpoint.delta() > 0x00).with_flag(reset_if))

    garrisonUnlockLogic.append((raceState != 0x04).with_flag(and_next))
    garrisonUnlockLogic.append(((raceData >> byte(0x0c)) != 0x0f).with_flag(reset_if))
    garrisonUnlockLogic.append(((raceData >> byte(0x0c)) == 0x0f).with_flag(reset_if))
    garrisonUnlockLogic.append((raceState.delta() == 0x04))
    garrisonUnlockLogic.append((raceState == 0x05).with_flag(trigger))


    garrisonAchievement = Achievement(achievementTitle("mr_garrison"), "Unlock Mr. Garrison by being the only player to pass over each checkpoint with the trophy in Rally Days #2", 2)
    garrisonAchievement.add_core(garrisonUnlockLogic)
    mySet.add_achievement(garrisonAchievement)

# Pip
def pipUnlock():
    pipUnlockLogic = [
        *commonLogic(0x01),
        raceOutcome,
        playerWin.with_flag(trigger),
        resetToCountdown
    ]

    for checkpoint in range(0x00, 0x03):
        print(checkpoint)
        bit_func = getattr(helpers, f"bit{checkpoint}")
        droveOverCheckpoint = (raceData >> bit_func(0xc0))

        if checkpoint == 0x00:
            pipUnlockLogic.append((droveOverCheckpoint == 0x00).with_flag(and_next))
            pipUnlockLogic.append((rallyDays2Checkpoint.delta() > 0x00).with_flag(reset_if))
        else:
            pipUnlockLogic.append((droveOverCheckpoint == 0x01).with_flag(reset_if))



    pipUnlockLogic.append((raceState != 0x04).with_flag(and_next))
    pipUnlockLogic.append(((raceData >> byte(0x0c)) != 0x09).with_flag(reset_if))
    pipUnlockLogic.append(((raceData >> byte(0x0c)) == 0x09).with_flag(reset_if))
    pipUnlockLogic.append((raceState.delta() == 0x04))
    pipUnlockLogic.append((raceState == 0x05).with_flag(trigger))


    pipAchievement = Achievement(achievementTitle("pip"), "Unlock Pip by passing over only Checkpoints 1 and 4 with the trophy in Rally Days #2", 2)
    pipAchievement.add_core(pipUnlockLogic)
    mySet.add_achievement(pipAchievement)  

# Bebe
def bebeUnlock():
    bebeUnlockLogic = [
        *commonLogic(0x02),
        raceOutcome,
        playerWin,
        (unlockTimers.delta() < 120.0).with_flag(reset_if),
        resetToCountdown,
        *waitingOnWin()
    ]

    bebeAchievement = Achievement(achievementTitle("bebe"), "Unlock Bebe by losing without touching the cure in Cow Days", 2)
    bebeAchievement.add_core(bebeUnlockLogic)
    mySet.add_achievement(bebeAchievement)
    
# Extra Skins
def extraSkinsUnlock():
    extraSkinsLogic = unlocks(0x03, 0x03, 0xc8, True)
    extraSkinsAchievement = Achievement(achievementTitle("extra_skins"), "Unlock the extra skins for The Boys and Chef by collecting all 3 Golden Cows in the Valentine's Day race", 2)
    extraSkinsAchievement.add_core(extraSkinsLogic)
    mySet.add_achievement(extraSkinsAchievement)
    
# Tweek
def tweekUnlock():
    tweekUnlockLogic = unlocks(0x04, 0x05, 0xc8, True)
    tweekAchievement = Achievement(achievementTitle("tweek"), "Unlock Tweek by using 5 caffeine boosts from the blue power up boxes in the Spring Cleaning race", 2)
    tweekAchievement.add_core(tweekUnlockLogic)
    mySet.add_achievement(tweekAchievement)

def cartmanCopUnlock():
    cartmanCopLogic = unlocks(0x05, 0x05, 0xc0, True)
    cartmanCopAchievement = Achievement(achievementTitle("cartman_cop"), "Unlock Cartman Cop by hitting Chicken Lover's bus 5 times with Salty Balls in the Read a Book Day race", 2)
    cartmanCopAchievement.add_core(cartmanCopLogic)
    mySet.add_achievement(cartmanCopAchievement)

def skuzzlebuttUnlock():
    skuzzlebuttLogic = unlocks(0x06, 0x01, 0xc8)
    skuzzlebuttAchievement = Achievement(achievementTitle("skuzzlebutt"), "Unlock Skuzzlebutt by collecting the Golden Cow during the Easter race", 2)
    skuzzlebuttAchievement.add_core(skuzzlebuttLogic)
    mySet.add_achievement(skuzzlebuttAchievement)

def mrsBrovlofskiUnlock():
    mrsBrovlofskiLogic = unlocks(0x06, 0x01, 0xcc)
    mrsBrovlofskiAchievement = Achievement(achievementTitle("mrs_broflovski"), "Unlock Mrs. Broflovski by collecting the Pie during the Easter Race", 2)
    mrsBrovlofskiAchievement.add_core(mrsBrovlofskiLogic)
    mySet.add_achievement(mrsBrovlofskiAchievement)

def msCartmanUnlock():
    msCartmanLogic = [
        *commonLogic(0x07),
        raceOutcome,
        playerWin,
        resetToCountdown,
        (playerCheckpoint != 0x00).with_flag(trigger),
        (ai1Checkpoint != 0x00).with_flag(reset_if),
        (ai2Checkpoint != 0x00).with_flag(reset_if),
        (ai3Checkpoint != 0x00).with_flag(reset_if),
        (ai4Checkpoint != 0x00).with_flag(reset_if),
        (ai5Checkpoint != 0x00).with_flag(reset_if),
        *waitingOnWin()
    ]
    msCartmanAchievement = Achievement(achievementTitle("ms_cartman"), "Unlock Ms. Cartman by being the only player to deliver lemonade during the Pink Lemonade race", 2)
    msCartmanAchievement.add_core(msCartmanLogic)
    mySet.add_achievement(msCartmanAchievement)

def ikeUnlock():
    ikeLogic = unlocks(0x08, 0x01, 0xc8)
    ikeAchievement = Achievement(achievementTitle("ike"), "Unlock Ike by collecting the Golden Cow on the plane wing during the Memorial Day race", 2)
    ikeAchievement.add_core(ikeLogic)
    mySet.add_achievement(ikeAchievement)

def visitorUnlock():
    visitorLogic = unlocks(0x08, 0x01, 0xcc, True)
    visitorAchievement = Achievement(achievementTitle("visitor"), "Unlock Visitor by collecting both Pies during the Memorial Day race", 2)
    visitorAchievement.add_core(visitorLogic)
    mySet.add_achievement(visitorAchievement)

def nedUnlock():
    nedLogic = [
        (demoCheck).with_flag(measured_if),
        (championship).with_flag(measured_if),
        (raceIndicator == 0x09).with_flag(measured_if),
        raceOutcome,
        playerWin,
        (raceData >> byte(0xc8) == 0x0c - 1),
        (raceData >> byte(0xc8) >= 0x0c).with_flag(measured),
        *waitingOnWin()
    ]
    nedAchievement = Achievement(achievementTitle("ned"), "Unlock Ned by winning after using 12 Caffeine Boosts or Terrance Boosts during the Independence Day race", 2)
    nedAchievement.add_core(nedLogic)
    mySet.add_achievement(nedAchievement)

def deathUnlock():
    unlockCondition = (raceData >> byte(0xc8))
    deathLogic = [
        *commonLogic(0x0a),
        raceOutcome,
        playerWin,
        unlockCondition == 0x00,
        *waitingOnWin()
    ]
    deathAchievement = Achievement(achievementTitle("death"), "Unlock Death by winning while only delivering 4 Candies at once during the Halloween race", 2)
    deathAchievement.add_core(deathLogic)
    mySet.add_achievement(deathAchievement)

def marvinUnlock():
    marvinLogic = [
        *commonLogic(0x0b),
        playerFinish,
        (playerCheckpoint != 0x00).with_flag(reset_if),
        resetToCountdown,
        *waitingOnWin()
    ]
    marvinAchievement = Achievement(achievementTitle("marvin"), "Unlock Marvin by losing without collecting any turkeys during the Thanksgiving race", 2)
    marvinAchievement.add_core(marvinLogic)
    mySet.add_achievement(marvinAchievement)

def damienUnlock():
    damienLogic = [
        *commonLogic(0x0d),
        raceOutcome,
        playerWin,
        (raceData >> byte(0xc4) != 0x00).with_flag(reset_if),
        resetToCountdown,
        *waitingOnWin()
    ]
    damienAchievement = Achievement(achievementTitle("damien"), "Unlock Damien by winning without letting another player pick up the key during the Millenium New Years Eve race", 2)
    damienAchievement.add_core(damienLogic)
    mySet.add_achievement(damienAchievement)

def tapUnlock():
    tapLogic = unlocks(0x0c, 0x04, 0xc8, True)
    tapAchievement = Achievement(achievementTitle("terrance_phillip"), "Unlock Terrance & Phillip by collecting all 4 Golden Cows during the Christmas race", 2)
    tapAchievement.add_core(tapLogic)
    mySet.add_achievement(tapAchievement)




garrisonUnlock()
pipUnlock()
bebeUnlock()
extraSkinsUnlock()
tweekUnlock()
cartmanCopUnlock()
skuzzlebuttUnlock()
mrsBrovlofskiUnlock()
msCartmanUnlock()
ikeUnlock()
visitorUnlock()
nedUnlock()
deathUnlock()
marvinUnlock()
damienUnlock()
tapUnlock()

# Unlocks based on ++0xc0
# Garrison
# Pip
# Cartman Cop
# Bebe

# Unlocks based on ++0xc4
# Damien

# Unlocks based on ++0xc8
# Cheat Sheet
# Extra Skins
# Tweek
# Skuzzlebutt
# Ike
# Ned
# Death



# Unlocks based on ++0xcc
# Ms. Brovlofski
# Visitor


# Unlocks that are wack as fuck and are unique
# Ms. Cartman
# Starvin' Marvin



# Credit Achievements
order = 1
for race in range(0x00, 0x0e):
    creditAchievementLogic = [
        *commonLogic(race),
        raceState == 0x04,
        *creditIncrease,
    ]

    credAchievement = Achievement(achievementTitle(f"{order}_cred"), f"Collect the Extra Credit during the {raceName(race)} race in Championship mode", 1)
    credAchievement.add_core(creditAchievementLogic)

    mySet.add_achievement(credAchievement)
    order += 1
    

# Intro - likely UWC but was a good pointer test
intro = Achievement(achievementTitle("intro"), "Watch the whole South Park intro", 0)
introCore = [
    (gameState.delta() == 0x02).with_flag(or_next),
    (gameState.delta() == 0x03).with_flag(reset_if),
    (gameState == 0x06)
]

def introAlts(currentHz: int):
    return [
        (hz == currentHz).with_flag(and_next),
        (loadingScreen == 0x00).with_flag(and_next),
        (gameState.delta() == 0x04).with_hits(1420 if currentHz == 0x05 else 1700)
    ]

intro.add_core(introCore)
intro.add_alt(introAlts(0x05))
intro.add_alt(introAlts(0x06))
mySet.add_achievement(intro)


mySet.save()