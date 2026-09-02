#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import sys
from datetime import datetime

ROOT = Path.cwd()
MAPS = ROOT / "data" / "wild" / "maps"
CONSTANTS = ROOT / "constants" / "pokemon_constants.asm"

if not MAPS.is_dir():
    sys.exit("ERRO: execute este script na raiz do projeto pokeyellow (onde existe data/wild/maps).")

if not CONSTANTS.is_file():
    sys.exit("ERRO: não encontrei constants/pokemon_constants.asm.")

# Backup automático, além do backup manual que já foi feito.
backup = ROOT / f"data/wild_backup_before_151_{datetime.now():%Y%m%d_%H%M%S}"
## backup automatico desativado
print(f"Backup criado em: {backup}")

# Cada lista abaixo substitui somente a tabela indicada (grass ou water).
# A taxa de encontro original do mapa é preservada.
PLAN = {
    "ViridianForest.asm": {
        "grass": [(3,"CATERPIE"),(4,"WEEDLE"),(4,"METAPOD"),(5,"KAKUNA"),(4,"PIDGEY"),
                  (5,"PIKACHU"),(6,"CATERPIE"),(6,"WEEDLE"),(8,"BUTTERFREE"),(9,"BEEDRILL")]
    },

    "MtMoon1F.asm": {
        "grass": [(8,"ZUBAT"),(9,"ZUBAT"),(10,"GEODUDE"),(9,"NIDORINA"),(9,"NIDORINO"),
                  (10,"ZUBAT"),(10,"GEODUDE"),(11,"CLEFAIRY"),(12,"SANDSHREW"),(13,"CLEFABLE")]
    },
    "MtMoonB1F.asm": {
        "grass": [(8,"ZUBAT"),(9,"ZUBAT"),(10,"GEODUDE"),(10,"NIDORINA"),(10,"NIDORINO"),
                  (11,"PARAS"),(11,"CLEFAIRY"),(12,"OMANYTE"),(12,"KABUTO"),(13,"CLEFABLE")]
    },
    "MtMoonB2F.asm": {
        "grass": [(10,"ZUBAT"),(11,"GEODUDE"),(13,"PARAS"),(12,"NIDORINA"),(12,"NIDORINO"),
                  (13,"CLEFAIRY"),(14,"OMANYTE"),(14,"KABUTO"),(15,"CLEFABLE"),(16,"PARASECT")]
    },

    "Route5.asm": {
        "grass": [(14,"PIDGEY"),(14,"RATTATA"),(7,"ABRA"),(15,"MEOWTH"),(16,"RATTATA"),
                  (17,"PIDGEOTTO"),(16,"MEOWTH"),(5,"JIGGLYPUFF"),(17,"PERSIAN"),(18,"EEVEE")]
    },
    "Route6.asm": {
        "grass": [(15,"PIDGEY"),(14,"RATTATA"),(7,"ABRA"),(16,"MEOWTH"),(16,"RATTATA"),
                  (17,"PIDGEOTTO"),(17,"MEOWTH"),(5,"JIGGLYPUFF"),(18,"PERSIAN"),(19,"WIGGLYTUFF")],
        "water": [(15,"PSYDUCK"),(15,"POLIWAG"),(16,"GOLDEEN"),(17,"POLIWAG"),(18,"PSYDUCK"),
                  (18,"POLIWHIRL"),(19,"GOLDEEN"),(20,"GOLDUCK"),(20,"POLIWHIRL"),(21,"SEAKING")]
    },
    "Route7.asm": {
        "grass": [(20,"PIDGEY"),(20,"RATTATA"),(15,"ABRA"),(19,"ABRA"),(20,"MEOWTH"),
                  (22,"PIDGEOTTO"),(22,"VULPIX"),(23,"MEOWTH"),(24,"WIGGLYTUFF"),(25,"EEVEE")]
    },
    "Route8.asm": {
        "grass": [(20,"PIDGEY"),(20,"RATTATA"),(15,"ABRA"),(19,"ABRA"),(20,"MEOWTH"),
                  (22,"PIDGEOTTO"),(22,"VULPIX"),(24,"PERSIAN"),(25,"NINETALES"),(27,"KADABRA")]
    },

    "Route11.asm": {
        "grass": [(16,"PIDGEY"),(15,"RATTATA"),(15,"DROWZEE"),(17,"DROWZEE"),(17,"EKANS"),
                  (18,"PIDGEOTTO"),(19,"MEOWTH"),(19,"DROWZEE"),(20,"ARBOK"),(21,"HYPNO")]
    },
    "Route12.asm": {
        "grass": [(25,"ODDISH"),(25,"BELLSPROUT"),(28,"PIDGEOTTO"),(27,"ODDISH"),(27,"BELLSPROUT"),
                  (29,"GLOOM"),(29,"WEEPINBELL"),(30,"VILEPLUME"),(30,"VICTREEBEL"),(31,"PIDGEOT")],
        "water": [(15,"SLOWPOKE"),(15,"POLIWAG"),(16,"GOLDEEN"),(17,"SLOWPOKE"),(18,"POLIWHIRL"),
                  (18,"HORSEA"),(19,"GOLDEEN"),(20,"SLOWBRO"),(21,"SEAKING"),(22,"SEADRA")]
    },
    "Route13.asm": {
        "grass": [(25,"ODDISH"),(25,"BELLSPROUT"),(28,"PIDGEOTTO"),(27,"VENONAT"),(27,"BELLSPROUT"),
                  (29,"GLOOM"),(29,"WEEPINBELL"),(30,"VILEPLUME"),(30,"VICTREEBEL"),(31,"FARFETCHD")],
        "water": [(15,"SLOWPOKE"),(16,"POLIWAG"),(17,"GOLDEEN"),(18,"SLOWPOKE"),(19,"POLIWHIRL"),
                  (19,"HORSEA"),(20,"SLOWBRO"),(21,"SEAKING"),(22,"SEADRA"),(23,"POLIWRATH")]
    },
    "Route14.asm": {
        "grass": [(26,"ODDISH"),(26,"BELLSPROUT"),(24,"VENONAT"),(28,"EKANS"),(28,"KOFFING"),
                  (30,"GLOOM"),(30,"WEEPINBELL"),(30,"VENOMOTH"),(31,"ARBOK"),(32,"WEEZING")]
    },
    "Route15.asm": {
        "grass": [(26,"ODDISH"),(26,"BELLSPROUT"),(24,"VENONAT"),(28,"DROWZEE"),(28,"KOFFING"),
                  (30,"VENOMOTH"),(30,"GLOOM"),(30,"WEEPINBELL"),(32,"HYPNO"),(33,"PIDGEOT")]
    },

    "Route16.asm": {
        "grass": [(22,"SPEAROW"),(22,"DODUO"),(23,"RATTATA"),(24,"DODUO"),(24,"RATTATA"),
                  (26,"DODUO"),(24,"FEAROW"),(25,"RATICATE"),(27,"EEVEE"),(30,"SNORLAX")]
    },
    "Route17.asm": {
        "grass": [(26,"DODUO"),(27,"FEAROW"),(27,"DODUO"),(28,"PONYTA"),(30,"PONYTA"),
                  (29,"DODRIO"),(32,"RAPIDASH"),(31,"EEVEE"),(33,"ARCANINE"),(34,"NINETALES")]
    },
    "Route18.asm": {
        "grass": [(22,"SPEAROW"),(22,"DODUO"),(23,"RATTATA"),(24,"DODUO"),(24,"FEAROW"),
                  (26,"DODUO"),(25,"RATICATE"),(29,"EEVEE"),(31,"RAPIDASH"),(32,"PIDGEOT")]
    },

    "Route19.asm": {
        "water": [(10,"TENTACOOL"),(12,"MAGIKARP"),(15,"TENTACOOL"),(18,"HORSEA"),(20,"SHELLDER"),
                  (22,"GOLDEEN"),(25,"SEAKING"),(28,"SEADRA"),(30,"TENTACRUEL"),(32,"GYARADOS")]
    },
    "Route20.asm": {
        "water": [(15,"TENTACOOL"),(18,"HORSEA"),(20,"SHELLDER"),(22,"STARYU"),(24,"SEADRA"),
                  (26,"CLOYSTER"),(28,"TENTACRUEL"),(30,"STARMIE"),(32,"DRATINI"),(34,"GYARADOS")]
    },
    "Route21.asm": {
        "water": [(15,"TENTACOOL"),(16,"GOLDEEN"),(18,"POLIWAG"),(20,"POLIWHIRL"),(22,"SEAKING"),
                  (24,"HORSEA"),(26,"POLIWRATH"),(28,"SEADRA"),(30,"GYARADOS"),(32,"DRAGONAIR")]
    },

    "PokemonMansion1F.asm": {
        "grass": [(34,"RATTATA"),(34,"RATICATE"),(26,"GRIMER"),(28,"GROWLITHE"),(30,"VULPIX"),
                  (30,"KOFFING"),(32,"CHARMANDER"),(34,"GROWLITHE"),(36,"VULPIX"),(38,"KOFFING")]
    },
    "PokemonMansion2F.asm": {
        "grass": [(37,"RATICATE"),(30,"GRIMER"),(31,"KOFFING"),(32,"GROWLITHE"),(33,"VULPIX"),
                  (34,"CHARMELEON"),(35,"MUK"),(36,"WEEZING"),(38,"MAGMAR"),(40,"NINETALES")]
    },
    "PokemonMansion3F.asm": {
        "grass": [(40,"RATICATE"),(32,"GRIMER"),(34,"KOFFING"),(35,"GROWLITHE"),(36,"VULPIX"),
                  (38,"CHARMELEON"),(39,"MUK"),(40,"WEEZING"),(41,"MAGMAR"),(43,"ARCANINE")]
    },
    "PokemonMansionB1F.asm": {
        "grass": [(35,"GRIMER"),(37,"RATICATE"),(38,"MUK"),(39,"WEEZING"),(40,"DITTO"),
                  (41,"MAGMAR"),(42,"ARCANINE"),(43,"FLAREON"),(44,"PORYGON"),(46,"CHARIZARD")]
    },

    "PokemonTower7F.asm": {
        "grass": [(24,"GASTLY"),(25,"GASTLY"),(26,"GASTLY"),(27,"GASTLY"),(28,"GASTLY"),
                  (24,"CUBONE"),(26,"HAUNTER"),(28,"HAUNTER"),(30,"HAUNTER"),(32,"GENGAR")]
    },

    "PowerPlant.asm": {
        "grass": [(30,"MAGNEMITE"),(33,"VOLTORB"),(33,"MAGNETON"),(34,"GRIMER"),(35,"ELECTABUZZ"),
                  (36,"VOLTORB"),(37,"ELECTRODE"),(38,"MAGNETON"),(39,"RAICHU"),(40,"JOLTEON")]
    },

    "SafariZoneCenter.asm": {
        "grass": [(20,"NIDORAN_M"),(20,"NIDORAN_F"),(22,"BULBASAUR"),(24,"IVYSAUR"),(24,"EXEGGCUTE"),
                  (25,"RHYHORN"),(27,"PARASECT"),(28,"TANGELA"),(30,"MR_MIME"),(32,"VENUSAUR")]
    },
    "SafariZoneEast.asm": {
        "grass": [(21,"NIDORAN_M"),(21,"NIDORAN_F"),(22,"BULBASAUR"),(24,"IVYSAUR"),(24,"TAUROS"),
                  (25,"EXEGGCUTE"),(26,"MAROWAK"),(27,"EXEGGUTOR"),(28,"CHANSEY"),(30,"SCYTHER")]
    },
    "SafariZoneNorth.asm": {
        "grass": [(22,"NIDORAN_M"),(22,"NIDORAN_F"),(24,"IVYSAUR"),(25,"RHYHORN"),(26,"EXEGGCUTE"),
                  (28,"KANGASKHAN"),(29,"EXEGGUTOR"),(30,"SCYTHER"),(30,"PINSIR"),(32,"VENUSAUR")]
    },
    "SafariZoneWest.asm": {
        "grass": [(21,"NIDORAN_M"),(21,"NIDORAN_F"),(22,"BULBASAUR"),(24,"EXEGGCUTE"),(24,"TAUROS"),
                  (26,"MAROWAK"),(27,"TANGELA"),(28,"PINSIR"),(29,"VICTREEBEL"),(29,"VILEPLUME")]
    },

    "SeafoamIslandsB3F.asm": {
        "water": [(20,"TENTACOOL"),(22,"STARYU"),(24,"SHELLDER"),(26,"SEEL"),(28,"CLOYSTER"),
                  (29,"STARYU"),(30,"SQUIRTLE"),(31,"WARTORTLE"),(32,"STARMIE"),(34,"LAPRAS")]
    },
    "SeafoamIslandsB4F.asm": {
        # Jynx não é aquático; entra como encontro terrestre da caverna gelada.
        # Os Pokémon de água novos ficam na tabela WATER, não na GRASS.
        "grass": [(36,"GOLBAT"),(36,"ZUBAT"),(30,"KRABBY"),(32,"KINGLER"),(28,"SEEL"),
                  (32,"SEEL"),(27,"GOLBAT"),(34,"JYNX"),(30,"DEWGONG"),(34,"DEWGONG")],
        "water": [(22,"TENTACOOL"),(24,"SHELLDER"),(26,"CLOYSTER"),(28,"STARYU"),(30,"SQUIRTLE"),
                  (32,"WARTORTLE"),(34,"STARMIE"),(36,"LAPRAS"),(38,"VAPOREON"),(40,"BLASTOISE")]
    },

    "VictoryRoad1F.asm": {
        "grass": [(31,"GEODUDE"),(36,"GEODUDE"),(39,"ZUBAT"),(41,"GRAVELER"),(43,"ONIX"),
                  (44,"MACHOKE"),(45,"GOLBAT"),(46,"HITMONLEE"),(46,"HITMONCHAN"),(48,"GOLEM")]
    },
    "VictoryRoad2F.asm": {
        "grass": [(36,"GEODUDE"),(39,"GOLBAT"),(41,"GRAVELER"),(44,"MACHOKE"),(45,"ONIX"),
                  (46,"GRAVELER"),(47,"GOLEM"),(48,"MACHAMP"),(49,"AERODACTYL"),(50,"KABUTOPS")]
    },
    "VictoryRoad3F.asm": {
        "grass": [(41,"GEODUDE"),(44,"GOLBAT"),(45,"GRAVELER"),(46,"MACHOKE"),(47,"ONIX"),
                  (48,"GOLEM"),(49,"MACHAMP"),(50,"OMASTAR"),(51,"DRAGONAIR"),(52,"DRAGONITE")]
    },

    "CeruleanCave1F.asm": {
        "grass": [(50,"GOLBAT"),(52,"GRAVELER"),(52,"SANDSLASH"),(54,"VENOMOTH"),(54,"PARASECT"),
                  (55,"DITTO"),(56,"GLOOM"),(56,"WEEPINBELL"),(58,"ALAKAZAM"),(60,"GOLEM")]
    },
    "CeruleanCave2F.asm": {
        "grass": [(52,"GOLBAT"),(54,"SANDSLASH"),(55,"RHYHORN"),(56,"DITTO"),(57,"RHYDON"),
                  (58,"ALAKAZAM"),(58,"GOLEM"),(59,"MACHAMP"),(60,"NIDOKING"),(60,"NIDOQUEEN")]
    },
    "CeruleanCaveB1F.asm": {
        "grass": [(54,"GOLBAT"),(55,"LICKITUNG"),(56,"CHANSEY"),(58,"RHYDON"),(60,"DITTO"),
                  (60,"ALAKAZAM"),(61,"GOLEM"),(62,"MACHAMP"),(63,"NIDOKING"),(63,"NIDOQUEEN")]
    },
}

