from pathlib import Path

HUD = Path("engine/battle/draw_hud_pokeball_gfx.asm")
EXPERIENCE = Path("engine/battle/experience.asm")

OLD_BLOCK = '''\tld hl, GainedText\n\tcall PrintText\n\n\t; Pokemon Yellow Complete: if the Pokemon that just received EXP is the\n\t; one currently in battle, immediately redraw its EXP progress bar.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, DrawPlayerExpBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n'''

FIXED_BLOCK = '''\t; Pokemon Yellow Complete: if the Pokemon that just received EXP is the\n\t; one currently in battle, rebuild the whole player HUD before printing the\n\t; gained-EXP message. DrawPlayerHUDAndHPBar re-enables automatic BG transfer,\n\t; so the new EXP bar reaches VRAM during this battle instead of waiting until\n\t; the next HUD setup.\n\tld a, [wWhichPokemon]\n\tld b, a\n\tld a, [wPlayerMonNumber]\n\tcp b\n\tjr nz, .skipExpBarRefresh\n\tld hl, DrawPlayerHUDAndHPBar\n\tcall CallBattleCore\n.skipExpBarRefresh\n\n\tld hl, GainedText\n\tcall PrintText\n'''


def main():
    if not HUD.exists():
        raise SystemExit(f"Arquivo nao encontrado: {HUD}")
    if not EXPERIENCE.exists():
        raise SystemExit(f"Arquivo nao encontrado: {EXPERIENCE}")

    hud = HUD.read_text(encoding="utf-8")
    experience = EXPERIENCE.read_text(encoding="utf-8")

    if "DrawPlayerExpBar:" not in hud:
        raise SystemExit("DrawPlayerExpBar nao encontrado no arquivo do HUD.")

    if FIXED_BLOCK in experience:
        print("Refresh visivel da barra de EXP ja aplicado.")
    elif OLD_BLOCK in experience:
        experience = experience.replace(OLD_BLOCK, FIXED_BLOCK, 1)
        EXPERIENCE.write_text(experience, encoding="utf-8")
        print("HUD do jogador agora e redesenhado antes da mensagem de EXP.")
        print("Transferencia do novo estado da barra para a tela sera feita na mesma batalha.")
    else:
        raise SystemExit("Nao encontrei o bloco esperado de atualizacao da barra de EXP.")

    print("DrawPlayerExpBar confirmado no HUD.")


if __name__ == "__main__":
    main()
