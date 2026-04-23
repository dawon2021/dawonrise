#!/usr/bin/env python3
"""T30 로타리 브로치 펀치 DXF 도면 생성 (AutoCAD 호환)"""
import math
import ezdxf
from ezdxf.enums import TextEntityAlignment

# ── 설계 파라미터 ─────────────────────────────────────────
R_OUT   = 26.3272   # 외경 반지름 mm (Ø52.6543)
R_IN    = 24.9577   # 내경 반지름 mm (Ø49.9154)
N       = 30        # 잇수
L_TOTAL = 44.0
L_SHANK = 20.0
L_BODY  = 18.0
L_TOOTH = 6.0
TD      = R_OUT - R_IN  # 치형 깊이 1.3695mm

# ── DXF 문서 생성 ─────────────────────────────────────────
doc = ezdxf.new('R2010')
doc.header['$INSUNITS'] = 4   # mm
doc.header['$LTSCALE']  = 1.5
doc.header['$MEASUREMENT'] = 1  # metric

# 선종류 정의
doc.linetypes.add('DASHDOT', pattern=[1.25, -0.25, 0.25, -0.25],
                  description='Center line')
doc.linetypes.add('DASHED2', pattern=[0.5, -0.25],
                  description='Hidden line')

# 레이어 정의
for name, col, lt, lw in [
    ('OUTLINE',   7, 'Continuous', 50),
    ('CENTER',    1, 'DASHDOT',    18),
    ('HIDDEN',    8, 'DASHED2',    18),
    ('TEETH',     2, 'Continuous', 35),
    ('DIMENSION', 5, 'Continuous', 18),
    ('HATCH',     8, 'Continuous', 18),
    ('TEXT',      7, 'Continuous', 18),
    ('BORDER',    7, 'Continuous', 70),
]:
    doc.layers.new(name, dxfattribs={'color': col, 'linetype': lt, 'lineweight': lw})

msp = doc.modelspace()

# ── 치수 스타일 ────────────────────────────────────────────
ds = doc.dimstyles.new('T30')
ds.dxf.dimtxt  = 2.5
ds.dxf.dimasz  = 2.0
ds.dxf.dimexe  = 1.5
ds.dxf.dimexo  = 1.5
ds.dxf.dimdle  = 0.0
ds.dxf.dimdec  = 4
ds.dxf.dimclrt = 5   # dim text color: blue
ds.dxf.dimclrd = 5   # dim line color: blue
ds.dxf.dimclre = 5   # ext line color: blue

# ── 헬퍼 ─────────────────────────────────────────────────
def tooth_pts(cx, cy):
    pts = []
    for i in range(N):
        v_rad = math.radians(90 + (i - 0.5) * (360.0 / N))
        pts.append((cx + R_IN * math.cos(v_rad), cy + R_IN * math.sin(v_rad)))
        t_rad = math.radians(90 + i * (360.0 / N))
        pts.append((cx + R_OUT * math.cos(t_rad), cy + R_OUT * math.sin(t_rad)))
    return pts

def cl(x1, y1, x2, y2):
    msp.add_line((x1, y1), (x2, y2), dxfattribs={'layer': 'CENTER'})

def txt(s, x, y, h=2.5, align='LEFT'):
    msp.add_text(s, dxfattribs={'layer': 'TEXT', 'height': h,
                  'insert': (x, y), 'halign': 0})

# ════════════════════════════════════════════════════════════
# A. 정면도 (Front View)  origin: (0, 0)
# ════════════════════════════════════════════════════════════
CX, CY = 0.0, 0.0

# 치형 폴리곤
msp.add_lwpolyline(tooth_pts(CX, CY), close=True,
                   dxfattribs={'layer': 'TEETH'})

# 기준원 (가상선)
msp.add_circle((CX, CY), R_OUT, dxfattribs={'layer': 'HIDDEN'})
msp.add_circle((CX, CY), R_IN,  dxfattribs={'layer': 'HIDDEN'})

# 중심선
ext = 6
cl(CX - R_OUT - ext, CY, CX + R_OUT + ext, CY)
cl(CX, CY - R_OUT - ext, CX, CY + R_OUT + ext)

# 치수: Ø52.6543
msp.add_diameter_dim(center=(CX, CY), radius=R_OUT, angle=135,
                     dimstyle='T30',
                     dxfattribs={'layer': 'DIMENSION'}).render()

# 치수: Ø49.9154
msp.add_diameter_dim(center=(CX, CY), radius=R_IN, angle=315,
                     dimstyle='T30',
                     dxfattribs={'layer': 'DIMENSION'}).render()

# 치형각 주석
msp.add_text('∠120° (치형각)', dxfattribs={'layer': 'TEXT', 'height': 2.2,
              'insert': (CX + 2, CY - R_OUT + 3)})

