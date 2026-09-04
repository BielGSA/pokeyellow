DrawAllPokeballs:
	call LoadPartyPokeballGfx
	call SetupOwnPartyPokeballs
	ld a, [wIsInBattle]
	dec a
	ret z ; return if wild pokémon
	jp SetupEnemyPartyPokeballs

DrawEnemyPokeballs:
	call LoadPartyPokeballGfx
	jp SetupEnemyPartyPokeballs

LoadPartyPokeballGfx:
	ld de, PokeballTileGraphics
	ld hl, vSprites tile $31
	lb bc, BANK(PokeballTileGraphics), (PokeballTileGraphicsEnd - PokeballTileGraphics) / TILE_SIZE
	jp CopyVideoData

SetupOwnPartyPokeballs:
	call PlacePlayerHUDTiles
	ld hl, wPartyMons
	ld de, wPartyCount
	call SetupPokeballs
	ld a, $60
	ld hl, wBaseCoordX
	ld [hli], a
	ld [hl], a
	ld a, 8
	ld [wHUDPokeballGfxOffsetX], a
	xor a
	ld [wdef4], a
	ld hl, wShadowOAM
	jp WritePokeballOAMData

SetupEnemyPartyPokeballs:
	call PlaceEnemyHUDTiles
	ld hl, wEnemyMons
	ld de, wEnemyPartyCount
	call SetupPokeballs
	ld hl, wBaseCoordX
	ld a, $48
	ld [hli], a
	ld [hl], $20
	ld a, -8
	ld [wHUDPokeballGfxOffsetX], a
	ld a, $1
	ld [wdef4], a
	ld hl, wShadowOAMSprite06
	jp WritePokeballOAMData

SetupPokeballs:
	ld a, [de]
	push af
	ld de, wBuffer
	ld c, PARTY_LENGTH
	ld a, $34 ; empty pokeball
.emptyloop
	ld [de], a
	inc de
	dec c
	jr nz, .emptyloop
	pop af
	ld de, wBuffer
.monloop
	push af
	call PickPokeball
	inc de
	pop af
	dec a
	jr nz, .monloop
	ret

PickPokeball:
	inc hl
	ld a, [hli]
	and a
	jr nz, .alive
	ld a, [hl]
	and a
	ld b, $33 ; crossed ball (fainted)
	jr z, .done_fainted
.alive
	inc hl
	inc hl
	ld a, [hl] ; status
	and a
	ld b, $32 ; black ball (status)
	jr nz, .done
	dec b ; regular ball
	jr .done
.done_fainted
	inc hl
	inc hl
.done
	ld a, b
	ld [de], a
	ld bc, PARTYMON_STRUCT_LENGTH - MON_STATUS
	add hl, bc ; next mon struct
	ret

WritePokeballOAMData:
	ld de, wBuffer
	ld c, PARTY_LENGTH
.loop
	ld a, [wBaseCoordY]
	ld [hli], a
	ld a, [wBaseCoordX]
	ld [hli], a
	ld a, [de]
	ld [hli], a
	ld a, [wdef4]
	ld [hli], a
	ld a, [wBaseCoordX]
	ld b, a
	ld a, [wHUDPokeballGfxOffsetX]
	add b
	ld [wBaseCoordX], a
	inc de
	dec c
	jr nz, .loop
	ret

PlacePlayerHUDTiles:
	ld hl, PlayerBattleHUDGraphicsTiles
	ld de, wHUDGraphicsTiles
	ld bc, wHUDGraphicsTilesEnd - wHUDGraphicsTiles
	call CopyData
	hlcoord 18, 10
	ld de, -1
	call PlaceHUDTiles
	jp DrawPlayerExpBar

