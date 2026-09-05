from pathlib import Path

HUD = Path("engine/battle/draw_hud_pokeball_gfx.asm")
EXPERIENCE = Path("engine/battle/experience.asm")


def main():
    """Validate the EXP-bar integration without patching core.asm.

    The branch already has the real DrawPlayerExpBar routine in
    engine/battle/draw_hud_pokeball_gfx.asm and the EXP-gain refresh hook in
    engine/battle/experience.asm.  An older version of this helper inserted a
    second routine into core.asm, which caused RGBDS to report a duplicate
    symbol.  Keeping this script as a validation step makes the Makefile safe
    and idempotent while preserving the isolated exp-bar-test workflow.
    """
    if not HUD.exists():
        raise SystemExit(f"Arquivo nao encontrado: {HUD}")
    if not EXPERIENCE.exists():
        raise SystemExit(f"Arquivo nao encontrado: {EXPERIENCE}")

    hud = HUD.read_text(encoding="utf-8")
    experience = EXPERIENCE.read_text(encoding="utf-8")

    if "DrawPlayerExpBar:" not in hud:
        raise SystemExit("DrawPlayerExpBar nao encontrado no arquivo do HUD.")

    if "ld hl, DrawPlayerExpBar" not in experience:
        raise SystemExit("Hook de atualizacao da barra apos ganho de EXP nao encontrado.")

    print("Barra de EXP funcional encontrada no HUD; nenhum patch em core.asm necessario.")
    print("Hook de atualizacao apos ganho de EXP confirmado.")


if __name__ == "__main__":
    main()
