-- Warp to a scene from a cold boot (docs/re/debug.md).
--   emu.py ROM --out D --script tools/debug/warp.lua --var "SCENE='story_03'" --frames 900 [--mash 40]
-- Scene list: tools/debug/scenes.txt (override with --var "SCENES=[[abs path]]").
-- How: the main loop (0800038C) keeps the next state in r2 and calls table 0x0830C408[r2]. When the title state (0)
-- is about to run for the first time, r2 is replaced by the scene's state and its RAM pokes are applied. Pokes tagged
-- @N are applied (again) each time state N is about to run. Opt-in: GOD=1 (see below).
local mt = emu.memType.gbaMemory
local names = { B78 = 0x03002B78, B7C = 0x03002B7C }  -- story area counter, route (docs/re/debug.md)
local function parse(path)
  for line in io.lines(path) do
    local l = line:gsub("#.*", ""):gsub("|.*", "")  -- after "|": emu.py args and the expected log line (warp_all.py)
    local name, state, rest = l:match("^%s*(%S+)%s+(%d+)%s*(.-)%s*$")
    if name == SCENE then
      local pokes = {}
      for tok in rest:gmatch("%S+") do
        local k, v, at = tok:match("^([%w_]+)=([%xx]+)@?(%d*)$")
        assert(k, "bad poke " .. tok)
        if names[k] or tonumber(k) then
          pokes[#pokes + 1] = { addr = names[k] or tonumber(k), val = tonumber(v), at = tonumber(at) }
        elseif _G[k] == nil then
          _G[k] = tonumber(v)  -- an option (STAGE_R4...); --var on the command line wins
        end
      end
      return tonumber(state), pokes
    end
  end
  error("scene not in list: " .. tostring(SCENE))
end
local target, pokes = parse(SCENES or "../debug/scenes.txt")
local function apply(at)
  for _, p in ipairs(pokes) do
    if p.at == at then emu.write(p.addr, p.val, mt) end
  end
end
local warped = false
L.on_exec(0x0800038E, 0x0800038E, function()
  local s = emu.getState()
  local st = s["cpu.r2"]
  if not warped and st == 0 then
    warped = true
    apply(nil)
    s["cpu.r2"] = target
    emu.setState(s)
    L.log(string.format("f%d warp %s: state %d", L.frame, SCENE, target))
    st = target
  end
  if warped then apply(st); L.log(string.format("f%d STATE %d", L.frame, st)) end
end)
-- FLOOR_RESULT=X / BOSS_RESULT=Y [RESULT_AT=F]: once per floor / boss fight, after F frames (default 120) in the
-- player-control state 10, write X / Y into the event byte [[0x03002BDC]+0x157C] that state 10 checks.
-- The value is then held there until the loop returns it (EXIT, if given, is held instead).
-- Floor (0800EA84, loop state r4 at 0800EB34): 0x63 clear (-> boss), 0x62 quit to title, 2 pause menu, 0xE retry.
-- Boss (08012AAC, loop state r7 at 08012B6C): 0x63 win (-> post-area script), 0x61 lose (GAME OVER / continue
-- screen 080135BC), 0x62 quit. Puzzle mode (08017728, r6 at 080177CE): 0x63 + PUZZLE_EXIT=0x18 = stage clear,
-- 0x63 alone = retry, 0x62 quit. LOG_LOOP=1 logs loop state changes.
local function forcer(entry, pc, reg, what, result, exit)
  local n, last
  L.on_exec(entry, entry, function()
    n = 0
    L.log(string.format("f%d %s start, area %d", L.frame, what, emu.read(emu.read32(0x03002BD0, mt) + 1, mt)))
  end)
  L.on_exec(pc, pc, function()
    local s = emu.getState()
    if LOG_LOOP and s[reg] ~= last then last = s[reg]; L.log(string.format("f%d %s state %d", L.frame, what, last)) end
    if not result then return end
    if n == nil then  -- forced: keep an ending code until the loop exits (a mashed A press writes 1 there, 0800CE94)
      if exit or result >= 0x60 then emu.write(emu.read32(0x03002BDC, mt) + 0x157C, exit or result, mt) end
      return
    end
    if s[reg] ~= 10 then return end
    n = n + 1
    if n == (RESULT_AT or 120) then
      n = nil
      -- RESCUE_ID: demon whose rescue dialogue result 2 shows (0800EF62 reads +0x158D)
      if RESCUE_ID then emu.write(emu.read32(0x03002BDC, mt) + 0x158D, RESCUE_ID, mt) end
      emu.write(emu.read32(0x03002BDC, mt) + 0x157C, result, mt)
      L.log(string.format("f%d %s result 0x%X", L.frame, what, result))
    end
  end)
end
forcer(0x0800EA84, 0x0800EB34, "cpu.r4", "floor", FLOOR_RESULT)
forcer(0x08012AAC, 0x08012B6C, "cpu.r7", "boss", BOSS_RESULT)
forcer(0x08017728, 0x080177CE, "cpu.r6", "puzzle", PUZZLE_RESULT, PUZZLE_EXIT)  -- B78 = diff<<4 | stage
-- SCRIPT=N: story text state starts script N (written after its init picked one from B78/B7C, 0801AD9A); used for
-- the scripts the game only reaches by chaining (2 after 1, 14 after 13, 16 after 15, 28 after 27).
if SCRIPT then
  L.on_exec(0x0801AD9A, 0x0801AD9A, function()
    if SCRIPT then emu.write(0x03000BF3, SCRIPT, mt); SCRIPT = nil end
  end)
end
-- GAME OVER / continue screen (boss lost)
L.on_exec(0x080135BC, 0x080135BC, function() L.log(string.format("f%d continue screen", L.frame)) end)
-- the script index actually started (proof for story scenes)
local lastscript
L.on_exec(0x0801B34C, 0x0801B34C, function()
  local v = emu.read(0x03000BF3, mt)
  if v ~= lastscript then lastscript = v; L.log(string.format("f%d script %d", L.frame, v)) end
end)
