; Pokemon Yellow Complete:
; after becoming Champion, the Indigo Plateau mart also sells
; Master Balls and Rare Candies for easy post-game Pokedex completion.
AddChampionMartItems::
	ld a, [wCurMap]
	cp INDIGO_PLATEAU_LOBBY
	ret nz
	CheckEvent EVENT_BEAT_CHAMPION_RIVAL
	ret z

	ld hl, wItemList
	ld [hl], 9
	ld de, 8
	add hl, de
	ld a, MASTER_BALL
	ld [hli], a
	ld a, RARE_CANDY
	ld [hli], a
	ld [hl], -1
	ret
