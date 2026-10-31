@ Variable-width font for the 16x16 text boxes (docs/re/vwf.md). Thumb, assembled by tools/asm.py (keystone).
@ {NAME} placeholders are filled in by tools/asm.py: WIDTH (u8 advance per code),
@ FONT (64 bytes per code: 16 rows x u32, 2 bits per pixel, pixel x at bits 2x..2x+1), HEART (code of the heart).
@ Hooks (tools/asm.py PATCHES): story 0801B3A4 -> story_char; message boxes 080062C0 / 080069EC / 08006D98 ->
@ msg_char.

@ entry points at fixed offsets, so the hooks need no symbol table
    b story_char                @ ENGINE + 0
    b msg_char                  @ ENGINE + 2
    b small_char                @ ENGINE + 4
    b dd_name                   @ ENGINE + 6

@ ---------------------------------------------------------------------------------------------------------------
@ dd_name: the DeviDas demon name, 8 big-font sprites 16 px apart (0801D598 drew one glyph per sprite).
@ r0 = name (FF-terminated), r1 = tiles of sprite 0 (the next sprites follow at +128), r2 = sprite 0's record
@ (16 bytes each, +0 = visible).
dd_name:
    push {r4-r7, lr}
    adds r4, r0, #0
    adds r5, r1, #0
    adds r6, r2, #0
    movs r7, #0
dd_clear:
    lsls r0, r7, #7
    adds r0, r5, r0
    bl clear_cell
    lsls r0, r7, #4
    movs r1, #0
    strb r1, [r6, r0]
    adds r7, #1
    cmp r7, #8
    blt dd_clear
    movs r7, #0                 @ pen x
dd_char:
    ldrb r2, [r4]
    cmp r2, #0xFF
    beq dd_show
    ldr r0, ={WIDTH}
    ldrb r0, [r0, r2]
    adds r0, r7, r0
    cmp r0, #128
    bgt dd_show                 @ past the 8th sprite
    lsrs r0, r7, #4
    lsls r0, r0, #7
    adds r0, r5, r0
    movs r1, #15
    ands r1, r7
    push {r2}
    movs r3, #16
    bl render
    pop {r2}
    ldr r0, ={WIDTH}
    ldrb r0, [r0, r2]
    adds r7, r7, r0
    adds r4, #1
    b dd_char
dd_show:
    adds r7, #15
    lsrs r7, r7, #4             @ sprites in use
    movs r1, #1
dd_vis:
    subs r7, #1
    bmi dd_out
    lsls r0, r7, #4
    strb r1, [r6, r0]
    b dd_vis
dd_out:
    pop {r4-r7, pc}