; Pokemon Yellow Complete: show the active Pokemon's progress toward its
; next level as a six-tile (48 pixel) bar in the bottom edge of its HUD.
; The existing HP-bar fill tiles are reused so the addition matches Gen 1.
DrawPlayerExpBar:
	ld a, [wBattleMonSpecies]
	and a
	ret z
	ld a, [wBattleMonLevel]
	and a
	ret z
	cp MAX_LEVEL
	jr z, .maxLevel

	ld a, [wCurSpecies]
	push af
	ld a, [wBattleMonSpecies]
	ld [wCurSpecies], a
	call GetMonHeader

	; Save cumulative EXP required for the current level.
	ld a, [wBattleMonLevel]
	ld d, a
	callfar CalcExperience
	ld hl, wBuffer
	ldh a, [hExperience]
	ld [hli], a
	ldh a, [hExperience + 1]
	ld [hli], a
	ldh a, [hExperience + 2]
	ld [hl], a

	; Copy active party Pokemon's cumulative EXP into scratch space.
	ld a, [wPlayerMonNumber]
	ld hl, wPartyMon1
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes
	ld bc, MON_EXP
	add hl, bc
	ld de, wBuffer + 3
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hl]
	ld [de], a

	; BC = progress made since the current level threshold.
	ld hl, wBuffer + 2
	ld a, [wBuffer + 5]
	sub [hl]
	ld c, a
	dec hl
	ld a, [wBuffer + 4]
	sbc [hl]
	ld b, a

	; DE = EXP interval between this level and the next.
	ld a, [wBattleMonLevel]
	inc a
	ld d, a
	callfar CalcExperience
	ld hl, wBuffer + 2
	ldh a, [hExperience + 2]
	sub [hl]
	ld e, a
	dec hl
	ldh a, [hExperience + 1]
	sbc [hl]
	ld d, a

	ld a, b
	or c
	jr z, .empty
	predef HPBarLength ; BC / DE scaled to 48 pixels, result in E
	jr .restoreAndDraw
.empty
	ld e, 0
.restoreAndDraw
	pop af
	ld [wCurSpecies], a
	and a
	call nz, GetMonHeader
	jr .draw

.maxLevel
	ld e, 48
.draw
	hlcoord 11, 11
	ld d, 6
	ld a, e
.drawFullTiles
	cp 8
	jr c, .partialTile
	sub 8
	ld [hl], $6b ; full HP-bar segment
	inc hl
	dec d
	jr nz, .drawFullTiles
	ret
.partialTile
	and a
	jr z, .emptyTiles
	add $63 ; $64-$6a are 1-7 pixel HP-bar segments
	ld [hli], a
	dec d
.emptyTiles
	ld a, d
	and a
	ret z
	ld a, $63 ; empty HP-bar segment
.emptyTileLoop
	ld [hli], a
	dec d
	jr nz, .emptyTileLoop
	ret

PlayerBattleHUDGraphicsTiles:
; The tile numbers for specific parts of the battle display for the player's pokemon
	db $73 ; unused ($73 is hardcoded into the routine that uses these bytes)
	db $77 ; lower-right corner tile of the HUD
	db $6F ; lower-left triangle tile of the HUD

PlaceEnemyHUDTiles:
	ld hl, EnemyBattleHUDGraphicsTiles
	ld de, wHUDGraphicsTiles
	ld bc, wHUDGraphicsTilesEnd - wHUDGraphicsTiles
	call CopyData
	hlcoord 1, 2
	ld de, $1
	jr PlaceHUDTiles

EnemyBattleHUDGraphicsTiles:
; The tile numbers for specific parts of the battle display for the enemy
	db $73 ; unused ($73 is hardcoded into the routine that uses these bytes)
	db $74 ; lower-left corner tile of the HUD
	db $78 ; lower-right triangle tile of the HUD

PlaceHUDTiles:
	ld [hl], $73
	ld bc, SCREEN_WIDTH
	add hl, bc
	ld a, [wHUDCornerTile] ; leftmost tile
	ld [hl], a
	ld a, 8
.loop
	add hl, de
	ld [hl], $76
	dec a
	jr nz, .loop
	add hl, de
	ld a, [wHUDTriangleTile] ; rightmost tile
	ld [hl], a
	ret

SetupPlayerAndEnemyPokeballs:
	call LoadPartyPokeballGfx
	ld hl, wPartyMons
	ld de, wPartyCount
	call SetupPokeballs
	ld hl, wBaseCoordX
	ld a, $50
	ld [hli], a
	ld [hl], $40
	ld a, 8
	ld [wHUDPokeballGfxOffsetX], a
	xor a
	ld [wdef4], a
	ld hl, wShadowOAM
	call WritePokeballOAMData
	ld hl, wEnemyMons
	ld de, wEnemyPartyCount
	call SetupPokeballs
	ld hl, wBaseCoordX
	ld a, $50
	ld [hli], a
	ld [hl], $68
	ld a, $1
	ld [wdef4], a
	ld hl, wShadowOAMSprite06
	jp WritePokeballOAMData

; four tiles: pokeball, black pokeball (status ailment), crossed out pokeball (fainted) and pokeball slot (no mon)
PokeballTileGraphics::
	INCBIN "gfx/battle/balls.2bpp"
PokeballTileGraphicsEnd:
