#!/usr/bin/env python3
"""T30 로타리 브로치 펀치 DXF 도면 생성 (단차 형상 반영)"""
import math
import ezdxf

# ── 설계 파라미터 ─────────────────────────────────────────
R_OUT    = 26.3272   # 치형 외경 반지름 mm (Ø52.6543)
R_IN     = 24.9577   # 치형 내경 반지름 mm (Ø49.9154)
R_SHANK  = 12.5      # 샹크/바디 반지름 mm (Ø25)
N        = 30
L_SHANK  = 20.0
L_BODY   = 18.0
L_TOOTH  = 8.0
L_CYL    = L_SHANK + L_BODY   # 38mm (단일 원통부)
L_TOTAL  = L_CYL + L_TOOTH    # 46mm
TD       = R_OUT - R_IN        # 치형 깊이 1.3695mm

doc = ezdxf.new('R2010')
doc.header['$INSUNITS'] = 4
doc.header['$LTSCALE']  = 1.5
doc.header['$MEASUREMENT'] = 1

doc.linetypes.add('DASHDOT', pattern=[1.25, -0.25, 0.25, -0.25])
doc.linetypes.add('DASHED2', pattern=[0.5, -0.25])

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

ds = doc.dimstyles.new('T30')
ds.dxf.dimtxt  = 2.5
ds.dxf.dimasz  = 2.0
ds.dxf.dimexe  = 1.5
ds.dxf.dimexo  = 1.5
ds.dxf.dimdle  = 0.0
ds.dxf.dimdec  = 4
ds.dxf.dimclrt = 5
ds.dxf.dimclrd = 5
ds.dxf.dimclre = 5

def tooth_pts(cx, cy):
    pts = []
    for i in range(N):
        v_rad = math.radians(90 + (i - 0.5) * (360.0 / N))
        pts.append((cx + R_IN * math.cos(v_rad), cy + R_IN * math.sin(v_rad)))
        t_rad = math.radians(90 + i * (360.0 / N))
        pts.append((cx + R_OUT * math.cos(t_rad), cy + R_OUT * math.sin(t_rad)))
    return pts

# ════════════════════════════════════════════════════════════
# A. 정면도 (절삭단)
# ════════════════════════════════════════════════════════════
CX, CY = 0.0, 0.0
msp.add_lwpolyline(tooth_pts(CX, CY), close=True, dxfattribs={'layer': 'TEETH'})
msp.add_circle((CX, CY), R_OUT, dxfattribs={'layer': 'HIDDEN'})
msp.add_circle((CX, CY), R_IN,  dxfattribs={'layer': 'HIDDEN'})

ext = 6
msp.add_line((CX - R_OUT - ext, CY), (CX + R_OUT + ext, CY), dxfattribs={'layer': 'CENTER'})
msp.add_line((CX, CY - R_OUT - ext), (CX, CY + R_OUT + ext), dxfattribs={'layer': 'CENTER'})

msp.add_diameter_dim(center=(CX, CY), radius=R_OUT, angle=135,
                     dimstyle='T30', dxfattribs={'layer': 'DIMENSION'}).render()
msp.add_diameter_dim(center=(CX, CY), radius=R_IN, angle=315,
                     dimstyle='T30', dxfattribs={'layer': 'DIMENSION'}).render()
msp.add_text('∠120° (치형각)', dxfattribs={'layer': 'TEXT', 'height': 2.2,
              'insert': (CX + 2, CY - R_OUT + 3)})
msp.add_text('정면도 (절삭단) T30', dxfattribs={'layer': 'TEXT', 'height': 3.0,
              'insert': (CX - 16, CY - R_OUT - 10)})

# ════════════════════════════════════════════════════════════
# B. 샹크 단면도 (Ø25 원형)
# ════════════════════════════════════════════════════════════
SCX, SCY = 70.0, 0.0
msp.add_circle((SCX, SCY), R_SHANK, dxfattribs={'layer': 'OUTLINE'})
msp.add_line((SCX - R_SHANK - ext, SCY), (SCX + R_SHANK + ext, SCY), dxfattribs={'layer': 'CENTER'})
msp.add_line((SCX, SCY - R_SHANK - ext), (SCX, SCY + R_SHANK + ext), dxfattribs={'layer': 'CENTER'})
msp.add_diameter_dim(center=(SCX, SCY), radius=R_SHANK, angle=135,
                     dimstyle='T30', dxfattribs={'layer': 'DIMENSION'}).render()
msp.add_text('샹크/바디 단면 (Ø25)', dxfattribs={'layer': 'TEXT', 'height': 2.5,
              'insert': (SCX - 16, SCY - R_SHANK - 9)})

