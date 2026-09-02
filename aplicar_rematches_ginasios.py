from pathlib import Path
import shutil, sys
from datetime import datetime

ROOT=Path('.')
BACKUP=ROOT/f"backup_rematches_{datetime.now():%Y%m%d_%H%M%S}"
FILES=[
'data/trainers/parties.asm','engine/battle/read_trainer_party.asm','scripts/CeruleanGym.asm',
'scripts/VermilionGym.asm','scripts/CeladonGym.asm','scripts/FuchsiaGym.asm','scripts/SaffronGym.asm',
'scripts/CinnabarGym.asm','scripts/ViridianGym.asm','scripts/ChampionsRoom.asm',
'text/VermilionGym.asm','text/CeladonGym.asm','text/FuchsiaGym.asm','text/SaffronGym.asm','text/CinnabarGym.asm','text/ViridianGym.asm']
missing=[f for f in FILES if not (ROOT/f).exists()]
if missing:
    print('ERRO: execute este script na raiz do projeto pokeyellow.')
    print('\n'.join(' - '+x for x in missing)); sys.exit(1)
data={f:(ROOT/f).read_text() for f in FILES}

def need(f,s):
    if s not in data[f]: raise RuntimeError(f'{f}: não encontrei {s}')

def before(f,label,block,marker):
    if marker in data[f]: return
    need(f,label); data[f]=data[f].replace(label,block.rstrip()+'\n\n'+label,1)

def after_local(f,global_label,local_label,block,marker):
    if marker in data[f]: return
    s=data[f]; a=s.find(global_label)
    if a<0: raise RuntimeError(f'{f}: não encontrei {global_label}')
    b=s.find('\n'+local_label+'\n',a)
    if b<0: raise RuntimeError(f'{f}: não encontrei {local_label}')
    p=b+len('\n'+local_label+'\n')
    data[f]=s[:p]+block.rstrip()+'\n'+s[p:]

def local_text(f,global_label,before_label,block):
    s=data[f]; a=s.find(global_label)
    if a<0: raise RuntimeError(f'{f}: não encontrei {global_label}')
    b=s.find(before_label,a)
    if b<0: raise RuntimeError(f'{f}: não encontrei {before_label}')
    # Só considera .RematchText existente dentro deste bloco de líder.
    if s.find('.RematchText:',a,b)>=0: return
    data[f]=s[:b]+block.rstrip()+'\n\n'+s[b:]

# Times novos no fim do arquivo: não altera nenhum time original.
f='data/trainers/parties.asm'
if 'LtSurgeRematchData:' not in data[f]:
    data[f]=data[f].rstrip()+'''\n\n; Gym Leader rematch teams
LtSurgeRematchData:
    db $FF, 60, ELECTRODE, 61, MAGNETON, 62, ELECTABUZZ, 63, JOLTEON, 68, RAICHU, 0

ErikaRematchData:
    db $FF, 60, TANGELA, 61, VICTREEBEL, 62, EXEGGUTOR, 63, PARASECT, 64, VENUSAUR, 68, VILEPLUME, 0

KogaRematchData:
    db $FF, 60, ARBOK, 61, WEEZING, 62, TENTACRUEL, 63, MUK, 64, NIDOKING, 68, VENOMOTH, 0

SabrinaRematchData:
    db $FF, 60, MR_MIME, 61, HYPNO, 62, SLOWBRO, 63, JYNX, 64, EXEGGUTOR, 68, ALAKAZAM, 0

BlaineRematchData:
    db $FF, 60, NINETALES, 61, RAPIDASH, 62, MAGMAR, 63, FLAREON, 64, CHARIZARD, 68, ARCANINE, 0

GiovanniRematchData:
    db $FF, 60, DUGTRIO, 61, MAROWAK, 62, NIDOQUEEN, 63, NIDOKING, 64, RHYDON, 68, GOLEM, 0
'''

