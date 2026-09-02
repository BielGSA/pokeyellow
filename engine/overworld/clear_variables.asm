ClearVariablesOnEnterMap::
	ld a, SCREEN_HEIGHT_PX
	ldh [hWY], a
	ldh [rWY], a
	xor a
	ldh [hAutoBGTransferEnabled], a
	ld [wStepCounter], a
	ld [wLoneAttackNo], a
	ldh [hJoyPressed], a
	ldh [hJoyReleased], a
	ldh [hJoyHeld], a
	ld [wActionResultOrTookBattleTurn], a
	ld [wUnusedMapVariable], a
	ld hl, wCardKeyDoorY
	ld [hli], a
	ld [hl], a
	ld hl, wWhichTrade
	ld bc, wStandingOnWarpPadOrHole - wWhichTrade
	call FillMemory

; Pokemon Yellow Complete: automatically illuminate Rock Tunnel when the
; Boulder Badge is owned and any party Pokemon knows Flash.
	ld a, [wCurMap]
	cp ROCK_TUNNEL_1F
	jr z, .tryAutoFlash
	cp ROCK_TUNNEL_B1F
	jr nz, .done
.tryAutoFlash
	ld a, [wObtainedBadges]
	bit BIT_BOULDERBADGE, a
	jr z, .done
	ld b, FLASH
	call FindPartyMonWithFieldMove
	jr nc, .done
	xor a
	ld [wMapPalOffset], a
.done
	ret
