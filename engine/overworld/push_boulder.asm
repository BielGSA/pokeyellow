; Pokemon Yellow Complete: find the first party Pokemon that knows the
; requested field move (move ID in b). Sets wWhichPokemon and wCurPartySpecies.
; Carry set on success.
FindPartyMonWithFieldMove::
	ld hl, wPartyMon1Moves
	ld c, 0
.monLoop
	ld d, NUM_MOVES
.moveLoop
	ld a, [hli]
	cp b
	jr z, .found
	dec d
	jr nz, .moveLoop
	ld de, PARTYMON_STRUCT_LENGTH - NUM_MOVES
	add hl, de
	inc c
	ld a, [wPartyCount]
	cp c
	jr nz, .monLoop
	and a
	ret
.found
	ld a, c
	ld [wWhichPokemon], a
	ld hl, wPartySpecies
	ld b, 0
	add hl, bc
	ld a, [hl]
	ld [wCurPartySpecies], a
	scf
	ret

TryPushingBoulder::
	ld a, [wStatusFlags1]
	bit BIT_STRENGTH_ACTIVE, a
	jr nz, .strengthReady

; Direct Strength: when the player tries to push a boulder, automatically
; activate Strength if the Rainbow Badge is owned and a party Pokemon knows it.
	ld a, [wObtainedBadges]
	bit BIT_RAINBOWBADGE, a
	ret z
	ld b, STRENGTH
	call FindPartyMonWithFieldMove
	ret nc
	ld hl, wStatusFlags1
	set BIT_STRENGTH_ACTIVE, [hl]
.strengthReady
	ld a, [wMiscFlags]
	bit BIT_BOULDER_DUST, a
	ret nz
	xor a
	ldh [hSpriteIndex], a
	call IsSpriteInFrontOfPlayer
	ldh a, [hSpriteIndex]
	ld [wBoulderSpriteIndex], a
	and a
	jp z, ResetBoulderPushFlags
	ld hl, wSpritePlayerStateData1MovementStatus
	ld d, $0
	ldh a, [hSpriteIndex]
	swap a
	ld e, a
	add hl, de
	res BIT_FACE_PLAYER, [hl]
	call GetSpriteMovementByte2Pointer
	ld a, [hl]
	cp BOULDER_MOVEMENT_BYTE_2
	jp nz, ResetBoulderPushFlags
	ld hl, wMiscFlags
	bit BIT_TRIED_PUSH_BOULDER, [hl]
	set BIT_TRIED_PUSH_BOULDER, [hl]
	ret z ; the player must try pushing twice before the boulder will move
	ldh a, [hJoyHeld]
	and PAD_CTRL_PAD
	ret z
	predef CheckForCollisionWhenPushingBoulder
	ld a, [wTileInFrontOfBoulderAndBoulderCollisionResult]
	and a ; was there a collision?
	jp nz, ResetBoulderPushFlags
	ldh a, [hJoyHeld]
	ld b, a
	ld a, [wSpritePlayerStateData1FacingDirection]
	cp SPRITE_FACING_UP
	jr z, .pushBoulderUp
	cp SPRITE_FACING_LEFT
	jr z, .pushBoulderLeft
	cp SPRITE_FACING_RIGHT
	jr z, .pushBoulderRight
; push boulder down
	bit B_PAD_DOWN, b
	ret z
	ld de, PushBoulderDownMovementData
	jr .done
.pushBoulderUp
	bit B_PAD_UP, b
	ret z
	ld de, PushBoulderUpMovementData
	jr .done
.pushBoulderLeft
	bit B_PAD_LEFT, b
	ret z
	ld de, PushBoulderLeftMovementData
	jr .done
.pushBoulderRight
	bit B_PAD_RIGHT, b
	ret z
	ld de, PushBoulderRightMovementData
.done
	call MoveSprite
	ld a, SFX_PUSH_BOULDER
	call PlaySound
	ld hl, wMiscFlags
	set BIT_BOULDER_DUST, [hl]
	ret

PushBoulderUpMovementData:
	db NPC_MOVEMENT_UP
	db -1 ; end

PushBoulderDownMovementData:
	db NPC_MOVEMENT_DOWN
	db -1 ; end

PushBoulderLeftMovementData:
	db NPC_MOVEMENT_LEFT
	db -1 ; end

PushBoulderRightMovementData:
	db NPC_MOVEMENT_RIGHT
	db -1 ; end

DoBoulderDustAnimation::
	ld a, [wStatusFlags5]
	bit BIT_SCRIPTED_NPC_MOVEMENT, a
	ret nz
	callfar AnimateBoulderDust
	call DiscardButtonPresses
	ld [wJoyIgnore], a
	call ResetBoulderPushFlags
	set BIT_PUSHED_BOULDER, [hl]
	ld a, [wBoulderSpriteIndex]
	ldh [hSpriteIndex], a
	call GetSpriteMovementByte2Pointer
	ld [hl], $10
	ld a, SFX_CUT
	jp PlaySound

ResetBoulderPushFlags:
	ld hl, wMiscFlags
	res BIT_BOULDER_DUST, [hl]
	res BIT_TRIED_PUSH_BOULDER, [hl]
	ret
