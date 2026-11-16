import struct, sys, math
def cstr(b, o):
    e = b.index(b'\0', o); return b[o:e].decode('latin1'), e + 1
def parse(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'MLOD'
    ver, nl = struct.unpack_from('<II', b, 4); o = 12
    lods = []
    for _ in range(nl):
        assert b[o:o+4] == b'P3DM', b[o:o+4]
        _, _, npt, nnm, nfc, flags = struct.unpack_from('<IIIIII', b, o + 4); o += 28
        pts = [struct.unpack_from('<fffI', b, o + 16*i)[:3] for i in range(npt)]; o += 16*npt
        o += 12*nnm
        faces = []
        for _ in range(nfc):
            ns, = struct.unpack_from('<I', b, o); o += 4
            idx = [struct.unpack_from('<IIff', b, o + 16*k)[0] for k in range(4)]; o += 64
            o += 4
            tex, o = cstr(b, o); mat, o = cstr(b, o)
            faces.append((idx[:ns], tex))
        assert b[o:o+4] == b'TAGG'; o += 4
        tags = {}; props = []
        while True:
            act = b[o]; o += 1
            name, o = cstr(b, o)
            sz, = struct.unpack_from('<I', b, o); o += 4
            data = b[o:o+sz]; o += sz
            if name == '#EndOfFile#': break
            if name == '#Property#':
                k = data[:64].split(b'\0')[0].decode(); v = data[64:].split(b'\0')[0].decode(); props.append((k, v))
            elif not name.startswith('#'):
                sel = [i for i in range(min(npt, sz)) if data[i]]
                tags[name] = sel
        res, = struct.unpack_from('<f', b, o); o += 4
        lods.append(dict(res=res, pts=pts, faces=faces, tags=tags, props=props))
    return lods
if __name__ == '__main__':
    for p in sys.argv[1:]:
        print('==', p)
        for L in parse(p):
            xs=[q[0] for q in L['pts']]; ys=[q[1] for q in L['pts']]; zs=[q[2] for q in L['pts']]
            bb = f"x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}]" if xs else ''
            print(f"  res={L['res']:.3g} pts={len(L['pts'])} faces={len(L['faces'])} {bb} props={L['props']}")
            for k,v in L['tags'].items():
                print(f"     sel {k}: " + ' '.join(f"({L['pts'][i][0]:.2f},{L['pts'][i][1]:.2f},{L['pts'][i][2]:.2f})" for i in v[:6]))
