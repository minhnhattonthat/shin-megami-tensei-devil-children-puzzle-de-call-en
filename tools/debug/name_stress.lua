-- Host-only pause-menu OBJ-pool check: fill every name slot with the longest
-- real English name (Jack Frost, ten glyphs), including empty slots.
local function longest()
  local s = emu.getState()
  local p = s["cpu.r1"]
  if p >= 0x083F4C00 and p < 0x083F4C00 + 167 * 16 then
    s["cpu.r1"] = 0x083F4C00 + 48 * 16
    emu.setState(s)
  end
end
L.on_exec(0x0800B4C4, 0x0800B4C4, longest)
L.on_exec(0x0800B528, 0x0800B528, longest)