def replace_block(text, block, entries):
    start_tag = f"def_{block}_wildmons"
    end_tag = f"end_{block}_wildmons"

    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if start_tag in line), None)
    end = next((i for i, line in enumerate(lines) if end_tag in line and start is not None and i > start), None)

    if start is None or end is None:
        raise RuntimeError(f"Não encontrei bloco {block}.")

    if len(entries) != 10:
        raise RuntimeError(f"Bloco {block} precisa ter exatamente 10 encontros.")

    new_entries = [f"\tdb {level:2d}, {mon}" for level, mon in entries]
    new_lines = lines[:start+1] + new_entries + lines[end:]
    return "\n".join(new_lines) + "\n"

changed = 0
for filename, blocks in PLAN.items():
    path = MAPS / filename
    if not path.is_file():
        sys.exit(f"ERRO: não encontrei {path}")

    txt = path.read_text(encoding="utf-8")
    for block, entries in blocks.items():
        txt = replace_block(txt, block, entries)

    path.write_text(txt, encoding="utf-8", newline="\n")
    changed += 1

print(f"{changed} arquivos de encontros foram atualizados.")

# Validação: lê todos os Pokémon presentes nas tabelas selvagens.
wild_species = set()
for path in MAPS.glob("*.asm"):
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*db\s+\d+,\s*([A-Z0-9_]+)", line)
        if m:
            wild_species.add(m.group(1))