# ReadTrainer completo.
f='engine/battle/read_trainer_party.asm'; start='; Gym Leader rematches after becoming Champion.'; end='.normalTrainer'
need(f,start); need(f,end); s=data[f]; a=s.index(start); b=s.index(end,a)
block='''; Gym Leader rematches after becoming Champion.
        ld a, [wTrainerClass]
        cp BROCK
        jr z, .brockRematch
        cp MISTY
        jr z, .mistyRematch
        cp LT_SURGE
        jr z, .ltSurgeRematch
        cp ERIKA
        jr z, .erikaRematch
        cp KOGA
        jr z, .kogaRematch
        cp SABRINA
        jr z, .sabrinaRematch
        cp BLAINE
        jr z, .blaineRematch
        cp GIOVANNI
        jr z, .giovanniRematch
        jr .normalTrainer

.brockRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, BrockRematchData
        jr .IterateTrainer

.mistyRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, MistyRematchData
        jr .IterateTrainer

.ltSurgeRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, LtSurgeRematchData
        jr .IterateTrainer

.erikaRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, ErikaRematchData
        jr .IterateTrainer

.kogaRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, KogaRematchData
        jr .IterateTrainer

.sabrinaRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, SabrinaRematchData
        jr .IterateTrainer

.blaineRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, BlaineRematchData
        jr .IterateTrainer

.giovanniRematch
        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalTrainer
        ld hl, GiovanniRematchData
        jr .IterateTrainer

'''
data[f]=s[:a]+block+s[b:]

# Corrige a condição da Misty caso esteja invertida pela etapa anterior.
f='scripts/CeruleanGym.asm'
data[f]=data[f].replace('        CheckEventReuseA EVENT_GOT_TM11\n        jr z, .afterBeat\n','        CheckEventReuseA EVENT_GOT_TM11\n        jr nz, .afterBeat\n',1)
# Reposiciona o bloco de rematch da Misty para depois de .afterBeat, se necessário.
marker='        ; Misty rematch after becoming Champion.'
if marker in data[f]:
    s=data[f]; m=s.index(marker); e=s.index('        jr .done',m)+len('        jr .done\n')
    q=s.rfind('        CheckEvent EVENT_BEAT_CHAMPION_RIVAL\n',0,m)
    r=q if q!=-1 and 'jr z, .afterBeat' in s[q:m] else m
    data[f]=s[:r]+s[e:]
if '        ; Misty rematch after becoming Champion.' not in data[f]:
    misty='''        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalAfterBeat
        ; Misty rematch after becoming Champion.
        ld hl, .RematchText
        call PrintText
        ld hl, wStatusFlags3
        set BIT_TALKED_TO_TRAINER, [hl]
        set BIT_PRINT_END_BATTLE_TEXT, [hl]
        ld hl, CeruleanGymMistyReceivedCascadeBadgeText
        ld de, CeruleanGymMistyReceivedCascadeBadgeText
        call SaveEndBattleTextPointers
        ldh a, [hSpriteIndex]
        ld [wSpriteIndex], a
        call EngageMapTrainer
        ld a, 2
        ld [wEngagedTrainerSet], a
        call InitBattleEnemyParameters
        ld a, $2
        ld [wGymLeaderNo], a
        xor a
        ldh [hJoyHeld], a
        ld a, SCRIPT_CERULEANGYM_MISTY_REMATCH_POST_BATTLE
        ld [wCeruleanGymCurScript], a
        ld [wCurMapScript], a
        jp TextScriptEnd
.normalAfterBeat
'''
    s=data[f]; a=s.find('CeruleanGymMistyText:'); p=s.find('\n.afterBeat\n',a)
    if p<0: raise RuntimeError('Misty: .afterBeat não encontrado')
    p+=len('\n.afterBeat\n'); data[f]=s[:p]+misty+s[p:]

