from pathlib import Path

HUD = Path("engine/battle/draw_hud_pokeball_gfx.asm")
EXPERIENCE = Path("engine/battle/experience.asm")

OLD_BLOCK = '''\tld hl, GainedText\n\tcall PrintText\n\n\t; Pokemon Yellow Complete: if the Pokemon that just received EXP is the\n\t; one currently in battle, immediately redraw its EXP progress bar.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, DrawPlayerExpBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n'''

ANIMATED_BLOCK = '''\t; Pokemon Yellow Complete: animate the active Pokemon's EXP bar before\n\t; printing the gained-EXP message. The animation advances one pixel per\n\t; frame from the bar currently on screen to the newly calculated value.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, AnimatePlayerExpBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n\n\tld hl, GainedText\n\tcall PrintText\n'''

ANIMATION_ROUTINES = r'''

; Pokemon Yellow Complete - gradual EXP bar animation.
; Reads the bar that is already visible, asks DrawPlayerExpBar for the new
; target, restores the old value, then advances one pixel per frame.
AnimatePlayerExpBar:
	push af
	push bc
	push de
	push hl

	call ReadPlayerExpBarPixels
	ld c, e ; C = old on-screen pixel length

	; Draw once to discover the target produced by the real EXP calculation.
	call DrawPlayerExpBar
	call ReadPlayerExpBarPixels
	ld b, e ; B = new target pixel length

	; If the new calculation wrapped below the old bar, EXP crossed a level
	; boundary. Fill to the end first; the normal level-up HUD redraw will then
	; show the leftover EXP for the new level.
	ld a, b
	cp c
	jr nc, .targetReady
	ld b, 48
.targetReady

	; Put the old bar back before starting the visible animation.
	ld e, c
	call DrawPlayerExpBarPixels
	ld a, 1
	ldh [hAutoBGTransferEnabled], a

.animateLoop
	ld a, e
	cp b
	jr nc, .done
	inc e
	push bc
	push de
	call DrawPlayerExpBarPixels
	call DelayFrame
	pop de
	pop bc
	jr .animateLoop

.done
	pop hl
	pop de
	pop bc
	pop af
	ret

; Return the currently displayed 6-tile EXP bar length in E (0..48 pixels).
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

    if "AnimatePlayerExpBar:" not in hud:
        if ROUTINE_MARKER not in hud:
            raise SystemExit("Ponto de insercao da animacao nao encontrado no HUD.")
        hud = hud.replace(ROUTINE_MARKER, ANIMATION_ROUTINES + ROUTINE_MARKER, 1)
        HUD.write_text(hud, encoding="utf-8")
        print("Rotina de animacao gradual da barra de EXP aplicada.")
    else:
        print("Rotina de animacao gradual da barra de EXP ja aplicada.")

    if ANIMATED_BLOCK in experience:
        print("Hook animado da barra de EXP ja aplicado.")
    elif OLD_BLOCK in experience:
        experience = experience.replace(OLD_BLOCK, ANIMATED_BLOCK, 1)
        EXPERIENCE.write_text(experience, encoding="utf-8")
        print("Ganho de EXP agora chama a animacao gradual antes da mensagem.")
    else:
        raise SystemExit("Nao encontrei o bloco esperado de atualizacao da barra de EXP.")

    print("A barra avanca um pixel por frame ate o novo progresso.")


if __name__ == "__main__":
    main()