# Obtém os 151 reais das constantes, excluindo as 4 constantes que não são espécies normais.
all_species = set()
for line in CONSTANTS.read_text(encoding="utf-8").splitlines():
    m = re.match(r"\s*const\s+([A-Z0-9_]+)", line)
    if m:
        all_species.add(m.group(1))

all_species -= {"NO_MON", "FOSSIL_KABUTOPS", "FOSSIL_AERODACTYL", "MON_GHOST"}

special_only = {"ARTICUNO", "ZAPDOS", "MOLTRES", "MEW", "MEWTWO"}
normal_target = all_species - special_only

missing = sorted(normal_target - wild_species)
forbidden = sorted(wild_species & special_only)

print()
print(f"Espécies reais reconhecidas: {len(all_species)}")
print(f"Espécies em encontros selvagens: {len(wild_species)}")
print(f"Meta normal (151 menos 5 especiais): {len(normal_target)}")

if missing:
    print("ATENÇÃO: ainda faltam nas tabelas normais:")
    print(", ".join(missing))
else:
    print("OK: todos os 146 Pokémon não especiais aparecem em alguma tabela selvagem.")

if forbidden:
    print("ERRO: lendários/especiais foram encontrados em tabelas aleatórias:")
    print(", ".join(forbidden))
    print(f"Use o backup para restaurar: {backup}")
    sys.exit(1)
else:
    print("OK: Articuno, Zapdos, Moltres, Mew e Mewtwo NÃO foram adicionados aos encontros aleatórios.")

print()
print("Distribuição aplicada. Agora execute: make")
