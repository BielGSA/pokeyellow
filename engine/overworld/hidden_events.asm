; Pokemon Yellow Complete: use common field HMs directly from the overworld.
; Called while the player presses A, before normal hidden-event/sign handling.
; Carry set = a field move was used and the A press was consumed.
TryContextFieldMove::
	predef GetTileAndCoordsInFrontOfPlayer

; CUT: A while facing a cut tree/grass, provided the Cascade Badge is owned
; and any party Pokemon knows Cut.
	ld a, [wObtainedBadges]
	bit BIT_CASCADEBADGE, a
	jr z, .trySurf
	ld a, [wCurMapTileset]
	and a ; OVERWORLD
	jr z, .cutOverworld
	cp GYM
	jr nz, .trySurf
	ld a, [wTileInFrontOfPlayer]
	cp $50 ; gym cut tree
	jr nz, .trySurf
	jr .findCutUser
.cutOverworld
	ld a, [wTileInFrontOfPlayer]
	cp $3d ; cut tree
	jr z, .findCutUser
	cp $52 ; grass
	jr nz, .trySurf
.findCutUser
	ld b, CUT
	farcall FindPartyMonWithFieldMove
	jr nc, .trySurf
	predef UsedCut
	ld a, [wActionResultOrTookBattleTurn]
	and a
	jr z, .trySurf
	scf
	ret

; SURF: A while facing valid water, provided the Soul Badge is owned
; and any party Pokemon knows Surf.
.trySurf
	ld a, [wObtainedBadges]
	bit BIT_SOULBADGE, a
	jr z, .nothing
	ld b, SURF
	farcall FindPartyMonWithFieldMove
	jr nc, .nothing
	lda_coord 8, 9
	ld [wTilePlayerStandingOn], a
	farcall IsSurfingAllowed
	ld hl, wStatusFlags1
	bit BIT_SURF_ALLOWED, [hl]
	res BIT_SURF_ALLOWED, [hl]
	jr z, .nothing
	ld a, [wCurPartySpecies]
	cp STARTER_PIKACHU
	jr z, .surfingPikachu
	ld a, 1
	jr .startSurf
.surfingPikachu
	ld a, 2
.startSurf
	ld [wd472], a
	ld a, SURFBOARD
	ld [wCurItem], a
	ld [wPseudoItemID], a
	call UseItem
	ld a, [wActionResultOrTookBattleTurn]
	and a
	jr z, .surfFailed
	scf
	ret
.surfFailed
	xor a
	ld [wd472], a
.nothing
	and a
	ret

; if a hidden event was found, stores $00 in [hDidntFindAnyHiddenEvent], else stores $ff
CheckForHiddenEvent::
	ld hl, hItemAlreadyFound
	xor a
	ld [hli], a ; [hItemAlreadyFound]
	ld [hli], a ; [hSavedMapTextPtr]
	ld [hli], a ; [hSavedMapTextPtr + 1]
	ld [hl], a  ; [hDidntFindAnyHiddenEvent]
	ld hl, HiddenEventMaps
	ld de, 3
	ld a, [wCurMap]
	call IsInArray
	jr nc, .noMatch
	inc hl
	ld a, [hli]
	ld h, [hl]
	ld l, a
	push hl
	ld hl, wHiddenEventFunctionArgument
	xor a
	ld [hli], a
	ld [hli], a
	ld [hl], a
	pop hl
.hiddenEventLoop
	ld a, [hli]
	cp $ff
	jr z, .noMatch
	ld [wHiddenEventY], a
	ld b, a
	ld a, [hli]
	ld [wHiddenEventX], a
	ld c, a
	call CheckIfCoordsInFrontOfPlayerMatch
	ldh a, [hCoordsInFrontOfPlayerMatch]
	and a
	jr z, .foundMatchingEvent
	inc hl
	inc hl
	inc hl
	inc hl
	push hl
	ld hl, wHiddenEventIndex
	inc [hl]
	pop hl
	jr .hiddenEventLoop
.foundMatchingEvent
	ld a, [hli]
	ld [wHiddenEventFunctionArgument], a
	ld a, [hli]
	ld [wHiddenEventFunctionRomBank], a
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ret
.noMatch
	ld a, $ff
	ldh [hDidntFindAnyHiddenEvent], a
	ret

; checks if the coordinates in front of the player's sprite match Y in b and X in c
; [hCoordsInFrontOfPlayerMatch] = $00 if they match, $ff if they don't match
CheckIfCoordsInFrontOfPlayerMatch:
	ld a, [wSpritePlayerStateData1FacingDirection]
	cp SPRITE_FACING_UP
	jr z, .facingUp
	cp SPRITE_FACING_LEFT
	jr z, .facingLeft
	cp SPRITE_FACING_RIGHT
	jr z, .facingRight
; facing down
	ld a, [wYCoord]
	inc a
	jr .upDownCommon
.facingUp
	ld a, [wYCoord]
	dec a
.upDownCommon
	cp b
	jr nz, .didNotMatch
	ld a, [wXCoord]
	cp c
	jr nz, .didNotMatch
	jr .matched
.facingLeft
	ld a, [wXCoord]
	dec a
	jr .leftRightCommon
.facingRight
	ld a, [wXCoord]
	inc a
.leftRightCommon
	cp c
	jr nz, .didNotMatch
	ld a, [wYCoord]
	cp b
	jr nz, .didNotMatch
.matched
	xor a
	jr .done
.didNotMatch
	ld a, $ff
.done
	ldh [hCoordsInFrontOfPlayerMatch], a
	ret

INCLUDE "data/events/hidden_events.asm"
