from pathlib import Path

HUD = Path("engine/battle/draw_hud_pokeball_gfx.asm")
EXPERIENCE = Path("engine/battle/experience.asm")

OLD_BLOCK = '''\tld hl, GainedText\n\tcall PrintText\n\n\t; Pokemon Yellow Complete: if the Pokemon that just received EXP is the\n\t; one currently in battle, immediately redraw its EXP progress bar.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, DrawPlayerExpBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n'''

NEW_BLOCK = '''\t; Pokemon Yellow Complete: if the Pokemon that just received EXP is the\n\t; one currently in battle, redraw its EXP progress bar BEFORE the gained-EXP\n\t; message. This gives the tilemap time to reach the screen while the message\n\t; is visible, instead of only becoming noticeable in the next battle.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, DrawPlayerExpBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n\n\tld hl, GainedText\n\tcall PrintText\n'''


def main():
    if not HUD.exists():
        raise SystemExit(f"Arquivo nao encontrado: {HUD}")
    if not EXPERIENCE.exists():
        raise SystemExit(f"Arquivo nao encontrado: {EXPERIENCE}")

    hud = HUD.read_text(encoding="utf-8")
    experience = EXPERIENCE.read_text(encoding="utf-8")

    if "DrawPlayerExpBar:" not in hud:
        raise SystemExit("DrawPlayerExpBar nao encontrado no arquivo do HUD.")

    if NEW_BLOCK in experience:
        print("Atualizacao imediata da barra de EXP ja aplicada.")
    elif OLD_BLOCK in experience:
        experience = experience.replace(OLD_BLOCK, NEW_BLOCK, 1)
        EXPERIENCE.write_text(experience, encoding="utf-8")
        print("Barra de EXP agora e redesenhada antes da mensagem de EXP ganha.")
    else:
        raise SystemExit("Nao encontrei o bloco esperado de atualizacao da barra de EXP.")

    print("DrawPlayerExpBar confirmado no HUD.")


if __name__ == "__main__":
    main()
