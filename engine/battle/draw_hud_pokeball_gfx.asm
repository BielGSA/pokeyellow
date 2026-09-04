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

; Draw the active Pokemon's progress through its current level.
; EXP is stored as a 3-byte cumulative value. Validate the full 24-bit value
; first, then use the low-word differences with the game's native 48-pixel
; HP-bar scaler. A level-to-level interval fits in 16 bits in Gen 1.
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

	; Save cumulative EXP required for the current level on the stack.
	ld a, [wBattleMonLevel]
	ld d, a
	callfar CalcExperience
	ldh a, [hExperience]
	push af
	ldh a, [hExperience + 1]
	push af
	ldh a, [hExperience + 2]
	push af

	; Save cumulative EXP required for the next level in wBuffer+3..5.
	ld a, [wBattleMonLevel]
	inc a
	ld d, a
	callfar CalcExperience
	ld hl, wBuffer + 3
	ldh a, [hExperience]
	ld [hli], a
	ldh a, [hExperience + 1]
	ld [hli], a
	ldh a, [hExperience + 2]
	ld [hl], a

	; Restore current-level threshold into wBuffer..2.
	pop af
	ld [wBuffer + 2], a
	pop af
	ld [wBuffer + 1], a
	pop af
	ld [wBuffer], a

	; Point HL at the active party Pokemon's 3-byte cumulative EXP.
	ld a, [wPlayerMonNumber]
	ld hl, wPartyMon1
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes
	ld bc, MON_EXP
	add hl, bc

	; The mon EXP must be >= the current-level threshold.
	ld a, [wBuffer]
	ld b, a
	ld a, [hli]
	cp b
	jr c, .invalidRange
	jr nz, .aboveCurrentHigh
	ld a, [wBuffer + 1]
	ld b, a
	ld a, [hli]
	cp b
	jr c, .invalidRange
	jr nz, .aboveCurrentMid
	ld a, [wBuffer + 2]
	ld b, a
	ld a, [hl]
	cp b
	jr c, .invalidRange
	jr .currentRangeOK
.aboveCurrentHigh
	inc hl
.aboveCurrentMid
	inc hl
.currentRangeOK

	; Rebuild the pointer and require mon EXP < next-level threshold.
	ld a, [wPlayerMonNumber]
	ld hl, wPartyMon1
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes
	ld bc, MON_EXP
	add hl, bc
	ld a, [wBuffer + 3]
	ld b, a
	ld a, [hli]
	cp b
	jr c, .belowNext
	jr nz, .invalidRange
	ld a, [wBuffer + 4]
	ld b, a
	ld a, [hli]
	cp b
	jr c, .belowNext
	jr nz, .invalidRange
	ld a, [wBuffer + 5]
	ld b, a
	ld a, [hl]
	cp b
	jr nc, .invalidRange
.belowNext

	; BC = progress since the current-level threshold (low 16 bits).
	ld a, [wPlayerMonNumber]
	ld hl, wPartyMon1
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes
	ld bc, MON_EXP + 1
	add hl, bc
	ld a, [wBuffer + 2]
	ld e, a
	ld a, [hl]
	inc hl
	ld c, a
	ld a, [hl]
	sub e
	ld c, a
	ld a, [wBuffer + 1]
	ld d, a
	dec hl
	ld a, [hl]
	sbc d
	ld b, a

	; DE = EXP interval from current level to next level (low 16 bits).
	ld a, [wBuffer + 5]
	ld e, a
	ld a, [wBuffer + 2]
	ld h, a
	ld a, e
	sub h
	ld e, a
	ld a, [wBuffer + 4]
	ld d, a
	ld a, [wBuffer + 1]
	ld h, a
	ld a, d
	sbc h
	ld d, a

	ld a, b
	or c
	jr z, .empty
	predef HPBarLength
	jr .restoreAndDraw

.invalidRange
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
