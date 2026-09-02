from pathlib import Path
import shutil
import sys
from datetime import datetime

ROOT = Path(".")
PARTIES = ROOT / "data/trainers/parties.asm"
READTRAINER = ROOT / "engine/battle/read_trainer_party.asm"

for p in (PARTIES, READTRAINER):
    if not p.exists():
        print("ERRO: execute este script na pasta raiz do pokeyellow.")
        print("Não encontrei:", p)
        sys.exit(1)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / f"backup_elite4_rematch_{stamp}"
(backup / "data/trainers").mkdir(parents=True)
(backup / "engine/battle").mkdir(parents=True)
shutil.copy2(PARTIES, backup / "data/trainers/parties.asm")
shutil.copy2(READTRAINER, backup / "engine/battle/read_trainer_party.asm")

# 1) Times de rematch
ptext = PARTIES.read_text()

block = """
; Elite Four and Champion rematch teams
LoreleiRematchData:
    db $FF, 65, DEWGONG, 66, CLOYSTER, 67, SLOWBRO, 68, JYNX, 70, LAPRAS, 72, ARTICUNO, 0

BrunoRematchData:
    db $FF, 65, HITMONLEE, 66, HITMONCHAN, 67, POLIWRATH, 68, MACHAMP, 70, ONIX, 72, MOLTRES, 0

AgathaRematchData:
    db $FF, 65, ARBOK, 66, GOLBAT, 67, HAUNTER, 68, GENGAR, 70, GENGAR, 72, MEWTWO, 0

LanceRematchData:
    db $FF, 65, GYARADOS, 66, AERODACTYL, 67, DRAGONAIR, 68, DRAGONAIR, 70, DRAGONITE, 72, ZAPDOS, 0

Rival3RematchData:
    db $FF, 68, PIKACHU, 68, ALAKAZAM, 69, EXEGGUTOR, 70, SNORLAX, 71, GYARADOS, 75, MEW, 0
"""

if "LoreleiRematchData:" not in ptext:
    ptext = ptext.rstrip() + "\n\n" + block.strip() + "\n"
    PARTIES.write_text(ptext)

# 2) Liga os novos times ao ReadTrainer após a primeira vitória na Liga.
rtext = READTRAINER.read_text()

if "; Elite Four rematches after becoming Champion." not in rtext:
    marker = "        jr .normalTrainer\n\n.brockRematch"
    if marker not in rtext:
        print("ERRO: não encontrei o bloco atual de rematches dos líderes.")
        print("Backup criado em:", backup)
        sys.exit(1)

    dispatch = """        cp LORELEI
        jr z, .loreleiRematch
        cp BRUNO
        jr z, .brunoRematch
        cp AGATHA
        jr z, .agathaRematch
        cp LANCE
        jr z, .lanceRematch
        cp RIVAL3
        jr z, .rival3Rematch
        jr .normalTrainer

"""
    rtext = rtext.replace(
        "        jr .normalTrainer\n\n.brockRematch",
        dispatch + ".brockRematch",
        1,
    )

    giovanni = """.giovanniRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, GiovanniRematchData
        jr .IterateTrainer

.normalTrainer
"""
    if giovanni not in rtext:
        print("ERRO: não encontrei o final do bloco de rematch (Giovanni).")
        print("Backup criado em:", backup)
        sys.exit(1)

    elite_handlers = """.giovanniRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, GiovanniRematchData
        jr .IterateTrainer

; Elite Four rematches after becoming Champion.
.loreleiRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, LoreleiRematchData
        jr .IterateTrainer

.brunoRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, BrunoRematchData
        jr .IterateTrainer

.agathaRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, AgathaRematchData
        jr .IterateTrainer

.lanceRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, LanceRematchData
        jr .IterateTrainer

.rival3Rematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, Rival3RematchData
        jr .IterateTrainer

.normalTrainer
"""
    rtext = rtext.replace(giovanni, elite_handlers, 1)
    READTRAINER.write_text(rtext)

print("OK: Elite Four + Champion rematch aplicados.")
print("Lorelei: Articuno Lv72")
print("Bruno: Moltres Lv72")
print("Agatha: Mewtwo Lv72")
print("Lance: Zapdos Lv72")
print("Champion: Mew Lv75")
print("Observação: Espeon não existe em Pokémon Yellow; foi usado Alakazam.")
print("Backup:", backup)
print("Agora rode: make")
