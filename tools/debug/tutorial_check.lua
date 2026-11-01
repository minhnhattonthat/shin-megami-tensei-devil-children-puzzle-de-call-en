-- Tutorials are automatic demos: any button skips them. Explicitly select the
-- requested script, log it and stop only after its own terminating opcode.
local mt = emu.memType.gbaMemory
local active = nil
L.on_exec(0x0800F52E, 0x0800F52E, function()
  local s = emu.getState()
  s["cpu.r4"] = TUTORIAL_ID
  emu.setState(s)
end)
L.on_exec(0x08006450, 0x08006450, function()
  local p = emu.getState()["cpu.r0"]
  for i = 0, 2 do
    if p == emu.read32(0x083111F8 + 4 * i, mt) then
      active = i
      L.log(string.format("f%d TUTORIAL_START %d", L.frame, i))
    end
  end
end)
L.on_exec(0x08006934, 0x08006934, function()
  local s = emu.getState()
  if active and s["cpu.r0"] == 0xFF and emu.read(s["cpu.r7"] + 0x26, mt) == 0 then
    L.log(string.format("f%d TUTORIAL_DONE %d", L.frame, active))
    L.shot(string.format("f%06d.png", L.frame))
    L.finish(0)
  end
end)
