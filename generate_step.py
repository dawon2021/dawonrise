#!/usr/bin/env python3
"""
T30 로타리 브로치 펀치 STEP AP214 파일 생성
3D B-rep 솔리드 모델: T30 치형 단면을 44mm 길이로 압출
"""
import math
from datetime import date

# ── 설계 파라미터 ─────────────────────────────────────────
R_OUT   = 26.3272   # 외경 반지름 mm
R_IN    = 24.9577   # 내경 반지름 mm
N       = 30        # 잇수
L       = 44.0      # 전체 길이 mm

# ── 2D 치형 프로파일 (60점: valley/tip 교대) ──────────────
profile = []
for i in range(N):
    # Valley
    a = math.radians(90.0 + (i - 0.5) * (360.0 / N))
    profile.append((R_IN * math.cos(a), R_IN * math.sin(a)))
    # Tip
    a = math.radians(90.0 + i * (360.0 / N))
    profile.append((R_OUT * math.cos(a), R_OUT * math.sin(a)))

M = len(profile)   # 60

# ── STEP 엔티티 빌더 ─────────────────────────────────────
entities = {}  # id -> line string
_next_id = [1]

def eid():
    i = _next_id[0]; _next_id[0] += 1; return i

def E(s):
    i = eid()
    entities[i] = s
    return i

def fmt_pt3(x, y, z):
    return f"({x:.6f},{y:.6f},{z:.6f})"

def fmt_dir(x, y, z):
    return f"({x:.6f},{y:.6f},{z:.6f})"

# ── 고정 구조 엔티티 ─────────────────────────────────────
e_app_ctx  = E("APPLICATION_CONTEXT('automotive design')")
e_app_prot = E(f"APPLICATION_PROTOCOL_DEFINITION('draft international standard','automotive_design',1998,#{e_app_ctx})")
e_prd_ctx  = E(f"PRODUCT_CONTEXT('',#{e_app_ctx},'mechanical')")
e_prd_def_ctx = E(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{e_app_ctx},'design')")
e_prd      = E(f"PRODUCT('T30-BROACH','T30 Rotary Broach Punch','',(#{e_prd_ctx}))")
e_prd_form = E(f"PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE('','',#{e_prd},.NOT_KNOWN.)")
e_prd_def  = E(f"PRODUCT_DEFINITION('design','',#{e_prd_form},#{e_prd_def_ctx})")
e_prd_shp  = E(f"PRODUCT_DEFINITION_SHAPE('','',#{e_prd_def})")

# Coordinate system
e_orig = E(f"CARTESIAN_POINT('Origin',(0.,0.,0.))")
e_zdir = E(f"DIRECTION('Z_Axis',(0.,0.,1.))")
e_xdir = E(f"DIRECTION('X_Axis',(1.,0.,0.))")
e_ap3d = E(f"AXIS2_PLACEMENT_3D('Global_CS',#{e_orig},#{e_zdir},#{e_xdir})")

e_geom_ctx = E(f"( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT"
               f"((#__UC__)) GLOBAL_UNIT_ASSIGNED_CONTEXT((#__LU__,#__AU__,#__SU__)) "
               f"REPRESENTATION_CONTEXT('Context #1','3D Context with UNIT and UNCERTAINTY') )")

