-- Runtime regression probe: the boss name's glyph sprites must not overlap.
-- Run on a cold boss_r0_a1 boot through frame 1800, with --mash 120.
local mt = emu.memType.gbaMemory
local last, count, bad = nil, 0, false
L.on_exec(0x0800B46C, 0x0800B46C, function()
  if L.frame ~= 1700 then return end
  local s = emu.getState()
  local ctx = s["cpu.r0"]
  local x, y = emu.read32(ctx + 4, mt), emu.read32(ctx + 8, mt)
  if x >= 128 and y >= 140 then
    L.log(string.format("HUD_CTX code=%02X x=%d y=%d col=%d pitch=%d", s["cpu.r1"], x, y,
      emu.read(ctx + 0x23, mt), emu.read(ctx + 0x25, mt)))
  end
end)
L.on_exec(0x08001E64, 0x08001E64, function()
  if L.frame ~= 1700 then return end
  local obj = emu.getState()["cpu.r1"]
  local tile, x, y = emu.read32(obj, mt), emu.read16(obj + 8, mt), emu.read16(obj + 10, mt)
  if tile < 0x280 or tile >= 0x380 or x < 128 or y < 140 or y > 152 then return end
  local code = tile - 0x280
  local width = EXPECT_PITCH or emu.read(0x083F0900 + code, mt)
  L.log(string.format("HUD_DRAW code=%02X x=%d y=%d width=%d", code, x, y, width))
  count = count + 1
  if width == 0 or (last and last.y == y and x < last.x + last.width) then
    bad = true
    L.log("HUD_FAIL overlapping boss-name glyphs")
  end
  last = {x=x, y=y, width=width}
end)
L.on_frame(function(n)
  if n == 1701 then
    L.log(string.format("HUD_CHECK %s glyphs=%d", (not bad and count >= 4) and "PASS" or "FAIL", count))
  end
end)
