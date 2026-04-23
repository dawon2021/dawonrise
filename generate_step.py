#!/usr/bin/env python3
"""
T30 로타리 브로치 펀치 STEP AP214 생성
형상: Ø25 원통(샹크+바디 38mm) + T30 치형부(8mm), 단차 있음
"""
import math
from datetime import date

# ── 설계 파라미터 ─────────────────────────────────────────
R_OUT    = 26.3272   # 치형 외경 반지름 mm
R_IN     = 24.9577   # 치형 내경 반지름 mm
R_SHANK  = 12.5      # 샹크/바디 반지름 mm (Ø25)
N_TEETH  = 30
L_SHANK  = 20.0
L_BODY   = 18.0
L_TOOTH  = 8.0
L_CYL    = L_SHANK + L_BODY    # 38mm
L_TOTAL  = L_CYL + L_TOOTH     # 46mm

# ── 프로파일 포인트 생성 ──────────────────────────────────
# Ø25 원통 단면 (60각형 근사)
N_CYL = 60
cyl_profile = [
    (R_SHANK * math.cos(math.radians(i * 360.0 / N_CYL)),
     R_SHANK * math.sin(math.radians(i * 360.0 / N_CYL)))
    for i in range(N_CYL)
]

# T30 치형 단면 (60점: valley/tip 교대)
tooth_profile = []
for i in range(N_TEETH):
    a = math.radians(90.0 + (i - 0.5) * (360.0 / N_TEETH))
    tooth_profile.append((R_IN * math.cos(a), R_IN * math.sin(a)))
    a = math.radians(90.0 + i * (360.0 / N_TEETH))
    tooth_profile.append((R_OUT * math.cos(a), R_OUT * math.sin(a)))

MC = len(cyl_profile)    # 60
MT = len(tooth_profile)  # 60

# ── STEP 엔티티 빌더 ─────────────────────────────────────
entities = {}
_id = [1]

def eid(): i = _id[0]; _id[0] += 1; return i
def E(s): i = eid(); entities[i] = s; return i

# ── 고정 구조 엔티티 ─────────────────────────────────────
e_app   = E("APPLICATION_CONTEXT('automotive design')")
E(f"APPLICATION_PROTOCOL_DEFINITION('draft international standard','automotive_design',1998,#{e_app})")
e_pctx  = E(f"PRODUCT_CONTEXT('',#{e_app},'mechanical')")
e_dctx  = E(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{e_app},'design')")
e_prod  = E(f"PRODUCT('T30-BROACH','T30 Rotary Broach Punch','',(#{e_pctx}))")
e_form  = E(f"PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE('','',#{e_prod},.NOT_KNOWN.)")
e_pdef  = E(f"PRODUCT_DEFINITION('design','',#{e_form},#{e_dctx})")
e_pshp  = E(f"PRODUCT_DEFINITION_SHAPE('','',#{e_pdef})")

e_orig  = E("CARTESIAN_POINT('Origin',(0.,0.,0.))")
e_zd    = E("DIRECTION('Z',(0.,0.,1.))")
e_xd    = E("DIRECTION('X',(1.,0.,0.))")
e_ap3d  = E(f"AXIS2_PLACEMENT_3D('CS',#{e_orig},#{e_zd},#{e_xd})")

e_lu    = E("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )")
e_au    = E("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )")
e_su    = E("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )")
e_unc   = E(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#{e_lu},'distance_accuracy_value','Confusion accuracy')")
e_gctx  = E(f"( GEOMETRIC_REPRESENTATION_CONTEXT(3) "
            f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{e_unc})) "
            f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{e_lu},#{e_au},#{e_su})) "
            f"REPRESENTATION_CONTEXT('Context','3D') )")

# ── 꼭짓점 생성 ──────────────────────────────────────────
# z=0      : Ø25 원형 (bottom of shank)
# z=L_CYL  : Ø25 원형 (top of cylinder = shoulder inner)
# z=L_CYL  : T30 프로파일 (shoulder outer = bottom of tooth)
# z=L_TOTAL: T30 프로파일 (top of tooth)

def make_verts(profile, z):
    cps, vps = [], []
    for x, y in profile:
        cp = E(f"CARTESIAN_POINT('',({x:.6f},{y:.6f},{z:.4f}))")
        vp = E(f"VERTEX_POINT('',#{cp})")
        cps.append(cp); vps.append(vp)
    return cps, vps

cp_bc, vp_bc = make_verts(cyl_profile,   0.0)        # bottom cylinder
cp_tc, vp_tc = make_verts(cyl_profile,   L_CYL)      # top cylinder / shoulder inner
cp_bt, vp_bt = make_verts(tooth_profile, L_CYL)      # bottom tooth / shoulder outer
cp_tt, vp_tt = make_verts(tooth_profile, L_TOTAL)    # top tooth