# 정면도 레이블
msp.add_text('정면도 (절삭단)', dxfattribs={'layer': 'TEXT', 'height': 3.0,
              'insert': (CX - 14, CY - R_OUT - 10), 'style': 'Standard'})
msp.add_text(f'T30  |  Ø{R_OUT*2:.4f} / Ø{R_IN*2:.4f}', dxfattribs={
    'layer': 'TEXT', 'height': 2.2,
    'insert': (CX - 18, CY - R_OUT - 14)})

# ════════════════════════════════════════════════════════════
# B. 측면도 (Side View)  origin: (60, 0) 기준
# ════════════════════════════════════════════════════════════
GAP     = 22.0
SL      = CX + R_OUT + GAP       # left  x
SR      = SL + L_TOTAL            # right x
ST      = CY + R_OUT              # top   y
SB      = CY - R_OUT              # bottom y
SCY     = CY                      # center y

SH_X    = SL + L_SHANK            # shank / body 경계
BD_X    = SH_X + L_BODY           # body / tooth 경계

# 외곽 사각형
msp.add_lwpolyline([(SL, ST), (SR, ST), (SR, SB), (SL, SB)], close=True,
                   dxfattribs={'layer': 'OUTLINE'})

# 구간 경계선 (가상선)
for bx in [SH_X, BD_X]:
    msp.add_line((bx, ST + 3), (bx, SB - 3), dxfattribs={'layer': 'HIDDEN'})

# 중심선
cl(SL - 5, SCY, SR + 20, SCY)

# 치형부 요철 (측면) - 상하 폴리라인
def sv_teeth_polyline(top: bool):
    n_sv  = 14
    pitch = L_TOOTH / n_sv
    sign  = 1 if top else -1
    base  = ST if top else SB
    pts   = [(BD_X, base)]
    for j in range(1, n_sv * 2 + 2):
        fx = BD_X + j * pitch / 2
        if fx > SR: fx = SR
        fy = base + sign * (TD if j % 2 == 1 else 0)
        pts.append((fx, fy))
        if fx >= SR:
            break
    return pts

msp.add_lwpolyline(sv_teeth_polyline(True),  dxfattribs={'layer': 'TEETH'})
msp.add_lwpolyline(sv_teeth_polyline(False), dxfattribs={'layer': 'TEETH'})

# 샹크/바디 구간 해칭 표시 (크로스해칭 단순화 - 사선)
hatch_y = SB + 2
for xi in range(int(SL), int(SR - L_TOOTH * 1), 4):
    msp.add_line((xi, SB + 0.5), (xi + 6, ST - 0.5),
                 dxfattribs={'layer': 'HATCH'})

# ── 치수선 (측면도) ────────────────────────────────────────
DY_TOP = ST + 8   # 상단 치수선 y 기준

# 전체 44mm
msp.add_linear_dim(base=(SL, DY_TOP + 10), p1=(SL, SCY), p2=(SR, SCY),
                   angle=0, dimstyle='T30',
                   dxfattribs={'layer': 'DIMENSION'}).render()
# 샹크 20mm
msp.add_linear_dim(base=(SL, DY_TOP + 5), p1=(SL, SCY), p2=(SH_X, SCY),
                   angle=0, dimstyle='T30',
                   dxfattribs={'layer': 'DIMENSION'}).render()
# 치형부 6mm
msp.add_linear_dim(base=(BD_X, DY_TOP + 5), p1=(BD_X, SCY), p2=(SR, SCY),
                   angle=0, dimstyle='T30',
                   dxfattribs={'layer': 'DIMENSION'}).render()
# 바디 18mm
msp.add_linear_dim(base=(SH_X, DY_TOP + 5), p1=(SH_X, SCY), p2=(BD_X, SCY),
                   angle=0, dimstyle='T30',
                   dxfattribs={'layer': 'DIMENSION'}).render()
# 직경 수직 치수
msp.add_linear_dim(base=(SR + 12, SCY), p1=(SR, ST), p2=(SR, SB),
                   angle=90, dimstyle='T30',
                   dxfattribs={'layer': 'DIMENSION'}).render()

# 구간 레이블
for bx, bw, label in [
    (SL,   L_SHANK, f'샹크 {L_SHANK:.0f}mm'),
    (SH_X, L_BODY,  f'바디 {L_BODY:.0f}mm'),
    (BD_X, L_TOOTH, f'치형부 {L_TOOTH:.0f}mm'),
]:
    msp.add_text(label, dxfattribs={'layer': 'TEXT', 'height': 2.2,
                  'insert': (bx + bw * 0.15, SB - 7)})

# 측면도 레이블
msp.add_text('측면도', dxfattribs={'layer': 'TEXT', 'height': 3.0,
              'insert': (SL + L_TOTAL / 2 - 5, SB - 11)})

# ════════════════════════════════════════════════════════════
# C. 치형 상세 확대도 (Detail View)
# ════════════════════════════════════════════════════════════
DX, DY   = CX, CY - R_OUT - 35   # 정면도 아래에 배치
DET_SC   = 6.0   # 확대 배율 (실제 mm 기준 3개 이빨 표시)
DET_CX   = DX
DET_CY   = DY