# Units  (place-holders replaced after)
e_length_unit   = E("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )")
e_angle_unit    = E("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )")
e_solid_angle   = E("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )")
e_uncertainty   = E(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#{e_length_unit},'distance_accuracy_value','Confusion accuracy')")

# Fix place-holders in geom context
entities[e_geom_ctx] = (
    f"( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT"
    f"((#{e_uncertainty})) GLOBAL_UNIT_ASSIGNED_CONTEXT((#{e_length_unit},#{e_angle_unit},#{e_solid_angle})) "
    f"REPRESENTATION_CONTEXT('Context #1','3D Context with UNIT and UNCERTAINTY') )"
)

# ── B-rep 생성 ────────────────────────────────────────────
# 꼭짓점 생성: bottom z=0, top z=L
vert_bot = []   # VERTEX_POINT ids  (60개)
vert_top = []   # VERTEX_POINT ids  (60개)
cp_bot   = []   # CARTESIAN_POINT ids
cp_top   = []

coords_bot = []   # actual (x, y, z) tuples
coords_top = []

for x, y in profile:
    cb = E(f"CARTESIAN_POINT('',({x:.6f},{y:.6f},0.))")
    vb = E(f"VERTEX_POINT('',#{cb})")
    cp_bot.append(cb); vert_bot.append(vb)
    coords_bot.append((x, y, 0.0))

    ct = E(f"CARTESIAN_POINT('',({x:.6f},{y:.6f},{L:.1f}))")
    vt = E(f"VERTEX_POINT('',#{ct})")
    cp_top.append(ct); vert_top.append(vt)
    coords_top.append((x, y, L))

# 엣지 생성
# ① Bottom edges (60개): bot[i] → bot[(i+1)%M]
# ② Top edges (60개): top[i] → top[(i+1)%M]
# ③ Vertical edges (60개): bot[i] → top[i]

edge_bot  = []   # EDGE_CURVE ids
edge_top  = []
edge_vert = []

def make_line_edge(v_start, v_end, coords_start, coords_end, label):
    xs, ys, zs = coords_start
    xe, ye, ze = coords_end
    dx, dy, dz = xe - xs, ye - ys, ze - zs
    mag = math.sqrt(dx*dx + dy*dy + dz*dz)
    if mag < 1e-10: mag = 1.0
    e_cp0 = E(f"CARTESIAN_POINT('',({xs:.6f},{ys:.6f},{zs:.6f}))")
    e_dir = E(f"DIRECTION('',({dx/mag:.6f},{dy/mag:.6f},{dz/mag:.6f}))")
    e_vec = E(f"VECTOR('',#{e_dir},{mag:.6f})")
    e_line= E(f"LINE('',#{e_cp0},#{e_vec})")
    e_edge= E(f"EDGE_CURVE('{label}',#{v_start},#{v_end},#{e_line},.T.)")
    return e_edge

# Bottom ring edges
for i in range(M):
    j = (i + 1) % M
    edge_bot.append(make_line_edge(vert_bot[i], vert_bot[j], coords_bot[i], coords_bot[j], f'Bbot{i}'))

# Top ring edges
for i in range(M):
    j = (i + 1) % M
    edge_top.append(make_line_edge(vert_top[i], vert_top[j], coords_top[i], coords_top[j], f'Btop{i}'))

# Vertical edges
for i in range(M):
    edge_vert.append(make_line_edge(vert_bot[i], vert_top[i], coords_bot[i], coords_top[i], f'Bv{i}'))

# ORIENTED_EDGE helper
def oe(edge_id, same_sense: bool):
    s = '.T.' if same_sense else '.F.'
    return E(f"ORIENTED_EDGE('',*,*,#{edge_id},{s})")

# ── 면 생성 ─────────────────────────────────────────────
faces = []

# ① Bottom face (z=0), outward normal = (0,0,-1)
#    Loop: vert_bot 역방향 (CW from +z = outward -z)
bot_loop_oes = []
for i in range(M - 1, -1, -1):
    # reversed ring: edge_bot[(i-1)%M] reversed
    bot_loop_oes.append(oe(edge_bot[(i - 1) % M], False))
e_bot_loop = E(f"EDGE_LOOP('',({','.join('#'+str(x) for x in bot_loop_oes)}))")
e_bot_bound= E(f"FACE_OUTER_BOUND('',#{e_bot_loop},.T.)")
# Plane at z=0, normal (0,0,-1)
e_bot_cp   = E(f"CARTESIAN_POINT('',(0.,0.,0.))")
e_bot_nrm  = E(f"DIRECTION('',(0.,0.,-1.))")
e_bot_xd   = E(f"DIRECTION('',(1.,0.,0.))")
e_bot_ax   = E(f"AXIS2_PLACEMENT_3D('',#{e_bot_cp},#{e_bot_nrm},#{e_bot_xd})")
e_bot_pl   = E(f"PLANE('',#{e_bot_ax})")
e_bot_face = E(f"ADVANCED_FACE('Bottom',( #{e_bot_bound} ),#{e_bot_pl},.F.)")
faces.append(e_bot_face)

# ② Top face (z=L), outward normal = (0,0,+1)
#    Loop: vert_top 정방향 (CCW from +z)
top_loop_oes = []
for i in range(M):
    top_loop_oes.append(oe(edge_top[i], True))
e_top_loop = E(f"EDGE_LOOP('',({','.join('#'+str(x) for x in top_loop_oes)}))")
e_top_bound= E(f"FACE_OUTER_BOUND('',#{e_top_loop},.T.)")
e_top_cp   = E(f"CARTESIAN_POINT('',(0.,0.,{L:.1f}))")
e_top_nrm  = E(f"DIRECTION('',(0.,0.,1.))")
e_top_xd   = E(f"DIRECTION('',(1.,0.,0.))")
e_top_ax   = E(f"AXIS2_PLACEMENT_3D('',#{e_top_cp},#{e_top_nrm},#{e_top_xd})")
e_top_pl   = E(f"PLANE('',#{e_top_ax})")
e_top_face = E(f"ADVANCED_FACE('Top',( #{e_top_bound} ),#{e_top_pl},.T.)")
faces.append(e_top_face)

# ③ Side faces (60개)
#    Face i: bot[i] → bot[(i+1)%M] → top[(i+1)%M] → top[i]
for i in range(M):
    j = (i + 1) % M
    # Loop (CCW from outside = outward normal pointing out)
    # Going: bot[i]→bot[j] (edge_bot[i] forward)
    #        bot[j]→top[j] (edge_vert[j] forward)
    #        top[j]→top[i] (edge_top[i] reversed)
    #        top[i]→bot[i] (edge_vert[i] reversed)
    s_oes = [
        oe(edge_bot[i],  True),
        oe(edge_vert[j], True),
        oe(edge_top[i],  False),
        oe(edge_vert[i], False),
    ]
    e_s_loop  = E(f"EDGE_LOOP('',({','.join('#'+str(x) for x in s_oes)}))")
    e_s_bound = E(f"FACE_OUTER_BOUND('',#{e_s_loop},.T.)")

    # Plane normal: perpendicular to edge i, pointing outward
    x0, y0 = profile[i]
    x1, y1 = profile[j]
    dx, dy  = x1 - x0, y1 - y0
    mag     = math.sqrt(dx*dx + dy*dy)
    # outward normal = rotate edge direction 90° CW (for CCW profile)
    nx, ny  = dy / mag, -dx / mag
    # check: dot(n, midpoint) > 0 means outward
    mx, my  = (x0 + x1) / 2, (y0 + y1) / 2
    if nx * mx + ny * my < 0:
        nx, ny = -nx, -ny
    e_s_cp  = E(f"CARTESIAN_POINT('',({x0:.6f},{y0:.6f},0.))")
    e_s_nrm = E(f"DIRECTION('',({nx:.6f},{ny:.6f},0.))")
    e_s_xd  = E(f"DIRECTION('',(0.,0.,1.))")
    e_s_ax  = E(f"AXIS2_PLACEMENT_3D('',#{e_s_cp},#{e_s_nrm},#{e_s_xd})")
    e_s_pl  = E(f"PLANE('',#{e_s_ax})")
    e_s_fc  = E(f"ADVANCED_FACE('Side{i}',( #{e_s_bound} ),#{e_s_pl},.T.)")
    faces.append(e_s_fc)

# Closed shell & solid
face_refs = ','.join(f'#{f}' for f in faces)
e_shell = E(f"CLOSED_SHELL('T30Shell',({face_refs}))")
e_brep  = E(f"MANIFOLD_SOLID_BREP('T30_Broach',#{e_shell})")

# Shape representation
e_srep  = E(f"SHAPE_REPRESENTATION('T30_SR',(#{e_ap3d},#{e_brep}),#{e_geom_ctx})")
e_sdrep = E(f"SHAPE_DEFINITION_REPRESENTATION(#{e_prd_shp},#{e_srep})")

# ── STEP 파일 출력 ─────────────────────────────────────────
today = date.today().isoformat()
lines = [
    "ISO-10303-21;",
    "HEADER;",
    f"FILE_DESCRIPTION(('T30 Rotary Broach Punch - DAWONRISE'),'2;1');",
    f"FILE_NAME('T30_rotary_broach_punch.stp','{today}T00:00:00',",
    f"  ('DAWONRISE'),(''),'Custom STEP Writer 1.0','','');",
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));",
    "ENDSEC;",
    "DATA;",
]

for eid_num in sorted(entities.keys()):
    lines.append(f"#{eid_num}={entities[eid_num]};")

lines += ["ENDSEC;", "END-ISO-10303-21;"]

stp_content = "\n".join(lines)
with open("T30_rotary_broach_punch.stp", "w", encoding="utf-8") as f:
    f.write(stp_content)

print(f"STEP 생성 완료: T30_rotary_broach_punch.stp")
print(f"  총 엔티티 수: {len(entities)}")
print(f"  꼭짓점(Vertex): {M*2}개  |  엣지(Edge): {M*3}개  |  면(Face): {M+2}개")