coords_bc = [(x, y, 0.0)     for x, y in cyl_profile]
coords_tc = [(x, y, L_CYL)   for x, y in cyl_profile]
coords_bt = [(x, y, L_CYL)   for x, y in tooth_profile]
coords_tt = [(x, y, L_TOTAL) for x, y in tooth_profile]

# ── 엣지 생성 ────────────────────────────────────────────
def line_edge(vs, ve, cs, ce, lbl):
    xs, ys, zs = cs; xe, ye, ze = ce
    dx, dy, dz = xe-xs, ye-ys, ze-zs
    mag = math.sqrt(dx*dx+dy*dy+dz*dz) or 1.0
    ec  = E(f"CARTESIAN_POINT('',({xs:.6f},{ys:.6f},{zs:.6f}))")
    ed  = E(f"DIRECTION('',({dx/mag:.6f},{dy/mag:.6f},{dz/mag:.6f}))")
    ev  = E(f"VECTOR('',#{ed},{mag:.6f})")
    el  = E(f"LINE('',#{ec},#{ev})")
    return E(f"EDGE_CURVE('{lbl}',#{vs},#{ve},#{el},.T.)")

def ring_edges(vps, coords, prefix):
    M = len(vps)
    return [line_edge(vps[i], vps[(i+1)%M], coords[i], coords[(i+1)%M], f'{prefix}{i}')
            for i in range(M)]

def vert_edges(vps_bot, vps_top, coords_bot, coords_top, prefix):
    return [line_edge(vps_bot[i], vps_top[i], coords_bot[i], coords_top[i], f'{prefix}{i}')
            for i in range(len(vps_bot))]

e_bot_ring  = ring_edges(vp_bc, coords_bc, 'BR')   # bottom circle ring
e_cyl_vert  = vert_edges(vp_bc, vp_tc, coords_bc, coords_tc, 'CV')  # cylinder vertical
e_cyl_ring  = ring_edges(vp_tc, coords_tc, 'CR')   # top cylinder / shoulder inner
e_tbt_ring  = ring_edges(vp_bt, coords_bt, 'TB')   # tooth bottom ring
e_tooth_vert= vert_edges(vp_bt, vp_tt, coords_bt, coords_tt, 'TV')  # tooth vertical
e_top_ring  = ring_edges(vp_tt, coords_tt, 'TR')   # top tooth ring

# ── ORIENTED_EDGE 헬퍼 ────────────────────────────────────
def oe(e, fwd): return E(f"ORIENTED_EDGE('',*,*,#{e},{'T' if fwd else 'F'}.)")

# ── 면 생성 ─────────────────────────────────────────────
faces = []

def make_plane_face(label, loop_oes, extra_bounds, nx, ny, nz, px, py, pz, same_sense):
    loop   = E(f"EDGE_LOOP('',({','.join('#'+str(x) for x in loop_oes)}))")
    bound  = E(f"FACE_OUTER_BOUND('',#{loop},.T.)")
    bounds = f"#{bound}"
    for (inner_oes, ss) in extra_bounds:
        il = E(f"EDGE_LOOP('',({','.join('#'+str(x) for x in inner_oes)}))")
        ib = E(f"FACE_BOUND('',#{il},.{ss}.)")
        bounds += f",#{ib}"
    cp = E(f"CARTESIAN_POINT('',({px:.4f},{py:.4f},{pz:.4f}))")
    nd = E(f"DIRECTION('',({nx:.6f},{ny:.6f},{nz:.6f}))")
    xd = E(f"DIRECTION('',(1.,0.,0.))")
    ax = E(f"AXIS2_PLACEMENT_3D('',#{cp},#{nd},#{xd})")
    pl = E(f"PLANE('',#{ax})")
    f  = E(f"ADVANCED_FACE('{label}',({bounds}),#{pl},.{'T' if same_sense else 'F'}.)")
    faces.append(f)

# 1. Bottom face (z=0), normal -z
#    Loop: bot_ring 역방향 (CW from +z = outward -z)
bot_oes = [oe(e_bot_ring[(i-1)%MC], False) for i in range(MC-1, -1, -1)]
make_plane_face('Bottom', bot_oes, [], 0, 0, -1, 0, 0, 0, False)

# 2. Cylinder lateral faces (60 quads)
for i in range(MC):
    j = (i+1) % MC
    x0,y0,_ = coords_bc[i]; x1,y1,_ = coords_bc[j]
    dx,dy = x1-x0, y1-y0; mag = math.sqrt(dx*dx+dy*dy) or 1.0
    nx,ny = dy/mag, -dx/mag  # outward radial
    if nx*(x0+x1)/2 + ny*(y0+y1)/2 < 0: nx,ny = -nx,-ny
    s_oes = [oe(e_bot_ring[i], True), oe(e_cyl_vert[j], True),
             oe(e_cyl_ring[i], False), oe(e_cyl_vert[i], False)]
    loop  = E(f"EDGE_LOOP('',({','.join('#'+str(x) for x in s_oes)}))")
    bound = E(f"FACE_OUTER_BOUND('',#{loop},.T.)")
    cp    = E(f"CARTESIAN_POINT('',({x0:.6f},{y0:.6f},0.))")
    nd    = E(f"DIRECTION('',({nx:.6f},{ny:.6f},0.))")
    xv    = E(f"DIRECTION('',(0.,0.,1.))")
    ax    = E(f"AXIS2_PLACEMENT_3D('',#{cp},#{nd},#{xv})")
    pl    = E(f"PLANE('',#{ax})")
    faces.append(E(f"ADVANCED_FACE('Cyl{i}',(#{bound}),#{pl},.T.)"))

# 3. Shoulder face (z=L_CYL, annular: outer=tooth_bot, inner=cyl_top, normal -z)
#    Outer: tooth_bot_ring 역방향 (CW from +z)
sh_outer = [oe(e_tbt_ring[(i-1)%MT], False) for i in range(MT-1, -1, -1)]
#    Inner hole: cyl_top_ring 정방향 (CCW from +z when viewed as hole)
sh_inner_oes = [oe(e_cyl_ring[i], True) for i in range(MC)]
make_plane_face('Shoulder', sh_outer,
                [(sh_inner_oes, 'T')],
                0, 0, -1, 0, 0, L_CYL, False)

# 4. Tooth lateral faces (60 quads)
for i in range(MT):
    j = (i+1) % MT
    x0,y0,_ = coords_bt[i]; x1,y1,_ = coords_bt[j]
    dx,dy = x1-x0, y1-y0; mag = math.sqrt(dx*dx+dy*dy) or 1.0
    nx,ny = dy/mag, -dx/mag
    if nx*(x0+x1)/2 + ny*(y0+y1)/2 < 0: nx,ny = -nx,-ny
    s_oes = [oe(e_tbt_ring[i], True), oe(e_tooth_vert[j], True),
             oe(e_top_ring[i], False), oe(e_tooth_vert[i], False)]
    loop  = E(f"EDGE_LOOP('',({','.join('#'+str(x) for x in s_oes)}))")
    bound = E(f"FACE_OUTER_BOUND('',#{loop},.T.)")
    cp    = E(f"CARTESIAN_POINT('',({x0:.6f},{y0:.6f},{L_CYL:.4f}))")
    nd    = E(f"DIRECTION('',({nx:.6f},{ny:.6f},0.))")
    xv    = E(f"DIRECTION('',(0.,0.,1.))")
    ax    = E(f"AXIS2_PLACEMENT_3D('',#{cp},#{nd},#{xv})")
    pl    = E(f"PLANE('',#{ax})")
    faces.append(E(f"ADVANCED_FACE('Tooth{i}',(#{bound}),#{pl},.T.)"))

# 5. Top face (z=L_TOTAL), normal +z, CCW from +z
top_oes = [oe(e_top_ring[i], True) for i in range(MT)]
make_plane_face('Top', top_oes, [], 0, 0, 1, 0, 0, L_TOTAL, True)

# ── 솔리드 조립 ─────────────────────────────────────────
face_refs = ','.join(f'#{f}' for f in faces)
e_shell = E(f"CLOSED_SHELL('T30Shell',({face_refs}))")
e_brep  = E(f"MANIFOLD_SOLID_BREP('T30_Broach_Punch',#{e_shell})")
e_srep  = E(f"SHAPE_REPRESENTATION('T30_SR',(#{e_ap3d},#{e_brep}),#{e_gctx})")
E(f"SHAPE_DEFINITION_REPRESENTATION(#{e_pshp},#{e_srep})")

# ── 파일 출력 ─────────────────────────────────────────────
today = date.today().isoformat()
lines = [
    "ISO-10303-21;",
    "HEADER;",
    "FILE_DESCRIPTION(('T30 Rotary Broach Punch - Stepped Shank Ø25 + Tooth Ø52.6543'),'2;1');",
    f"FILE_NAME('T30_rotary_broach_punch.stp','{today}T00:00:00',",
    "  ('DAWONRISE'),(''),'Custom STEP Writer 2.0','','');",
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));",
    "ENDSEC;",
    "DATA;",
]
for k in sorted(entities.keys()):
    lines.append(f"#{k}={entities[k]};")
lines += ["ENDSEC;", "END-ISO-10303-21;"]

with open('T30_rotary_broach_punch.stp', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

n_verts = MC*2 + MT*2
n_edges = MC*2 + MT*2 + MC + MT
n_faces = 1 + MC + 1 + MT + 1
print(f'STEP 생성 완료: T30_rotary_broach_punch.stp')
print(f'  엔티티 수: {len(entities)}  꼭짓점: {n_verts}  엣지: {n_edges}  면: {n_faces}')
print(f'  형상: Ø25×{L_CYL:.0f}mm(샹크+바디) + T30×{L_TOOTH:.0f}mm(치형) = {L_TOTAL:.0f}mm')