# 3개 이빨 (-1, 0, +1) 확대 표시
det_pts = []
for i in range(-2, 4):
    v_rad = math.radians(90 + (i - 0.5) * (360.0 / N))
    det_pts.append((DET_CX + R_IN * DET_SC * math.cos(v_rad),
                    DET_CY + R_IN * DET_SC * math.sin(v_rad)))
    t_rad = math.radians(90 + i * (360.0 / N))
    det_pts.append((DET_CX + R_OUT * DET_SC * math.cos(t_rad),
                    DET_CY + R_OUT * DET_SC * math.sin(t_rad)))

msp.add_lwpolyline(det_pts, dxfattribs={'layer': 'TEETH'})

# 치형 깊이 치수
tx0, ty0 = det_pts[1]   # 첫 팁
tx1, ty1 = det_pts[2]   # 다음 밸리 (R_IN)
msp.add_linear_dim(base=(tx0 + 8, (ty0 + ty1) / 2), p1=(tx0, ty0), p2=(tx1, ty1),
                   angle=90, dimstyle='T30',
                   dxfattribs={'layer': 'DIMENSION'}).render()
msp.add_text(f'치형깊이 {TD:.4f}mm (×{DET_SC:.0f})', dxfattribs={
    'layer': 'TEXT', 'height': 2.2,
    'insert': (DET_CX - 25, DET_CY - R_OUT * DET_SC - 6)})
msp.add_text(f'상세도 (배율 {DET_SC:.0f}:1)', dxfattribs={
    'layer': 'TEXT', 'height': 3.0,
    'insert': (DET_CX - 18, DET_CY - R_OUT * DET_SC - 10)})

# ════════════════════════════════════════════════════════════
# D. 도면 테두리 & 타이틀 블록
# ════════════════════════════════════════════════════════════
BX1, BY1 = -40, -200
BX2, BY2 = SR + 40, ST + 30

msp.add_lwpolyline([(BX1, BY1), (BX2, BY1), (BX2, BY2), (BX1, BY2)],
                   close=True, dxfattribs={'layer': 'BORDER'})

# 타이틀 블록 (우하단)
TBX = BX2 - 120
TBY = BY1 + 5
msp.add_lwpolyline([(TBX, BY1), (BX2, BY1), (BX2, BY1 + 35), (TBX, BY1 + 35)],
                   close=True, dxfattribs={'layer': 'BORDER'})

tb_lines = [
    (3.5, '품  명 : T30 로타리 브로치 펀치'),
    (2.5, f'외  경 : Ø{R_OUT*2:.4f} mm    내경 : Ø{R_IN*2:.4f} mm'),
    (2.5, f'잇  수 : {N}개    치형각 : 120°    치형깊이 : {TD:.4f} mm'),
    (2.5, f'전체길이 : {L_TOTAL}mm  (샹크{L_SHANK}+바디{L_BODY}+치형{L_TOOTH})'),
    (2.5, '피삭재 : AL6061 t6.0  |  공구경도 : 62~65 HRC  |  코팅 : DLC/AlCrN'),
    (2.2, 'DAWONRISE  |  DWG-T30-001  |  Rev.A  |  2026-04-23'),
]
for k, (h, s) in enumerate(tb_lines):
    msp.add_text(s, dxfattribs={'layer': 'TEXT', 'height': h,
                  'insert': (TBX + 2, TBY + (len(tb_lines) - 1 - k) * 5)})

# 주의사항 박스
NX = BX1 + 2
NY = BY1 + 5
msp.add_lwpolyline([(NX, NY), (TBX - 2, NY), (TBX - 2, NY + 20), (NX, NY + 20)],
                   close=True, dxfattribs={'layer': 'DIMENSION'})
msp.add_text('⚠ 주의사항', dxfattribs={'layer': 'TEXT', 'height': 2.8,
              'insert': (NX + 2, NY + 16)})
notes = [
    '① 치형부 6mm = 피삭재 두께 6mm → 선단챔퍼 0.5mm×15° 이하로 최소화 (또는 절삭부 7mm 이상 검토)',
    '② AL6061 BUE 방지 → DLC/AlCrN 코팅 필수 / 알루미늄 전용 에멀젼 절삭유 공급',
    '③ 틸트각 1°±0.1° / 볼시트 정밀도 확인 / 가공 후 전체 치형 CMM 검사 실시',
]
for k, n in enumerate(notes):
    msp.add_text(n, dxfattribs={'layer': 'TEXT', 'height': 2.0,
                  'insert': (NX + 2, NY + 11 - k * 4)})

# ── 저장 ─────────────────────────────────────────────────
doc.saveas('T30_rotary_broach_punch.dxf')
print('DXF 생성 완료: T30_rotary_broach_punch.dxf')
