from pathlib import Path

CORE = Path("engine/battle/core.asm")

CALL_MARKER = "\thlcoord 10, 9\n\tpredef DrawHP\n"
CALL_PATCH = "\thlcoord 10, 9\n\tpredef DrawHP\n\tcall DrawEXPBarVisualTest\n"

ROUTINE_MARKER = "\nDrawEnemyHUDAndHPBar:\n"
ROUTINE = r'''

; Temporary visual-only EXP bar test.
; This deliberately does NOT calculate or animate EXP yet.
; It only verifies that row 11 of the player's HUD can be used safely.
DrawEXPBarVisualTest:
	push hl
	push de
	push bc
	push af

	; Label at the left of the test bar.
	hlcoord 9, 11
	ld de, .label
	call PlaceString

	; Draw an 8-character placeholder bar.
	; Once this survives battle HUD redraws, these characters will be
	; replaced by dedicated 0..8 pixel EXP tiles and real EXP calculation.
	hlcoord 12, 11
	ld b, 8
	ld a, '-'
.loop
	ld [hli], a
	dec b
	jr nz, .loop

	pop af
	pop bc
	pop de
	pop hl
	ret

.label
	db "EXP@"
'''


def main():
    if not CORE.exists():
        raise SystemExit(f"Arquivo nao encontrado: {CORE}")

    text = CORE.read_text(encoding="utf-8")

    if "DrawEXPBarVisualTest:" in text:
        print("Teste visual da barra de EXP ja aplicado.")
        return

    if CALL_MARKER not in text:
        raise SystemExit("Nao encontrei o ponto de insercao apos DrawHP. Nenhum arquivo foi alterado.")

    text = text.replace(CALL_MARKER, CALL_PATCH, 1)

    if ROUTINE_MARKER not in text:
        raise SystemExit("Nao encontrei DrawEnemyHUDAndHPBar. Nenhum arquivo foi alterado.")

    text = text.replace(ROUTINE_MARKER, ROUTINE + ROUTINE_MARKER, 1)
    CORE.write_text(text, encoding="utf-8")
    print("Teste visual da barra de EXP aplicado em engine/battle/core.asm")
    print("Proximo passo: executar make e testar uma batalha no emulador.")


if __name__ == "__main__":
    main()