# ════════════════════════════════════════════════════════════
# C. 측면도 (단차 형상 반영)
# ════════════════════════════════════════════════════════════
GAP  = 22.0
SL   = CX + R_OUT + GAP    # 왼쪽 끝 x
SCY2 = 0.0                  # 중심 y
SH_X = SL + L_SHANK         # 샹크/바디 경계
BD_X = SL + L_CYL           # 바디/치형 경계 (=38mm 지점)
SR   = SL + L_TOTAL          # 오른쪽 끝 x

# 외곽 윤곽선 (단차형)
# 상단 라인: 샹크+바디 (y=R_SHANK) → 숄더 단차 → 치형부 (y=R_OUT)
top_outline = [
    (SL,   SCY2 + R_SHANK),
    (BD_X, SCY2 + R_SHANK),
    (BD_X, SCY2 + R_OUT),
    (SR,   SCY2 + R_OUT),
]
bot_outline = [
    (SL,   SCY2 - R_SHANK),
    (BD_X, SCY2 - R_SHANK),
    (BD_X, SCY2 - R_OUT),
    (SR,   SCY2 - R_OUT),
]

# 왼쪽 끝 / 오른쪽 끝
msp.add_line((SL, SCY2 + R_SHANK), (SL, SCY2 - R_SHANK), dxfattribs={'layer': 'OUTLINE'})
msp.add_line((SR, SCY2 + R_OUT),   (SR, SCY2 - R_OUT),   dxfattribs={'layer': 'OUTLINE'})
# 상단 윤곽
msp.add_lwpolyline(top_outline, dxfattribs={'layer': 'OUTLINE'})
# 하단 윤곽
msp.add_lwpolyline(bot_outline, dxfattribs={'layer': 'OUTLINE'})

# 샹크/바디 내부 구분선 (가상선)
msp.add_line((SH_X, SCY2 + R_SHANK + 3), (SH_X, SCY2 - R_SHANK - 3),
             dxfattribs={'layer': 'HIDDEN'})

# 중심선
msp.add_line((SL - 5, SCY2), (SR + 22, SCY2), dxfattribs={'layer': 'CENTER'})

# 치형 요철 (측면 - 상하)
def sv_teeth(top: bool):
    n_sv  = 14
    pitch = L_TOOTH / n_sv
    sign  = 1 if top else -1
    base  = SCY2 + sign * R_OUT
    pts   = [(BD_X, base)]
    for j in range(1, n_sv * 2 + 2):
        fx = BD_X + j * pitch / 2
        if fx > SR: fx = SR
        fy = base + sign * (TD if j % 2 == 1 else 0)
        pts.append((fx, fy))
        if fx >= SR:
            break
    return pts

msp.add_lwpolyline(sv_teeth(True),  dxfattribs={'layer': 'TEETH'})
msp.add_lwpolyline(sv_teeth(False), dxfattribs={'layer': 'TEETH'})

# 샹크+바디 해칭
for xi in range(int(SL), int(BD_X), 5):
    msp.add_line((xi, SCY2 - R_SHANK + 0.5), (xi + 7, SCY2 + R_SHANK - 0.5),
                 dxfattribs={'layer': 'HATCH'})

# ── 치수선 ──────────────────────────────────────────────────
DY_TOP = SCY2 + R_OUT + 8

# 전체 46mm
msp.add_linear_dim(base=(SL, DY_TOP + 12), p1=(SL, SCY2), p2=(SR, SCY2),
                   angle=0, dimstyle='T30', dxfattribs={'layer': 'DIMENSION'}).render()
# 샹크 20mm
msp.add_linear_dim(base=(SL, DY_TOP + 7), p1=(SL, SCY2), p2=(SH_X, SCY2),
                   angle=0, dimstyle='T30', dxfattribs={'layer': 'DIMENSION'}).render()
# 바디 18mm
msp.add_linear_dim(base=(SH_X, DY_TOP + 7), p1=(SH_X, SCY2), p2=(BD_X, SCY2),
                   angle=0, dimstyle='T30', dxfattribs={'layer': 'DIMENSION'}).render()
# 치형부 8mm
msp.add_linear_dim(base=(BD_X, DY_TOP + 7), p1=(BD_X, SCY2), p2=(SR, SCY2),
                   angle=0, dimstyle='T30', dxfattribs={'layer': 'DIMENSION'}).render()

# 샹크 직경 Ø25 (수직)
msp.add_linear_dim(base=(SH_X - 5, SCY2), p1=(SH_X, SCY2 + R_SHANK),
                   p2=(SH_X, SCY2 - R_SHANK), angle=90, dimstyle='T30',
                   dxfattribs={'layer': 'DIMENSION'}).render()
