-- Runtime proof of message-table coverage; host-side only, never patched into ROM.
local mt = emu.memType.gbaMemory
local ids = {}
-- The stock boss selector adds one, so boss.000 is not selected by normal
-- intros. Opt-in rendering probe through that same printer for the dormant text.
if TEST_BOSS_ZERO then
  local capture_until = 0
  L.on_exec(0x080120EA, 0x080120EA, function()
    emu.write(emu.read32(0x03002BDC, mt) + 0x158D, NAME_ID or 0, mt)
    local s = emu.getState()
    s["cpu.r0"] = emu.read32(0x0830E224, mt)
    emu.setState(s)
    capture_until = L.frame + 100
  end)
  L.on_frame(function(n)
    if n <= capture_until and n % 2 == 0 then L.shot(string.format("f%06d.png", n)) end
  end)
end
for i = 0, 100 do ids[emu.read32(0x0830DBDC + 4 * i, mt)] = string.format("rescue.%03d", i) end
for i = 0, 12 do ids[emu.read32(0x0830E224 + 4 * i, mt)] = string.format("boss.%03d", i) end
L.on_exec(0x080060CC, 0x080060CC, function()
  local pointer = emu.getState()["cpu.r0"]
  if ids[pointer] then L.log(string.format("f%d TEXT %s", L.frame, ids[pointer])) end
end)
L.on_exec(0x080062A4, 0x080062A4, function()
  L.log(string.format("f%d NAME id=%d", L.frame, emu.getState()["cpu.r0"]))
end)
