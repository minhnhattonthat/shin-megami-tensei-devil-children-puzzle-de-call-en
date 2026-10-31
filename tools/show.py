import sys
sys.path.insert(0, 'tools')
from tbl import Table
t = Table.load('tbl/jp.tbl')
d = open('rom/Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba', 'rb').read()
a, n = int(sys.argv[1], 16), int(sys.argv[2], 16)
s, _ = t.decode(d, a, length=n)
print(s.replace('{end}', '{end}\n'))
