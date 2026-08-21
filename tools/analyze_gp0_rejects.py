import collections
import struct
import sys

from analyze_gp0_trace import word_count


def s11(value):
    value &= 0x7FF
    return value - 0x800 if value & 0x400 else value


def vertex(word):
    return s11(word), s11(word >> 16)


VERTEX_WORDS = {
    range(0x20, 0x24): (1, 2, 3),
    range(0x24, 0x28): (1, 3, 5),
    range(0x28, 0x2C): (1, 2, 3, 4),
    range(0x2C, 0x30): (1, 3, 5, 7),
    range(0x30, 0x34): (1, 3, 5),
    range(0x34, 0x38): (1, 4, 7),
    range(0x38, 0x3C): (1, 3, 5, 7),
    range(0x3C, 0x40): (1, 4, 7, 10),
}


def indices_for(op):
    for ops, indices in VERTEX_WORDS.items():
        if op in ops:
            return indices
    return None


def rejected(a, b, c):
    xs = (a[0], b[0], c[0])
    ys = (a[1], b[1], c[1])
    return max(xs) - min(xs) > 1023 or max(ys) - min(ys) > 511


path = sys.argv[1]
data = open(path, "rb").read()
records = list(struct.iter_unpack("<IIII", data))
i = 0
counts = collections.Counter()
frames = collections.Counter()
examples = []

while i < len(records):
    frame, addr, value, pc = records[i]
    op = value >> 24
    count = word_count(op)
    start = i
    if count == 0:
        i += 1
        continue
    if count == -1:
        i += 1
        if 0x58 <= op <= 0x5F:
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
        continue
    if i + count > len(records):
        break
    inds = indices_for(op)
    if inds:
        verts = [vertex(records[i + n][2]) for n in inds]
        rejects = [rejected(verts[0], verts[1], verts[2])]
        if len(verts) == 4:
            rejects.append(rejected(verts[2], verts[1], verts[3]))
        nreject = sum(rejects)
        if nreject:
            counts[op] += nreject
            frames[frame] += nreject
            if len(examples) < 100:
                examples.append((frame, op, addr, pc, verts, rejects))
    i += count
    if 0xA0 <= op <= 0xBF:
        wh = records[start + 2][2]
        w = (wh & 0x3FF) or 0x400
        h = ((wh >> 16) & 0x1FF) or 0x200
        i += (w * h + 1) // 2

print("rejected triangles", sum(counts.values()))
print("by opcode", " ".join(f"{op:02X}:{n}" for op, n in counts.most_common()))
print("frames with rejects", len(frames))
print("top frames", frames.most_common(30))
print("examples")
for item in examples:
    print(item)
