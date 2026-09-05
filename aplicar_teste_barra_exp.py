from pathlib import Path

HUD = Path("engine/battle/draw_hud_pokeball_gfx.asm")
EXPERIENCE = Path("engine/battle/experience.asm")

OLD_BLOCK = '''\tld hl, GainedText\n\tcall PrintText\n\n\t; Pokemon Yellow Complete: if the Pokemon that just received EXP is the\n\t; one currently in battle, immediately redraw its EXP progress bar.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, DrawPlayerExpBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n'''

ANIMATED_BLOCK = '''\t; Pokemon Yellow Complete: animate the active Pokemon's EXP bar before\n\t; printing the gained-EXP message.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, AnimatePlayerExpBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n\n\tld hl, GainedText\n\tcall PrintText\n'''

ANIMATION_ROUTINES = r'''

; Pokemon Yellow Complete - gradual EXP bar animation.
; The Gen 1 automatic BG transfer can update the tilemap in chunks across
; VBlanks. Keep auto transfer enabled and wait three VBlanks for each pixel so
; every visible step reaches VRAM instead of only appearing on the next HUD.
AnimatePlayerExpBar:
	push af
	push bc
	push de
	push hl

	call ReadPlayerExpBarPixels
	ld c, e ; C = old on-screen pixel length

	; Calculate/draw the new target without waiting for a frame, then read it
	; back from the tilemap before restoring the old visible value.
	call DrawPlayerExpBar
	call ReadPlayerExpBarPixels
	ld b, e ; B = new target pixel length

	; EXP crossing a level boundary makes DrawPlayerExpBar return an empty bar
	; until the battle-mon level is updated. In that case animate to full first.
	ld a, b
	cp c
	jr nc, .targetReady
	ld b, 48
.targetReady

	; Restore the old bar and explicitly enable automatic BG-map transfers.
	ld e, c
	call DrawPlayerExpBarPixels
	ld a, 1
	ldh [hAutoBGTransferEnabled], a
	call Delay3

.animateLoop
	ld a, e
	cp b
	jr nc, .done
	inc e
	push bc
	push de
	call DrawPlayerExpBarPixels
	; Three VBlanks guarantee the HUD row is transferred before next pixel.
	call Delay3
	pop de
	pop bc
	jr .animateLoop

.done
	; Leave the final value on screen long enough for the last transfer too.
	call Delay3
	pop hl
	pop de
	pop bc
	pop af
	ret

; Return the current 6-tile EXP bar length in E (0..48 pixels).
ReadPlayerExpBarPixels:
	hlcoord 11, 11
	ld b, 6
	ld e, 0
.loop
	ld a, [hli]
	cp $63
	jr c, .next
	cp $6c
	jr nc, .next
	sub $63
	add e
	ld e, a
.next
	dec b
	jr nz, .loop
	ret

; Draw exactly E pixels into the 6 EXP-bar tiles.
DrawPlayerExpBarPixels:
	hlcoord 11, 11
	ld d, 6
	ld a, e
.fullTiles
	cp 8
	jr c, .partialTile
	sub 8
	ld [hl], $6b
	inc hl
	dec d
	jr nz, .fullTiles
	ret
.partialTile
	and a
	jr z, .emptyTiles
	add $63
	ld [hli], a
	dec d
.emptyTiles
	ld a, d
	and a
	ret z
	ld a, $63
.emptyLoop
	ld [hli], a
	dec d
	jr nz, .emptyLoop
	ret
'''

ROUTINE_MARKER = "\nPlayerBattleHUDGraphicsTiles:\n"


def main():
    if not HUD.exists():
        raise SystemExit(f"Arquivo nao encontrado: {HUD}")
    if not EXPERIENCE.exists():
        raise SystemExit(f"Arquivo nao encontrado: {EXPERIENCE}")

    hud = HUD.read_text(encoding="utf-8")
    experience = EXPERIENCE.read_text(encoding="utf-8")

    if "DrawPlayerExpBar:" not in hud:
        raise SystemExit("DrawPlayerExpBar nao encontrado no arquivo do HUD.")

    # CI builds start from clean source, but keep this idempotent in case the
    # workspace already contains the previous one-frame animation.
    start = hud.find("\n; Pokemon Yellow Complete - gradual EXP bar animation.\n")
    marker = hud.find(ROUTINE_MARKER)
    if start != -1 and marker != -1 and start < marker:
        hud = hud[:start] + ANIMATION_ROUTINES + hud[marker:]
        HUD.write_text(hud, encoding="utf-8")
        print("Rotina gradual atualizada para transferir cada passo para a tela.")
    elif "AnimatePlayerExpBar:" not in hud:
        if ROUTINE_MARKER not in hud:
            raise SystemExit("Ponto de insercao da animacao nao encontrado no HUD.")
        hud = hud.replace(ROUTINE_MARKER, ANIMATION_ROUTINES + ROUTINE_MARKER, 1)
        HUD.write_text(hud, encoding="utf-8")
        print("Rotina de animacao gradual da barra de EXP aplicada.")
    else:
        print("Rotina de animacao gradual ja esta atualizada.")

    if ANIMATED_BLOCK in experience:
        print("Hook animado da barra de EXP ja aplicado.")
    elif OLD_BLOCK in experience:
        experience = experience.replace(OLD_BLOCK, ANIMATED_BLOCK, 1)
        EXPERIENCE.write_text(experience, encoding="utf-8")
        print("Ganho de EXP agora chama a animacao gradual antes da mensagem.")
    else:
        raise SystemExit("Nao encontrei o bloco esperado de atualizacao da barra de EXP.")

    print("Cada pixel da barra agora permanece por tres VBlanks para ficar visivel.")


if __name__ == "__main__":
    main()
