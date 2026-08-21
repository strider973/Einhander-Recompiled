import collections, struct, sys

def wc(op):
    if op in (0,1,0x1f,0xe0,0xe1,0xe2,0xe3,0xe4,0xe5,0xe6): return 1
    if 3 <= op <= 0x1e or 0xe7 <= op <= 0xef or op == 0xff: return 1
    if op == 2: return 3
    if 0x20 <= op <= 0x23: return 4
    if 0x24 <= op <= 0x27: return 7
    if 0x28 <= op <= 0x2b: return 5
    if 0x2c <= op <= 0x2f: return 9
    if 0x30 <= op <= 0x33: return 6
    if 0x34 <= op <= 0x37: return 9
    if 0x38 <= op <= 0x3b: return 8
    if 0x3c <= op <= 0x3f: return 12
    if 0x40 <= op <= 0x47: return 3
    if 0x48 <= op <= 0x4f or 0x58 <= op <= 0x5f: return -1
    if 0x50 <= op <= 0x57: return 4
    if 0x60 <= op <= 0x63: return 3
    if 0x64 <= op <= 0x67: return 4
    if 0x68 <= op <= 0x6b: return 2
    if 0x6c <= op <= 0x6f: return 3
    if 0x70 <= op <= 0x73: return 2
    if 0x74 <= op <= 0x77: return 3
    if 0x78 <= op <= 0x7b: return 2
    if 0x7c <= op <= 0x7f: return 3
    if 0x80 <= op <= 0x9f: return 4
    if 0xa0 <= op <= 0xdf: return 3
    return 0

rec=list(struct.iter_unpack('<IIII',open(sys.argv[1],'rb').read()))
v=[0]*(1024*512); i=0; tpx=tpy=depth=0; stats=collections.Counter(); byframe=collections.Counter()
while i<len(rec):
    frame,addr,val,pc=rec[i]; op=val>>24; n=wc(op); start=i
    if n<=0:
        i+=1
        while i<len(rec) and not (rec[i][2]==0x55555555 if 0x58<=op<=0x5f else (rec[i][2]&0xf000f000)==0x50005000): i+=1
        i+=1; continue
    words=[rec[j][2] for j in range(i,min(i+n,len(rec)))]; i+=n
    if op==0xe1:
        p=val&0xffffff; tpx=p&15; tpy=(p>>4)&1; depth=(p>>7)&3
    elif op==0xa0 and len(words)>=3:
        xy,wh=words[1],words[2]; x=xy&0xffff; y=xy>>16; w=(wh&0x3ff) or 1024; h=((wh>>16)&0x1ff) or 512
        count=w*h; payload=(count+1)//2
        pix=[]
        for j in range(payload):
            q=rec[i+j][2]; pix.extend((q&0xffff,q>>16))
        for k,p in enumerate(pix[:count]): v[((y+k//w)&511)*1024+((x+k%w)&1023)]=p
        i+=payload
    elif op==0x80 and len(words)==4:
        sxy,dxy,wh=words[1:]; sx=sxy&0xffff; sy=sxy>>16; dx=dxy&0xffff; dy=dxy>>16; w=(wh&0x3ff)or 1024; h=((wh>>16)&0x1ff)or 512
        tmp=[v[((sy+yy)&511)*1024+((sx+xx)&1023)] for yy in range(h) for xx in range(w)]
        for k,p in enumerate(tmp): v[((dy+k//w)&511)*1024+((dx+k%w)&1023)]=p
    elif op in (0x24,0x25,0x26,0x27,0x2c,0x2d,0x2e,0x2f,0x34,0x35,0x36,0x37,0x3c,0x3d,0x3e,0x3f):
        gouraud=bool(op&0x10); quad=bool(op&8); tcidx=([2,4,6,8] if not gouraud else [2,5,8,11])[:4 if quad else 3]
        if max(tcidx)>=len(words): continue
        cl=words[tcidx[0]]>>16; tp=words[tcidx[1]]>>16
        bx=(tp&15)*64; by=((tp>>4)&1)*256; dep=(tp>>7)&3; cx=(cl&63)*16; cy=(cl>>6)&511
        uvs=[(words[z]&255,(words[z]>>8)&255) for z in tcidx]
        zero=total=0
        for u0,v0 in uvs:
            if dep==0:
                packed=v[(by+v0)*1024+bx+u0//4]; idx=(packed>>((u0&3)*4))&15; tex=v[cy*1024+cx+idx]
            elif dep==1:
                packed=v[(by+v0)*1024+bx+u0//2]; idx=(packed>>((u0&1)*8))&255; tex=v[cy*1024+cx+idx]
            else: tex=v[(by+v0)*1024+bx+u0]
            total+=1; zero+=tex==0
        stats[(op,dep,zero,total)]+=1
        if zero==total: byframe[frame]+=1

print('draw source samples (op depth zero/total):')
for k,n in stats.most_common(40): print('%02X d%d %d/%d %d'%(*k,n))
print('frames with all-zero textured vertex samples:')
print(byframe.most_common(40))
