-- Log every change of the scene handler and story state, one line per change (frame, name=value).
--   emu.py ROM --out D --script tools/debug/scenelog.lua [--var "EXTRA={0x03000BF3}"]
-- Watched: 0x03000934 / 0x03000938 scene handlers (u32), 0x03000BF2 route, 0x03000BF3 story index (u8).
local W = {
  { "scene", 0x03000934, 4 }, { "sub", 0x03000938, 4 },
  { "route", 0x03000BF2, 1 }, { "story", 0x03000BF3, 1 },
  { "B78", 0x03002B78, 1 }, { "B7C", 0x03002B7C, 1 },
}
-- main loop 0800038E: r2 = the state about to run (table 0x0830C408)
L.on_exec(0x0800038E, 0x0800038E, function()
  L.log(string.format("f%d STATE %d", L.frame, emu.getState()["cpu.r2"]))
end)
for _, a in ipairs(EXTRA or {}) do W[#W + 1] = { string.format("%08X", a), a, 1 } end
local last = {}
local mt = emu.memType.gbaMemory
L.on_frame(function(n)
  local ch = {}
  for i, w in ipairs(W) do
    local v = w[3] == 4 and emu.read32(w[2], mt) or emu.read(w[2], mt)
    if v ~= last[i] then
      last[i] = v
      ch[#ch + 1] = string.format("%s=%X", w[1], v)
    end
  end
  if #ch > 0 then L.log(string.format("f%d %s", n, table.concat(ch, " "))) end
end)