@ ---------------------------------------------------------------------------------------------------------------
@ small_char: replaces 0800B46C, which puts one 8x8 menu-font sprite at column [ctx+0x23] * pitch [ctx+0x25] and
@ advances the column by 1. With pitch 8 (menus) the column is now the pen x in px and advances by the glyph's
@ width ({SMALLW}, tools/smallfont.py); other pitches keep the fixed grid. r0 = ctx, r1 = code, r2 = palette.
small_char:
    push {r4-r6, lr}
    lsls r1, r1, #24
    lsrs r1, r1, #24
    adds r6, r0, #0
    ldr r5, [r6, #0x28]         @ the sprite record the game reuses for every character
    movs r4, #0x23
    ldrsb r3, [r6, r4]
    movs r4, #0x25
    ldrsb r4, [r6, r4]
    cmp r4, #8
    beq sm_px
    muls r3, r4
sm_px:
    ldr r0, [r6, #4]
    adds r0, r0, r3
    strh r0, [r5, #8]
    movs r4, #0x24
    ldrsb r3, [r6, r4]
    movs r4, #0x26
    ldrsb r4, [r6, r4]
    muls r3, r4
    ldr r0, [r6, #8]
    adds r0, r0, r3
    strh r0, [r5, #0xA]
    movs r0, #0xA0
    lsls r0, r0, #2
    adds r0, r0, r1
    str r0, [r5]                @ tile 0x280 + code
    strb r2, [r5, #0xE]
    push {r1}
    movs r0, #0
    adds r1, r5, #0
    bl 0x08001E64               @ draw it now, as the original did
    pop {r1}
    movs r0, #1
    movs r4, #0x25
    ldrsb r4, [r6, r4]
    cmp r4, #8
    bne sm_adv
    ldr r0, ={SMALLW}
    ldrb r0, [r0, r1]
sm_adv:
    movs r4, #0x23
    ldrb r3, [r6, r4]
    adds r3, r3, r0
    strb r3, [r6, r4]
    pop {r4-r6, pc}

@ ---------------------------------------------------------------------------------------------------------------
@ story_char: one character of a story script. r4 = text pointer, r5 = story struct 0x03000B70.
@ The story box has 28 fixed 16x16 sprites (slot 0-13 line 1, 14-27 line 2); the slot's tile data is at
@ [r5+8] + slot*128, its visible flag at [r5+0x20] + slot*16. The game placed them 14 px apart from x 16; the hook
@ at 0801A93E puts them 16 px apart from x 12, so a line is one 224 px bitmap. [r5+0x32] (the game's slot counter)
@ now holds the pen: 0 or 14 = start of line 1 or 2 (what the game's clear / newline commands write), else
@ 0x8000 | line << 8 | px.
story_char:
    push {r4-r7, lr}
    mov r0, r8
    mov r1, r9
    push {r0, r1}
    ldrb r6, [r4]
    ldrh r0, [r5, #0x32]
    movs r7, #0
    movs r1, #0
    cmp r0, #0
    beq sc_got
    cmp r0, #14
    bne sc_enc
    movs r7, #1
    b sc_got
sc_enc:
    lsrs r7, r0, #8
    movs r2, #1
    ands r7, r2
    movs r1, #0xFF
    ands r1, r0
sc_got:
    lsls r0, r7, #4
    subs r0, r0, r7
    subs r0, r0, r7
    mov r9, r0                  @ first slot of the line (0 / 14)
    adds r7, r1, #0             @ px
    ldr r0, ={WIDTH}
    ldrb r2, [r0, r6]
    adds r3, r7, r2             @ new px
    cmp r3, #224
    bhi sc_out                  @ past the line end: drop the character (the wrap check keeps lines shorter)
    mov r8, r3
    adds r4, r7, #0
    adds r4, #15
    lsrs r4, r4, #4             @ first sprite not yet used on this line = ceil(px / 16)
    adds r2, r3, #0
    adds r2, #15
    lsrs r2, r2, #4             @ ceil(new px / 16)
sc_cells:
    cmp r4, r2
    bge sc_draw
    mov r0, r9
    adds r0, r0, r4             @ slot
    lsls r3, r0, #4
    ldr r1, [r5, #0x20]
    adds r1, r1, r3
    movs r3, #1
    strb r3, [r1]               @ show the sprite
    lsls r0, r0, #7
    ldr r1, [r5, #8]
    adds r0, r0, r1
    push {r2}
    bl clear_cell               @ its tiles still hold the last page
    pop {r2}
    adds r4, #1
    b sc_cells
sc_draw:
    lsrs r4, r7, #4             @ sprite holding the glyph's first column
    movs r1, #15
    ands r1, r7                 @ column in it
    mov r0, r9
    adds r0, r0, r4
    lsls r0, r0, #7
    ldr r2, [r5, #8]
    adds r0, r0, r2
    adds r2, r6, #0
    movs r3, #16
    bl render
    movs r1, #0x80
    lsls r1, r1, #8
    mov r3, r8
    orrs r1, r3
    mov r0, r9
    cmp r0, #0
    beq sc_l0
    movs r0, #1
    lsls r0, r0, #8
    orrs r1, r0
sc_l0:
    strh r1, [r5, #0x32]
sc_out:
    movs r0, #0                 @ the typewriter delay counter, as the replaced code reset it
    movs r1, #0x2F
    strb r0, [r5, r1]
    pop {r0, r1}
    mov r8, r0
    mov r9, r1
    pop {r4-r7, pc}

@ ---------------------------------------------------------------------------------------------------------------
@ msg_char: one character of a message box (rescue / boss / system / tutorial). r0 = box struct, r1 = code.
@ Struct: +4 x, +8 y of the box text, +0x22 sprites used (max 32), +0x23 pen x in px (was: column), +0x24 line,
@ +0x25 colour (palette 10 + colour). Sprites: [0x03002BDC] + 0x1030 + n*0x1C (+8 x, +0xA y, +0xE palette), tiles
@ at 0x06014000 + n*128. A run of text in one colour is a segment of sprites 16 px apart starting where the run
@ starts, so a colour change or a new line starts a new sprite instead of recolouring a shared one.
msg_char:
    push {r4-r7, lr}
    mov r2, r8
    mov r3, r9
    push {r2, r3}
    adds r5, r0, #0             @ struct
    adds r6, r1, #0             @ code
    ldr r0, =0x03002BDC
    ldr r0, [r0]
    ldr r1, =0x1030
    adds r0, r0, r1
    mov r8, r0                  @ sprite array
    movs r0, #0
    mov r9, r0                  @ 1 = out of sprites
    movs r0, #0x25
    ldrb r7, [r5, r0]
    adds r7, #10                @ palette
    cmp r6, #{HEART}
    bne mc_pal
    movs r7, #11                @ the heart is red, as in the original (palette 11)
mc_pal:
    movs r0, #0x23
    ldrb r4, [r5, r0]           @ pen x
    cmp r4, #0
    beq mc_new                  @ new line
    bl last_obj
    cmp r0, #0
    beq mc_new
    ldrb r1, [r0, #0xE]
    cmp r1, r7
    beq mc_have
mc_new:
    ldr r0, [r5, #4]
    adds r0, r0, r4
    bl alloc
mc_have:
    ldr r2, [r5, #4]
    adds r2, r2, r4             @ glyph x on screen
    ldr r3, ={WIDTH}
    ldrb r3, [r3, r6]           @ advance
    bl last_obj
    cmp r0, #0
    beq mc_done
    ldrh r1, [r0, #8]
    adds r1, #16                @ right edge of the last sprite
    adds r0, r2, r3
    cmp r0, r1
    ble mc_fits
    adds r0, r1, #0
    bl alloc                    @ the glyph runs into the next sprite of the segment
mc_fits:
    mov r0, r9
    cmp r0, #0
    bne mc_done
    bl last_obj
    ldrh r1, [r0, #8]
    movs r0, #0x22
    ldrb r0, [r5, r0]
    subs r0, #1                 @ index of the sprite holding the glyph's first column
    cmp r2, r1
    bge mc_first
    subs r0, #1
    subs r1, #16
mc_first:
    subs r1, r2, r1             @ column in it
    lsls r0, r0, #7
    ldr r2, =0x06014000
    adds r0, r0, r2
    adds r2, r6, #0
    push {r3}
    movs r3, #16
    bl render
    pop {r3}
mc_done:
    adds r4, r4, r3
    cmp r4, #0xFF
    bls mc_store
    movs r4, #0xFF
mc_store:
    movs r0, #0x23
    strb r4, [r5, r0]
    pop {r2, r3}
    mov r8, r2
    mov r9, r3
    pop {r4-r7, pc}

@ last_obj: r0 = the last allocated sprite (r5 struct, r8 array), or 0 when none. Keeps r1-r7.
last_obj:
    push {r1}
    movs r0, #0x22
    ldrb r0, [r5, r0]
    cmp r0, #0
    beq lo_out
    subs r0, #1
    movs r1, #0x1C
    muls r0, r1
    add r0, r8
lo_out:
    pop {r1}
    bx lr

@ alloc: next sprite at screen x r0 on the current line, palette r7, tiles cleared. Sets r9 = 1 when all 32 are
@ in use. Keeps r1-r7.
alloc:
    push {r1-r4, lr}
    movs r4, #0x22
    ldrb r1, [r5, r4]
    cmp r1, #32
    bge al_full
    movs r2, #0x1C
    muls r2, r1
    add r2, r8
    strh r0, [r2, #8]
    movs r4, #0x24
    ldrsb r4, [r5, r4]
    lsls r4, r4, #4
    ldr r3, [r5, #8]
    adds r3, r3, r4
    strh r3, [r2, #0xA]
    strb r7, [r2, #0xE]
    adds r0, r1, #1
    movs r4, #0x22
    strb r0, [r5, r4]
    lsls r0, r1, #7
    ldr r3, =0x06014000
    adds r0, r0, r3
    bl clear_cell
    pop {r1-r4, pc}
al_full:
    movs r0, #1
    mov r9, r0
    pop {r1-r4, pc}

@ ---------------------------------------------------------------------------------------------------------------
@ clear_cell: zero the 128 bytes of tiles at r0 (one 16x16 4bpp sprite). Clobbers r0-r3.
clear_cell:
    push {r4, lr}
    movs r1, #0
    movs r2, #0
    movs r3, #0
    movs r4, #0
    stmia r0!, {r1-r4}
    stmia r0!, {r1-r4}
    stmia r0!, {r1-r4}
    stmia r0!, {r1-r4}
    stmia r0!, {r1-r4}
    stmia r0!, {r1-r4}
    stmia r0!, {r1-r4}
    stmia r0!, {r1-r4}
    pop {r4, pc}

@ render: draw glyph r2 with its first column at column r1 of the sprite whose tiles are at r0; the next sprite's
@ tiles follow at +128, r3 = columns per sprite (14 or 16). Tiles in a 16x16 sprite: TL TR BL BR, 32 bytes each,
@ 4 bytes per row, low nibble = left pixel. VRAM takes 16-bit writes only. Clobbers r0-r3.
render:
    push {r4-r7, lr}
    mov r4, r8
    mov r5, r9
    mov r6, r10
    mov r7, r11
    push {r4-r7}
    ldr r4, ={FONT}
    lsls r2, r2, #6
    adds r4, r4, r2
    mov r11, r4                 @ glyph rows
    mov r8, r0                  @ first sprite's tiles
    mov r9, r1                  @ first column
    mov r10, r3                 @ columns per sprite
    movs r5, #0                 @ y
rd_row:
    mov r4, r11
    ldr r6, [r4]
    adds r4, #4
    mov r11, r4
    cmp r6, #0
    beq rd_next
    mov r7, r9                  @ column
    mov r0, r8                  @ sprite
rd_px:
    movs r1, #3
    ands r1, r6
    beq rd_skip
    lsrs r2, r7, #3
    lsrs r3, r5, #3
    lsls r3, r3, #1
    adds r2, r2, r3
    lsls r2, r2, #5             @ tile * 32
    movs r3, #7
    ands r3, r5
    lsls r3, r3, #2
    adds r2, r2, r3             @ + row * 4
    movs r3, #7
    ands r3, r7
    lsrs r3, r3, #1
    adds r2, r2, r3             @ byte offset
    movs r3, #1
    ands r3, r2
    lsls r3, r3, #3
    movs r4, #1
    ands r4, r7
    lsls r4, r4, #2
    orrs r3, r4                 @ shift in the halfword
    lsrs r2, r2, #1
    lsls r2, r2, #1
    adds r2, r0, r2
    lsls r1, r1, r3
    mov r12, r1
    movs r1, #0xF
    lsls r1, r1, r3
    ldrh r4, [r2]
    bics r4, r1
    mov r1, r12
    orrs r4, r1
    strh r4, [r2]
rd_skip:
    lsrs r6, r6, #2
    adds r7, #1
    cmp r7, r10
    blt rd_cont
    movs r7, #0
    adds r0, #128
rd_cont:
    cmp r6, #0
    bne rd_px
rd_next:
    adds r5, #1
    cmp r5, #16
    blt rd_row
    pop {r4-r7}
    mov r8, r4
    mov r9, r5
    mov r10, r6
    mov r11, r7
    pop {r4-r7, pc}
    .ltorg
