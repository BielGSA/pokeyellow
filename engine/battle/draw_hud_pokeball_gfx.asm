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

	; Current level cumulative EXP. Keep the low two bytes on the stack so
	; the next CalcExperience call cannot clobber our scratch data.
	ld a, [wBattleMonLevel]
	ld d, a
	callfar CalcExperience
	ldh a, [hExperience + 1]
	push af
	ldh a, [hExperience + 2]
	push af

	; Next level cumulative EXP.
	ld a, [wBattleMonLevel]
	inc a
	ld d, a
	callfar CalcExperience
	ldh a, [hExperience + 1]
	ld b, a
	ldh a, [hExperience + 2]
	ld c, a

	; Restore current-level threshold low word into DE.
	pop af
	ld e, a
	pop af
	ld d, a

	; Save interval = next - current in wBuffer[0..1].
	ld a, c
	sub e
	ld [wBuffer + 1], a
	ld a, b
	sbc d
	ld [wBuffer], a

	; Read active party Pokemon cumulative EXP low word.
	ld a, [wPlayerMonNumber]
	ld hl, wPartyMon1
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes
	ld bc, MON_EXP + 1
	add hl, bc
	ld a, [hli]
	ld b, a
	ld c, [hl]

	; BC = current progress = mon EXP - current-level threshold.
	ld a, c
	sub e
	ld c, a
	ld a, b
	sbc d
	ld b, a

	; DE = interval to next level.
	ld a, [wBuffer]
	ld d, a
	ld a, [wBuffer + 1]
	ld e, a

	ld a, b
	or c
	jr z, .empty
	predef HPBarLength
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
	ld [hl], $6b
	inc hl
	dec d
	jr nz, .drawFullTiles
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
.emptyTileLoop
	ld [hli], a
	dec d
	jr nz, .emptyTileLoop
	ret

PlayerBattleHUDGraphicsTiles:
	db $73
	db $77
	db $6F

PlaceEnemyHUDTiles:
	ld hl, EnemyBattleHUDGraphicsTiles
	ld de, wHUDGraphicsTiles
	ld bc, wHUDGraphicsTilesEnd - wHUDGraphicsTiles
	call CopyData
	hlcoord 1, 2
	ld de, $1
	jr PlaceHUDTiles

EnemyBattleHUDGraphicsTiles:
	db $73
	db $74
	db $78

PlaceHUDTiles:
	ld [hl], $73
	ld bc, SCREEN_WIDTH
	add hl, bc
	ld a, [wHUDCornerTile]
	ld [hl], a
	ld a, 8
.loop
	add hl, de
	ld [hl], $76
	dec a
	jr nz, .loop
	add hl, de
	ld a, [wHUDTriangleTile]
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

PokeballTileGraphics::
	INCBIN "gfx/battle/balls.2bpp"
PokeballTileGraphicsEnd:
