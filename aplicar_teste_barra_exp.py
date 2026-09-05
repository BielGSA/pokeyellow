from pathlib import Path

HUD = Path("engine/battle/draw_hud_pokeball_gfx.asm")
EXPERIENCE = Path("engine/battle/experience.asm")
WRAM = Path("ram/wram.asm")

OLD_BLOCK = '''\tld hl, GainedText\n\tcall PrintText\n\n\t; Pokemon Yellow Complete: if the Pokemon that just received EXP is the\n\t; one currently in battle, immediately redraw its EXP progress bar.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, DrawPlayerExpBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n'''

ADD_EXP_MARKER = '''; add the gained exp to the party mon's exp\n\tld b, [hl]\n'''
ADD_EXP_REPLACEMENT = '''; Pokemon Yellow Complete: save the active Pokemon's EXP-bar position BEFORE\n; cumulative EXP changes. Preserve HL because it points into the current\n; party-mon structure. The battle-core routine recalculates the bar from the\n; real current EXP instead of trusting whatever tiles happen to be on screen.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipCaptureOldExpBar\n\tpush hl\n\tld hl, CapturePlayerExpBarPixels\n\tcall CallBattleCore\n\tpop hl\n.skipCaptureOldExpBar\n\n; add the gained exp to the party mon's exp\n\tld b, [hl]\n'''

ANIMATED_BLOCK = '''\t; Pokemon Yellow Complete: cumulative EXP is now updated, so animate the\n\t; active Pokemon from the saved old bar position to the new target.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, AnimatePlayerExpBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n\n\tld hl, GainedText\n\tcall PrintText\n'''

WRAM_OLD = '''; the address of the menu cursor's current location within wTileMap\nwMenuCursorLocation:: dw\n\n\tds 2\n'''
WRAM_NEW = '''; the address of the menu cursor's current location within wTileMap\nwMenuCursorLocation:: dw\n\n; Pokemon Yellow Complete: dedicated scratch byte for EXP-bar animation.\n; This replaces one previously unnamed reserved byte, so WRAM layout does not move.\nwExpBarOldPixels:: db\n\tds 1\n'''

ANIMATION_ROUTINES = r'''

; Pokemon Yellow Complete - gradual EXP bar animation.
; Before EXP is added, rebuild the active bar from the Pokemon's real current
; cumulative EXP, then save that pixel length. This avoids depending on stale
; or overwritten HUD tiles between trainer/wild battles.
CapturePlayerExpBarPixels:
	push af
	push bc
	push de
	push hl
	call DrawPlayerExpBar
	call ReadPlayerExpBarPixels
	ld a, e
	ld [wExpBarOldPixels], a
	pop hl
	pop de
	pop bc
	pop af
	ret

AnimatePlayerExpBar:
	push af
	push bc
	push de
	push hl

	; EXP bytes have already been updated here. Draw once only to calculate the
	; new target, then restore the saved old position before visible animation.
	call DrawPlayerExpBar
	call ReadPlayerExpBarPixels
	ld b, e ; B = new target pixels
	ld a, [wExpBarOldPixels]
	ld c, a ; C = old pixels

	; If target wrapped below old, a level boundary was crossed. Fill the current
	; level bar to its end; the normal level-up HUD redraw handles the next level.
	ld a, b
	cp c
	jr nc, .targetReady
	ld b, 48
.targetReady

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
	call Delay3
	pop de
	pop bc
	jr .animateLoop

.done
	call Delay3
	pop hl
	pop de
	pop bc
	pop af
	ret

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
    for path in (HUD, EXPERIENCE, WRAM):
        if not path.exists():
            raise SystemExit(f"Arquivo nao encontrado: {path}")

    hud = HUD.read_text(encoding="utf-8")
    experience = EXPERIENCE.read_text(encoding="utf-8")
    wram = WRAM.read_text(encoding="utf-8")

    if "DrawPlayerExpBar:" not in hud:
        raise SystemExit("DrawPlayerExpBar nao encontrado no HUD.")

    # Reserve one existing unnamed WRAM byte without changing any addresses.
    if "wExpBarOldPixels:: db" not in wram:
        if WRAM_OLD not in wram:
            raise SystemExit("Byte WRAM reservado esperado nao encontrado.")
        wram = wram.replace(WRAM_OLD, WRAM_NEW, 1)
        WRAM.write_text(wram, encoding="utf-8")

    # Replace/insert animation routines in the build workspace.
    start = hud.find("\n; Pokemon Yellow Complete - gradual EXP bar animation.\n")
    marker = hud.find(ROUTINE_MARKER)
    if start != -1 and marker != -1 and start < marker:
        hud = hud[:start] + ANIMATION_ROUTINES + hud[marker:]
    elif "CapturePlayerExpBarPixels:" not in hud:
        if ROUTINE_MARKER not in hud:
            raise SystemExit("Ponto de insercao da animacao nao encontrado no HUD.")
        hud = hud.replace(ROUTINE_MARKER, ANIMATION_ROUTINES + ROUTINE_MARKER, 1)
    HUD.write_text(hud, encoding="utf-8")

    # Move the EXP-bar capture to before the actual party EXP write.
    if ADD_EXP_REPLACEMENT not in experience:
        if ADD_EXP_MARKER not in experience:
            raise SystemExit("Ponto de escrita da EXP nao encontrado.")
        experience = experience.replace(ADD_EXP_MARKER, ADD_EXP_REPLACEMENT, 1)

    # The clean branch has the original static refresh after GainedText.
    if ANIMATED_BLOCK not in experience:
        if OLD_BLOCK not in experience:
            raise SystemExit("Hook original da barra de EXP nao encontrado.")
        experience = experience.replace(OLD_BLOCK, ANIMATED_BLOCK, 1)

    EXPERIENCE.write_text(experience, encoding="utf-8")
    print("EXP bar: old pixels recalculated from real current EXP before every gain; animation runs after write.")


if __name__ == "__main__":
    main()