leaders=[
('scripts/VermilionGym.asm','text/VermilionGym.asm','VermilionGymLTSurgeText:','.got_tm24_already','.PreBattleText:','_VermilionGymLTSurgeRematchText','VermilionGymLTSurgeAfterBattleScript:','VermilionGymLTSurgeRematchPostBattle','SCRIPT_VERMILIONGYM_LT_SURGE_AFTER_BATTLE','SCRIPT_VERMILIONGYM_LT_SURGE_REMATCH_POST_BATTLE','VermilionGymResetScripts','VermilionGymLTSurgeReceivedThunderBadgeText','wVermilionGymCurScript','$3','LT.SURGE'),
('scripts/CeladonGym.asm','text/CeladonGym.asm','CeladonGymErikaText:','.afterBeat','.PreBattleText:','_CeladonGymErikaRematchText','CeladonGymErikaPostBattleScript:','CeladonGymErikaRematchPostBattle','SCRIPT_CELADONGYM_ERIKA_POST_BATTLE','SCRIPT_CELADONGYM_ERIKA_REMATCH_POST_BATTLE','CeladonGymResetScripts','.ReceivedRainbowBadgeText','wCeladonGymCurScript','$4','ERIKA'),
('scripts/FuchsiaGym.asm','text/FuchsiaGym.asm','FuchsiaGymKogaText:','.afterBeat','.BeforeBattleText:','_FuchsiaGymKogaRematchText','FuchsiaGymKogaPostBattleScript:','FuchsiaGymKogaRematchPostBattle','SCRIPT_FUCHSIAGYM_KOGA_POST_BATTLE','SCRIPT_FUCHSIAGYM_KOGA_REMATCH_POST_BATTLE','FuchsiaGymResetScripts','.ReceivedSoulBadgeText','wFuchsiaGymCurScript','$5','KOGA'),
('scripts/SaffronGym.asm','text/SaffronGym.asm','SaffronGymSabrinaText:','.afterBeat','.Text:','_SaffronGymSabrinaRematchText','SaffronGymSabrinaPostBattle:','SaffronGymSabrinaRematchPostBattle','SCRIPT_SAFFRONGYM_SABRINA_POST_BATTLE','SCRIPT_SAFFRONGYM_SABRINA_REMATCH_POST_BATTLE','SaffronGymResetScripts','.ReceivedMarshBadgeText','wSaffronGymCurScript','$6','SABRINA'),
('scripts/CinnabarGym.asm','text/CinnabarGym.asm','CinnabarGymBlaineText:','.afterBeat','.PreBattleText:','_CinnabarGymBlaineRematchText','CinnabarGymBlainePostBattleScript:','CinnabarGymBlaineRematchPostBattle','SCRIPT_CINNABARGYM_BLAINE_POST_BATTLE','SCRIPT_CINNABARGYM_BLAINE_REMATCH_POST_BATTLE','CinnabarGymResetScripts','.ReceivedVolcanoBadgeText','wCinnabarGymCurScript','$7','BLAINE'),
('scripts/ViridianGym.asm','text/ViridianGym.asm','ViridianGymGiovanniText:','.afterBeat','.PreBattleText:','_ViridianGymGiovanniRematchText','ViridianGymGiovanniPostBattle:','ViridianGymGiovanniRematchPostBattle','SCRIPT_VIRIDIANGYM_GIOVANNI_POST_BATTLE','SCRIPT_VIRIDIANGYM_GIOVANNI_REMATCH_POST_BATTLE','ViridianGymResetScripts','.ReceivedEarthBadgeText','wViridianGymCurScript','$8','GIOVANNI')]

texts={
'LT.SURGE':['    text "Hey, CHAMP!"','    line "Back for more?"','','    para "My team is fully"','    line "charged now!"','','    para "Let us battle!"','    done'],
'ERIKA':['    text "Welcome back,"','    line "CHAMPION!"','','    para "My flowers have"','    line "grown stronger."','','    para "Shall we battle?"','    done'],
'KOGA':['    text "Fwahahaha!"','    line "The CHAMPION!"','','    para "My techniques"','    line "have improved!"','','    para "Face me again!"','    done'],
'SABRINA':['    text "I knew you would"','    line "return, CHAMPION."','','    para "My powers have"','    line "grown stronger."','','    para "Let us battle."','    done'],
'BLAINE':['    text "Hah! CHAMPION!"','    line "You came back!"','','    para "My fire burns"','    line "hotter than ever!"','','    para "Let us battle!"','    done'],
'GIOVANNI':['    text "So, the CHAMPION"','    line "has returned."','','    para "I will show you"','    line "my true strength."','','    para "We battle again!"','    done']}