# 치형 외경 Ø52.6543 (수직)
msp.add_linear_dim(base=(SR + 14, SCY2), p1=(SR, SCY2 + R_OUT),
                   p2=(SR, SCY2 - R_OUT), angle=90, dimstyle='T30',
                   dxfattribs={'layer': 'DIMENSION'}).render()

# 구간 레이블
for bx, bw, lbl in [
    (SL,   L_SHANK, f'샹크\nØ25×{L_SHANK:.0f}'),
    (SH_X, L_BODY,  f'바디\nØ25×{L_BODY:.0f}'),
    (BD_X, L_TOOTH, f'치형부\nØ52.6×{L_TOOTH:.0f}'),
]:
    for k, part in enumerate(lbl.split('\n')):
        msp.add_text(part, dxfattribs={'layer': 'TEXT', 'height': 2.2,
                      'insert': (bx + bw * 0.15, SCY2 - R_OUT - 7 - k * 4)})

msp.add_text('측면도', dxfattribs={'layer': 'TEXT', 'height': 3.0,
              'insert': (SL + L_TOTAL / 2 - 5, SCY2 - R_OUT - 16)})

# ════════════════════════════════════════════════════════════
# D. 타이틀 블록 & 주의사항
# ════════════════════════════════════════════════════════════
BX1, BY1 = -40, -230
BX2, BY2 = SR + 45, SCY2 + R_OUT + 30

msp.add_lwpolyline([(BX1, BY1), (BX2, BY1), (BX2, BY2), (BX1, BY2)],
                   close=True, dxfattribs={'layer': 'BORDER'})

TBX, TBY = BX2 - 130, BY1 + 5
msp.add_lwpolyline([(TBX, BY1), (BX2, BY1), (BX2, BY1 + 38), (TBX, BY1 + 38)],
                   close=True, dxfattribs={'layer': 'BORDER'})

tb_lines = [
    (3.5, '품  명 : T30 로타리 브로치 펀치'),
    (2.5, f'치형외경: Ø{R_OUT*2:.4f}  치형내경: Ø{R_IN*2:.4f}  잇수: {N}  치형각: 120°'),
    (2.5, f'샹크/바디: Ø25  |  샹크:{L_SHANK:.0f}mm + 바디:{L_BODY:.0f}mm + 치형:{L_TOOTH:.0f}mm = 전체:{L_TOTAL:.0f}mm'),
    (2.5, f'치형깊이: {TD:.4f}mm  |  피삭재: AL6061 t6.0  |  소재두께 ≤ {L_TOOTH:.0f}mm 확인'),
    (2.5, '공구경도: 62~65 HRC  |  코팅: DLC / AlCrN  |  권장RPM: 400~600'),
    (2.2, 'DAWONRISE  |  DWG-T30-002  |  Rev.B  |  2026-04-23'),
]
for k, (h, s) in enumerate(tb_lines):
    msp.add_text(s, dxfattribs={'layer': 'TEXT', 'height': h,
                  'insert': (TBX + 2, TBY + (len(tb_lines) - 1 - k) * 5.5)})

NX, NY = BX1 + 2, BY1 + 5
msp.add_lwpolyline([(NX, NY), (TBX - 2, NY), (TBX - 2, NY + 22), (NX, NY + 22)],
                   close=True, dxfattribs={'layer': 'DIMENSION'})
msp.add_text('⚠ 설계 주의사항', dxfattribs={'layer': 'TEXT', 'height': 2.8,
              'insert': (NX + 2, NY + 17)})
notes = [
    '① 샹크/바디 Ø25 → 치형부 Ø52.6543 단차(숄더)부 응력집중 주의 → 코너 R 0.5mm 이상 부여',
    '② 치형부 8mm: 피삭재 두께 6mm 이내 → 완전 치형 형성 가능 (여유 2mm 확보)',
    '③ AL6061 BUE 방지 → DLC/AlCrN 코팅 필수 / 알루미늄 전용 에멀젼 절삭유',
    '④ 틸트각 1°±0.1° / 홀더 볼시트 정밀도 확인 / 가공 후 CMM 전수 검사',
]
for k, n in enumerate(notes):
    msp.add_text(n, dxfattribs={'layer': 'TEXT', 'height': 2.0,
                  'insert': (NX + 2, NY + 12 - k * 4)})

doc.saveas('T30_rotary_broach_punch.dxf')
print('DXF 생성 완료: T30_rotary_broach_punch.dxf')
