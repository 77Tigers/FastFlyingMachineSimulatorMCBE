import sys, mcs
FD = {0:'v',1:'^',2:'N',3:'S',4:'W',5:'E'}   # facing_direction -> letter
ST = {'north':'N','south':'S','east':'E','west':'W','up':'U','down':'D'}
def sym(n, st, be):
    if n=='slime': return ' sl'
    if n=='honey_block': return ' ho'
    if n=='red_wool': return ' RW'
    if n=='redstone_block': return ' RB'
    if n=='piston': return ' P'+FD[st['facing_direction']]+('x' if be and be['State']==2 else '')
    if n=='sticky_piston': return ' Q'+FD[st['facing_direction']]+('x' if be and be['State']==2 else '')
    if n.endswith('arm_collision'): return ' ~'+FD[st['facing_direction']]
    if n=='observer': return ' O'+ST[st['minecraft:facing_direction']]
    if n=='waxed_lightning_rod': return ' |'+FD[st['facing_direction']]
    if n=='lever': return ' lv'
    if n=='white_stained_glass': return ' GL'
    if n=='obsidian': return ' OB'
    return ' ??'
def show(path, ys=None):
    (sx,sy,sz), b = mcs.blocks(path)
    for y in range(sy):
        if ys and y not in ys: continue
        if not any(p[1]==y for p in b): continue
        print(f'--- y={y}  (columns x=0..{sx-1}, rows z=0..{sz-1} top=north)')
        print('    '+''.join(f'{x:3d}' for x in range(sx)))
        for z in range(sz):
            row=''.join(sym(*b[(x,y,z)]) if (x,y,z) in b else '  .' for x in range(sx))
            print(f'{z:3d} '+row)
if __name__=='__main__':
    show(sys.argv[1])