for sf,tf,glob,aft,beforetxt,txtsym,postorig,postnew,constorig,constnew,reset,badge,scriptvar,gymno,name in leaders:
    need(sf,glob); need(sf,postorig); need(sf,reset+':')
    if constnew not in data[sf]:
        lines=data[sf].splitlines(); ok=False
        for i,line in enumerate(lines):
            if 'dw_const' in line and constorig in line:
                lines.insert(i+1,f'        dw_const {postnew}, {constnew}'); ok=True; break
        if not ok: raise RuntimeError(f'{sf}: não encontrei {constorig}')
        data[sf]='\n'.join(lines)+'\n'
    post=f'''{postnew}:
        ld a, [wIsInBattle]
        cp LOST_BATTLE
        jp z, {reset}
        ld a, PAD_CTRL_PAD
        ld [wJoyIgnore], a
        jp {reset}'''
    before(sf,postorig,post,postnew+':')
    rem=f'''        CheckEvent EVENT_BEAT_CHAMPION_RIVAL
        jr z, .normalAfterBeat
        ; {name} rematch after becoming Champion.
        ld hl, .RematchText
        call PrintText
        ld hl, wStatusFlags3
        set BIT_TALKED_TO_TRAINER, [hl]
        set BIT_PRINT_END_BATTLE_TEXT, [hl]
        ld hl, {badge}
        ld de, {badge}
        call SaveEndBattleTextPointers
        ldh a, [hSpriteIndex]
        ld [wSpriteIndex], a
        call EngageMapTrainer
        ld a, 2
        ld [wEngagedTrainerSet], a
        call InitBattleEnemyParameters
        ld a, {gymno}
        ld [wGymLeaderNo], a
        xor a
        ldh [hJoyHeld], a
        ld a, {constnew}
        ld [{scriptvar}], a
        ld [wCurMapScript], a
        jp TextScriptEnd
.normalAfterBeat'''
    after_local(sf,glob,aft,rem,f'; {name} rematch after becoming Champion.')
    lt=f'''.RematchText:
        text_far {txtsym}
        text_end'''
    local_text(sf,glob,beforetxt,lt)
    if txtsym+'::' not in data[tf]:
        data[tf]=data[tf].rstrip()+'\n\n'+txtsym+'::\n'+'\n'.join(texts[name])+'\n'

# Giovanni reaparece ao vencer a Liga.
f='scripts/ChampionsRoom.asm'
if 'TOGGLE_VIRIDIAN_GYM_GIOVANNI' not in data[f]:
    old='\tSetEvent EVENT_BEAT_CHAMPION_RIVAL\n'
    if old not in data[f]: old='        SetEvent EVENT_BEAT_CHAMPION_RIVAL\n'
    need(f,old)
    indent='\t' if old.startswith('\t') else '        '
    new=old+indent+'ld a, TOGGLE_VIRIDIAN_GYM_GIOVANNI\n'+indent+'ld [wToggleableObjectIndex], a\n'+indent+'predef ShowObject\n'
    data[f]=data[f].replace(old,new,1)

# Backup antes da gravação.
BACKUP.mkdir(parents=True)
for f in FILES:
    dst=BACKUP/f; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/f,dst)
for f,s in data.items(): (ROOT/f).write_text(s)
print('OK: rematches aplicados para Lt. Surge, Erika, Koga, Sabrina, Blaine e Giovanni.')
print('Brock e Misty preservados; condição da Misty corrigida.')
print('Backup:',BACKUP)
print('Agora rode: make')
