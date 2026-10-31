"""GBA BIOS LZ77 (type 0x10) decompress / compress. compress() reproduces all 556 ROM blocks exactly (min_disp 2 or 1).

    python -X utf8 tools/lz77.py scan ROM [--size HEX]      # list offsets that decode as LZ77 blocks
    python -X utf8 tools/lz77.py dec ROM OFF OUT
"""
import sys


def decompress(d, off=0):
    """Return (data, end_offset). Raises ValueError on a malformed block."""
    if d[off] != 0x10:
        raise ValueError("not LZ77")
    size = d[off + 1] | d[off + 2] << 8 | d[off + 3] << 16
    out = bytearray()
    i = off + 4
    n = len(d)
    while len(out) < size:
        if i >= n:
            raise ValueError("truncated")
        flags = d[i]; i += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                if i + 1 >= n:
                    raise ValueError("truncated")
                b0, b1 = d[i], d[i + 1]; i += 2
                ln = (b0 >> 4) + 3
                disp = ((b0 & 0xF) << 8 | b1) + 1
                if disp > len(out):
                    raise ValueError("bad disp")
                for _ in range(ln):
                    out.append(out[-disp])
            else:
                if i >= n:
                    raise ValueError("truncated")
                out.append(d[i]); i += 1
    return bytes(out[:size]), i


def compress(data, min_disp=2):
    """Greedy LZ77, longest match, nearest on ties: reproduces the ROM's blocks byte for byte (identity build).
    min_disp=2 (VRAM-safe) matches the fonts, min_disp=1 the graphics blocks; `mode()` finds a block's value."""
    out = bytearray([0x10, len(data) & 0xFF, len(data) >> 8 & 0xFF, len(data) >> 16 & 0xFF])
    i = 0
    n = len(data)
    chains = {}  # 3-byte prefix -> positions, ascending; only matches >= 3 bytes count
    added = 0  # positions < added are in chains

    while i < n:
        flag_pos = len(out); out.append(0)
        flags = 0
        for bit in range(8):
            if i >= n:
                break
            while added <= i - min_disp:
                chains.setdefault(data[added:added + 3], []).append(added); added += 1
            best_len, best_disp = 0, 0
            lo = max(0, i - 4096)
            maxlen = min(18, n - i)
            cand = chains.get(data[i:i + 3], ()) if maxlen >= 3 else ()
            for c in range(len(cand) - 1, -1, -1):
                j = cand[c]
                if j < lo:
                    break
                k = 3
                while k < maxlen and data[j + k] == data[i + k]:
                    k += 1
                if k > best_len:
                    best_len, best_disp = k, i - j
                    if k == maxlen:
                        break
            if best_len >= 3:
                flags |= 0x80 >> bit
                v = (best_len - 3) << 12 | (best_disp - 1)
                out += bytes([v >> 8, v & 0xFF])
                i += best_len
            else:
                out.append(data[i]); i += 1
        out[flag_pos] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def mode(rom, off):
    """(data, min_disp, end) for the block at off: the min_disp whose compress() reproduces its bytes, else None."""
    data, end = decompress(rom, off)
    for md in (2, 1):
        c = compress(data, md)
        if c[:end - off] == rom[off:end] and not any(c[end - off:]):
            return data, md, end
    return data, None, end


def _selftest():
    import os
    for data in (b"", b"a", b"abcabcabcabc" * 50, os.urandom(3000), bytes(5000)):
        c = compress(data)
        assert decompress(c)[0] == data
    print("lz77 selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        _selftest()
    elif a[0] == "scan":
        d = open(a[1], "rb").read()
        want = int(a[a.index("--size") + 1], 16) if "--size" in a else None
        for off in range(0, len(d) - 4, 4):
            if d[off] != 0x10:
                continue
            size = d[off + 1] | d[off + 2] << 8 | d[off + 3] << 16
            if size < 32 or size > 0x40000 or (want and size != want):
                continue
            try:
                _, end = decompress(d, off)
            except ValueError:
                continue
            print("%06X size=%05X end=%06X" % (off, size, end))
    elif a[0] == "dec":
        d = open(a[1], "rb").read()
        data, end = decompress(d, int(a[2], 16))
        open(a[3], "wb").write(data)
        print("%d bytes, block ends %06X" % (len(data), end))
