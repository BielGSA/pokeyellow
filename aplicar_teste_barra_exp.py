from pathlib import Path

CORE = Path("engine/battle/core.asm")

CALL_MARKER = "\thlcoord 10, 9\n\tpredef DrawHP\n"
CALL_PATCH = "\thlcoord 10, 9\n\tpredef DrawHP\n\tcall DrawPlayerExpBar\n"

ROUTINE_MARKER = "\nDrawEnemyHUDAndHPBar:\n"
ROUTINE = r'''

; Pokemon Yellow Complete - functional EXP progress bar test.
; Draws an 8-segment bar using the active party mon's real EXP progress.
; The visual tiles are still temporary (X = filled, - = empty); dedicated
; pixel graphics and smooth animation come after this calculation is proven.
DrawPlayerExpBar:
	push hl
	push de
	push bc
	push af

	; Find the active party mon's 3-byte EXP field and save its low 16 bits.
	; The EXP gained inside a single level is always below 65536, so subtracting
	; the low words is sufficient even when the total EXP crosses a bank boundary.
	ld hl, wPartyMon1 + MON_EXP + 1
	ld a, [wPlayerMonNumber]
	and a
	jr z, .gotPartyMonExp
	ld de, PARTYMON_STRUCT_LENGTH
.findPartyMonExp
	add hl, de
	dec a
	jr nz, .findPartyMonExp
.gotPartyMonExp
	ld b, [hl]
	inc hl
	ld c, [hl]
	push bc ; current total EXP low word

	; Load growth-rate data for the active species.
	ld a, [wBattleMonSpecies2]
	ld [wCurSpecies], a
	call GetMonHeader

	; Level 100 has no next-level threshold; show a full bar.
	ld a, [wBattleMonLevel]
	cp MAX_LEVEL
	jr nc, .maxLevel

	; EXP required at the start of the current level.
	ld d, a
	callfar CalcExperience
	ldh a, [hExperience + 1]
	ld b, a
	ldh a, [hExperience + 2]
	ld c, a
	push bc ; base EXP low word

	; EXP required for the next level.
	ld a, [wBattleMonLevel]
	inc a
	ld d, a
	callfar CalcExperience

	; HL = base EXP low word.
	pop hl

	; DE = EXP needed in this level = next level threshold - base threshold.
	ldh a, [hExperience + 2]
	sub l
	ld e, a
	ldh a, [hExperience + 1]
	sbc h
	ld d, a

	; BC = progress inside this level = current total EXP - base threshold.
	pop bc
	ld a, c
	sub l
	ld c, a
	ld a, b
	sbc h
	ld b, a

	; One visual segment represents approximately 1/8 of the level.
	; DE = max(1, needed / 8).
	srl d
	rr e
	srl d
	rr e
	srl d
	rr e
	ld a, d
	or e
	jr nz, .thresholdReady
	inc e
.thresholdReady

	; Count how many whole segment thresholds fit in the current progress.
	ld h, 0
.countSegments
	ld a, b
	cp d
	jr c, .segmentsReady
	jr nz, .subtractThreshold
	ld a, c
	cp e
	jr c, .segmentsReady
.subtractThreshold
	ld a, c
	sub e
	ld c, a
	ld a, b
	sbc d
	ld b, a
	inc h
	ld a, h
	cp 8
	jr c, .countSegments
.segmentsReady
	ld d, h
	jr .draw

.maxLevel
	pop bc ; discard saved current EXP
	ld d, 8

.draw
	; Temporary visual representation: EXPXXXXXXXX / EXPXXXX---- etc.
	hlcoord 9, 11
	ld a, 'E'
	ld [hli], a
	ld a, 'X'
	ld [hli], a
	ld a, 'P'
	ld [hli], a

	ld c, d ; filled segments remaining
	ld b, 8 ; total segments
.drawLoop
	ld a, c
	and a
	jr z, .emptySegment
	ld a, 'X'
	dec c
	jr .putSegment
.emptySegment
	ld a, '-'
.putSegment
	ld [hli], a
	dec b
	jr nz, .drawLoop

	pop af
	pop bc
	pop de
	pop hl
	ret
'''


def main():
    if not CORE.exists():
        raise SystemExit(f"Arquivo nao encontrado: {CORE}")

    text = CORE.read_text(encoding="utf-8")

    if "DrawPlayerExpBar:" in text:
        print("Barra funcional de EXP ja aplicada.")
        return

    if CALL_MARKER not in text:
        raise SystemExit("Nao encontrei o ponto de insercao apos DrawHP. Nenhum arquivo foi alterado.")

    text = text.replace(CALL_MARKER, CALL_PATCH, 1)

    if ROUTINE_MARKER not in text:
        raise SystemExit("Nao encontrei DrawEnemyHUDAndHPBar. Nenhum arquivo foi alterado.")

    text = text.replace(ROUTINE_MARKER, ROUTINE + ROUTINE_MARKER, 1)
    CORE.write_text(text, encoding="utf-8")
    print("Barra funcional de EXP aplicada em engine/battle/core.asm")
    print("Ela agora calcula o progresso real do Pokemon ativo em 8 segmentos.")


if __name__ == "__main__":
    main()
