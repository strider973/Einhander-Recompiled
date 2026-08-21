import collections
import struct
import sys


def word_count(op):
    if op in (0x00, 0x01, 0x1F, 0xE0, 0xE1, 0xE2, 0xE3, 0xE4, 0xE5, 0xE6): return 1
    if 0x03 <= op <= 0x1E or 0xE7 <= op <= 0xEF or op == 0xFF: return 1
    if op == 0x02: return 3
    if 0x20 <= op <= 0x23: return 4
    if 0x24 <= op <= 0x27: return 7
    if 0x28 <= op <= 0x2B: return 5
    if 0x2C <= op <= 0x2F: return 9
    if 0x30 <= op <= 0x33: return 6
    if 0x34 <= op <= 0x37: return 9
    if 0x38 <= op <= 0x3B: return 8
    if 0x3C <= op <= 0x3F: return 12
    if 0x40 <= op <= 0x47: return 3
    if 0x48 <= op <= 0x4F or 0x58 <= op <= 0x5F: return -1
    if 0x50 <= op <= 0x57: return 4
    if 0x60 <= op <= 0x63: return 3
    if 0x64 <= op <= 0x67: return 4
    if 0x68 <= op <= 0x6B: return 2
    if 0x6C <= op <= 0x6F: return 3
    if 0x70 <= op <= 0x73: return 2
    if 0x74 <= op <= 0x77: return 3
    if 0x78 <= op <= 0x7B: return 2
    if 0x7C <= op <= 0x7F: return 3
    if 0x80 <= op <= 0x9F: return 4
    if 0xA0 <= op <= 0xDF: return 3
    return 0


def s16(v):
    return v - 0x10000 if v & 0x8000 else v


data = open(sys.argv[1], "rb").read()
records = list(struct.iter_unpack("<IIII", data))
i = 0
by_frame = collections.defaultdict(collections.Counter)
odd = []
commands = []
crossings = []
while i < len(records):
    frame, addr, value, pc = records[i]
    op = value >> 24
    count = word_count(op)
    start = i
    if count == 0:
        odd.append(("unknown", i, records[i]))
        i += 1
        continue
    if count == -1:
        i += 1
        if 0x58 <= op <= 0x5F:
            # Shaded stream: V0,C1,V1,C2,V2,...,55555555.  The sentinel
            # occupies the next-colour position; Einhander has colour words
            # which match the loose nibble mask, so use its canonical value.
            while i < len(records):
                rel = i - (start + 1)
                if rel & 1 and records[i][2] == 0x55555555:
                    i += 1
                    break
                i += 1
        else:
            while i < len(records):
                if records[i][2] & 0xF000F000 == 0x50005000:
                    i += 1
                    break
                i += 1
        count = i - start
        if count > 256:
            odd.append(("long_polyline", start, records[start], count))
    else:
        i += count
        if i > len(records): break
        if 0xA0 <= op <= 0xBF and count == 3:
            wh = records[start + 2][2]
            w = wh & 0xFFFF
            h = wh >> 16
            pixels = ((w & 0x3FF) or 0x400) * ((h & 0x1FF) or 0x200)
            payload = (pixels + 1) // 2
            i += payload
            count += payload
    by_frame[frame][op] += 1
    commands.append((frame, start, count, op, addr, pc))
    end = min(i, len(records))
    for j in range(start + 1, end):
        prev, cur = records[j - 1][1], records[j][1]
        if prev != 0x1F801810 and cur != 0x1F801810 and cur != prev + 4:
            crossings.append((frame, start, j, op, prev, cur,
                              records[j - 1][2], records[j][2]))
            break
    if 0x20 <= op <= 0x7F and count > 1:
        words = [records[j][2] for j in range(start, min(i, len(records)))]
        coords = []
        for w in words[1:]:
            x, y = s16(w & 0xFFFF), s16(w >> 16)
            if -2048 <= x <= 2047 and -2048 <= y <= 2047:
                coords.append((x, y))
        if coords:
            spanx = max(x for x, _ in coords) - min(x for x, _ in coords)
            spany = max(y for _, y in coords) - min(y for _, y in coords)
            if spanx > 1024 or spany > 512:
                odd.append(("huge_span", start, records[start], count, spanx, spany))

print("records", len(records), "commands", len(commands), "frames", len(by_frame))
print("odd", len(odd))
for x in odd[-100:]: print(x)
print("packet crossings", len(crossings))
for x in crossings[-100:]: print(x)
if "--compact" not in sys.argv:
    print("frame summaries")
    for frame in sorted(by_frame):
        c = by_frame[frame]
        print(frame, sum(c.values()), " ".join(f"{op:02X}:{n}" for op, n in c.most_common(12)))
