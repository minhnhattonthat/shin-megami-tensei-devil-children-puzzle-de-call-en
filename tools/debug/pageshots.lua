-- Text tour: with --mash N, take a shot on the frame before each press, so every page is caught fully printed.
-- Shots are named f<frame>.png like emu.py's own, so sheet.py --changed drops the repeats. tools/qa_tour.py.
L.on_frame(function(n)
  if (MASH or 0) > 0 and L.route_done() and n % MASH == MASH - 1 then L.shot(string.format("f%06d.png", n)) end
end)
