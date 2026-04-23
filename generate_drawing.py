#!/usr/bin/env python3
"""T30 로타리 브로치 펀치 기술 도면 SVG 생성기"""
import math

# ── 설계 파라미터 ──────────────────────────────────────────
R_OUT_MM   = 26.3272   # 외경 반지름 (Ø52.6543 / 2)
R_IN_MM    = 24.9577   # 내경 반지름 (Ø49.9154 / 2)
N_TEETH    = 30
TOOTH_ANG  = 120       # 치형 각도 (°)
TOTAL_L    = 44.0      # 전체 길이 (mm)
SHANK_L    = 20.0      # 샹크 길이 (mm)
TOOTH_L    = 6.0       # 치형 절삭부 길이 (mm)
BODY_L     = TOTAL_L - SHANK_L - TOOTH_L  # 18.0mm

# ── SVG 레이아웃 파라미터 ──────────────────────────────────
SVG_W, SVG_H = 1100, 720
SC_FRONT = 4.6         # 정면도 스케일 (px/mm)
SC_SIDE  = 5.8         # 측면도 스케일 (px/mm)

CX1, CY1 = 215, 360   # 정면도 중심
R_OUT = R_OUT_MM * SC_FRONT
R_IN  = R_IN_MM  * SC_FRONT

SV_LEFT  = 470
SV_CY    = CY1
SV_LEN   = TOTAL_L  * SC_SIDE
SV_HW    = R_OUT_MM * SC_SIDE   # 반지름(외경) px
SV_RIGHT = SV_LEFT + SV_LEN

# ── 색상 ──────────────────────────────────────────────────
BG      = "#16213E"
WHITE   = "#E8E8E8"
YELLOW  = "#F0C040"
CYAN    = "#40C0E0"
GRAY    = "#606878"
RED     = "#E05050"
GREEN   = "#50C080"

# ── 헬퍼 함수 ─────────────────────────────────────────────
def pt(cx, cy, r, deg):
    rad = math.radians(deg)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)

def fmt(v): return f"{v:.2f}"

lines = []
def e(s): lines.append(s)

# ── SVG 헤더 ──────────────────────────────────────────────
e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}">')
e(f'<rect width="{SVG_W}" height="{SVG_H}" fill="{BG}"/>')
e('<defs>')
e(f'<marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{CYAN}"/></marker>')
e(f'<marker id="arrL" markerWidth="8" markerHeight="6" refX="0" refY="3" orient="auto"><polygon points="8 0,0 3,8 6" fill="{CYAN}"/></marker>')
e('</defs>')

# ══════════════════════════════════════════════════════════
# 제목
# ══════════════════════════════════════════════════════════
e(f'<text x="550" y="38" font-family="Arial" font-size="22" font-weight="bold" fill="{WHITE}" text-anchor="middle">T30 로타리 브로치 펀치 도면</text>')
e(f'<text x="550" y="60" font-family="Arial" font-size="13" fill="{CYAN}" text-anchor="middle">피삭재: AL6061 | 두께: 6mm | 잇수: 30 | 치형각: 120°</text>')
e(f'<line x1="30" y1="70" x2="{SVG_W-30}" y2="70" stroke="{GRAY}" stroke-width="0.8"/>')

# ══════════════════════════════════════════════════════════
# 정면도 (Front View)
# ══════════════════════════════════════════════════════════
e(f'<text x="{CX1}" y="90" font-family="Arial" font-size="14" fill="{WHITE}" text-anchor="middle" font-weight="bold">정면도 (절삭단)</text>')

# 기준원 (외경 / 내경 phantom)
e(f'<circle cx="{fmt(CX1)}" cy="{fmt(CY1)}" r="{fmt(R_OUT)}" fill="none" stroke="{GRAY}" stroke-width="0.7" stroke-dasharray="6,3"/>')
e(f'<circle cx="{fmt(CX1)}" cy="{fmt(CY1)}" r="{fmt(R_IN)}"  fill="none" stroke="{GRAY}" stroke-width="0.7" stroke-dasharray="4,3"/>')

# 치형 폴리곤 (30개 이빨)
tooth_pts = []
for i in range(N_TEETH):
    v_deg = 270 + (i - 0.5) * (360.0 / N_TEETH)
    vx, vy = pt(CX1, CY1, R_IN, v_deg)
    tooth_pts.append(f"{vx:.2f},{vy:.2f}")
    t_deg = 270 + i * (360.0 / N_TEETH)
    tx, ty = pt(CX1, CY1, R_OUT, t_deg)
    tooth_pts.append(f"{tx:.2f},{ty:.2f}")
e(f'<polygon points="{" ".join(tooth_pts)}" fill="none" stroke="{YELLOW}" stroke-width="1.6"/>')

# 중심선
e(f'<line x1="{CX1-160}" y1="{CY1}" x2="{CX1+160}" y2="{CY1}" stroke="{GRAY}" stroke-width="0.7" stroke-dasharray="10,4,2,4"/>')
e(f'<line x1="{CX1}" y1="{CY1-160}" x2="{CX1}" y2="{CY1+160}" stroke="{GRAY}" stroke-width="0.7" stroke-dasharray="10,4,2,4"/>')
e(f'<circle cx="{fmt(CX1)}" cy="{fmt(CY1)}" r="2.5" fill="{GRAY}"/>')

# 치형각 주석 (상단 치형 근처)
tx_top, ty_top = pt(CX1, CY1, R_OUT, 270)
e(f'<text x="{fmt(CX1+12)}" y="{fmt(ty_top+22)}" font-family="Arial" font-size="11" fill="{CYAN}">120°</text>')
# 치형각 호
v1x, v1y = pt(CX1, CY1, R_IN, 270 - 6)
v2x, v2y = pt(CX1, CY1, R_IN, 270 + 6)
e(f'<polyline points="{fmt(v1x)},{fmt(v1y)} {fmt(tx_top)},{fmt(ty_top)} {fmt(v2x)},{fmt(v2y)}" fill="none" stroke="{CYAN}" stroke-width="0.9"/>')

# 치수선: Ø52.6543
lx, ly = pt(CX1, CY1, R_OUT * 0.72, 225)
e(f'<line x1="{fmt(CX1)}" y1="{fmt(CY1)}" x2="{fmt(lx)}" y2="{fmt(ly)}" stroke="{CYAN}" stroke-width="0.8" stroke-dasharray="4,3"/>')
e(f'<text x="{fmt(lx-5)}" y="{fmt(ly-7)}" font-family="Arial" font-size="12" fill="{CYAN}" text-anchor="end">Ø52.6543</text>')

# 치수선: Ø49.9154
lx2, ly2 = pt(CX1, CY1, R_IN * 0.60, 330)
e(f'<line x1="{fmt(CX1)}" y1="{fmt(CY1)}" x2="{fmt(lx2)}" y2="{fmt(ly2)}" stroke="{GREEN}" stroke-width="0.8" stroke-dasharray="4,3"/>')
e(f'<text x="{fmt(lx2+4)}" y="{fmt(ly2-5)}" font-family="Arial" font-size="12" fill="{GREEN}">Ø49.9154</text>')

# 치형 깊이 주석
dep_mm = R_OUT_MM - R_IN_MM
e(f'<text x="{fmt(CX1-R_OUT-15)}" y="{fmt(CY1+20)}" font-family="Arial" font-size="11" fill="{YELLOW}" text-anchor="end">치형깊이</text>')
e(f'<text x="{fmt(CX1-R_OUT-15)}" y="{fmt(CY1+34)}" font-family="Arial" font-size="11" fill="{YELLOW}" text-anchor="end">{dep_mm:.3f}mm</text>')
e(f'<line x1="{fmt(CX1-R_IN)}" y1="{fmt(CY1+18)}" x2="{fmt(CX1-R_OUT-12)}" y2="{fmt(CY1+22)}" stroke="{YELLOW}" stroke-width="0.7" stroke-dasharray="3,2"/>')

# 정면도 레이블
e(f'<text x="{CX1}" y="{CY1+R_OUT+28}" font-family="Arial" font-size="12" fill="{GRAY}" text-anchor="middle">뷰 A</text>')

# ══════════════════════════════════════════════════════════
# 측면도 (Side View)
# ══════════════════════════════════════════════════════════
e(f'<text x="{fmt(SV_LEFT + SV_LEN/2)}" y="90" font-family="Arial" font-size="14" fill="{WHITE}" text-anchor="middle" font-weight="bold">측면도 (단면)</text>')

sv_top  = SV_CY - SV_HW
sv_bot  = SV_CY + SV_HW
shank_x = SV_LEFT + SHANK_L * SC_SIDE
body_x  = shank_x + BODY_L  * SC_SIDE   # = SV_RIGHT - TOOTH_L*SC_SIDE

# 외곽 윤곽선
e(f'<rect x="{fmt(SV_LEFT)}" y="{fmt(sv_top)}" width="{fmt(SV_LEN)}" height="{fmt(SV_HW*2)}" fill="none" stroke="{WHITE}" stroke-width="1.5"/>')

# 구간 구분선 (가상선)
for bx, label in [(shank_x, "샹크/바디"), (body_x, "바디/치형")]:
    e(f'<line x1="{fmt(bx)}" y1="{fmt(sv_top-10)}" x2="{fmt(bx)}" y2="{fmt(sv_bot+10)}" stroke="{GRAY}" stroke-width="0.8" stroke-dasharray="5,3"/>')

# 치형부 해칭 (빗금) - 오른쪽 6mm 구간
tooth_region_x = body_x
for hx in range(int(tooth_region_x), int(SV_RIGHT), 4):
    e(f'<line x1="{hx}" y1="{fmt(sv_top)}" x2="{hx+8}" y2="{fmt(sv_top+8)}" stroke="{GRAY}" stroke-width="0.5" opacity="0.5"/>')
    e(f'<line x1="{hx}" y1="{fmt(sv_bot-8)}" x2="{hx+8}" y2="{fmt(sv_bot)}" stroke="{GRAY}" stroke-width="0.5" opacity="0.5"/>')

# 치형 요철 (측면에서 본 모양 - 상/하단)
tooth_depth_px = dep_mm * SC_SIDE
n_sv_teeth = 8
sv_pitch = (SV_RIGHT - body_x) / n_sv_teeth

for j in range(n_sv_teeth * 2 + 1):
    fx = body_x + j * (sv_pitch / 2)
    if fx > SV_RIGHT + 0.5: fx = SV_RIGHT
    if j % 2 == 0:
        fy_top, fy_bot = sv_top, sv_bot
    else:
        fy_top, fy_bot = sv_top - tooth_depth_px, sv_bot + tooth_depth_px
    if j == 0:
        prev_top, prev_bot = fy_top, fy_bot
        continue
    e(f'<line x1="{fmt(fx - sv_pitch/2)}" y1="{fmt(prev_top)}" x2="{fmt(fx)}" y2="{fmt(fy_top)}" stroke="{YELLOW}" stroke-width="1.4"/>')
    e(f'<line x1="{fmt(fx - sv_pitch/2)}" y1="{fmt(prev_bot)}" x2="{fmt(fx)}" y2="{fmt(fy_bot)}" stroke="{YELLOW}" stroke-width="1.4"/>')
    prev_top, prev_bot = fy_top, fy_bot

# 중심선 (측면도)
e(f'<line x1="{fmt(SV_LEFT-20)}" y1="{fmt(SV_CY)}" x2="{fmt(SV_RIGHT+20)}" y2="{fmt(SV_CY)}" stroke="{GRAY}" stroke-width="0.7" stroke-dasharray="10,4,2,4"/>')

# ══════════════════════════════════════════════════════════
# 치수선 (측면도)
# ══════════════════════════════════════════════════════════
dim_y1 = sv_top - 35   # 상단 치수선 y

def dim_line(x1, x2, y, text, color=CYAN, offset=0):
    """수평 치수선"""
    yt = y - 6 + offset
    e(f'<line x1="{fmt(x1)}" y1="{fmt(y)}" x2="{fmt(x1)}" y2="{fmt(y+18)}" stroke="{color}" stroke-width="0.8"/>')
    e(f'<line x1="{fmt(x2)}" y1="{fmt(y)}" x2="{fmt(x2)}" y2="{fmt(y+18)}" stroke="{color}" stroke-width="0.8"/>')
    e(f'<line x1="{fmt(x1)}" y1="{fmt(y+8)}" x2="{fmt(x2)}" y2="{fmt(y+8)}" stroke="{color}" stroke-width="1" marker-start="url(#arrL)" marker-end="url(#arr)"/>')
    mx = (x1 + x2) / 2
    e(f'<text x="{fmt(mx)}" y="{fmt(yt)}" font-family="Arial" font-size="12" fill="{color}" text-anchor="middle">{text}</text>')

def dim_line_v(x, y1, y2, text, color=CYAN):
    """수직 치수선"""
    xd = x + 8
    e(f'<line x1="{fmt(x)}" y1="{fmt(y1)}" x2="{fmt(x+16)}" y2="{fmt(y1)}" stroke="{color}" stroke-width="0.8"/>')
    e(f'<line x1="{fmt(x)}" y1="{fmt(y2)}" x2="{fmt(x+16)}" y2="{fmt(y2)}" stroke="{color}" stroke-width="0.8"/>')
    e(f'<line x1="{fmt(xd)}" y1="{fmt(y1)}" x2="{fmt(xd)}" y2="{fmt(y2)}" stroke="{color}" stroke-width="1" marker-start="url(#arrL)" marker-end="url(#arr)"/>')
    my = (y1 + y2) / 2
    e(f'<text x="{fmt(xd+10)}" y="{fmt(my+4)}" font-family="Arial" font-size="12" fill="{color}">Ø{R_OUT_MM*2:.4f}</text>')

# 전체 길이 44mm
dim_line(SV_LEFT, SV_RIGHT, dim_y1, "44.00", CYAN)
# 샹크 길이 20mm
dim_line(SV_LEFT, shank_x, dim_y1 - 22, "20.00", GREEN)
# 치형부 길이 6mm
dim_line(body_x, SV_RIGHT, dim_y1 - 22, "6.00", YELLOW)
# 바디 길이 18mm (참고)
dim_line(shank_x, body_x, dim_y1 - 22, "18.00", GRAY)

# 직경 치수 (우측)
dim_line_v(SV_RIGHT + 15, sv_top, sv_bot, f"Ø{R_OUT_MM*2:.4f}", WHITE)

# 깊이 치수 (치형부 상단)
td_x = body_x + (SV_RIGHT - body_x) * 0.5
e(f'<line x1="{fmt(td_x)}" y1="{fmt(sv_top - tooth_depth_px)}" x2="{fmt(td_x)}" y2="{fmt(sv_top)}" stroke="{YELLOW}" stroke-width="0.8" stroke-dasharray="3,2"/>')
e(f'<text x="{fmt(td_x+5)}" y="{fmt(sv_top - tooth_depth_px - 5)}" font-family="Arial" font-size="10" fill="{YELLOW}">치형깊이 {dep_mm:.3f}</text>')

# 측면도 레이블
e(f'<text x="{fmt(SV_LEFT + SV_LEN/2)}" y="{fmt(sv_bot+30)}" font-family="Arial" font-size="12" fill="{GRAY}" text-anchor="middle">뷰 B (측면)</text>')

# 구간 레이블
lbl_y = sv_bot + 50
for bx, bw, lbl, col in [
    (SV_LEFT,   SHANK_L*SC_SIDE,  f"샹크\n{SHANK_L:.0f}mm", GREEN),
    (shank_x,   BODY_L*SC_SIDE,   f"바디\n{BODY_L:.0f}mm",  GRAY),
    (body_x,    TOOTH_L*SC_SIDE,  f"치형부\n{TOOTH_L:.0f}mm", YELLOW),
]:
    mx = bx + bw/2
    for k, part in enumerate(lbl.split('\n')):
        e(f'<text x="{fmt(mx)}" y="{fmt(lbl_y + k*16)}" font-family="Arial" font-size="11" fill="{col}" text-anchor="middle">{part}</text>')

# ══════════════════════════════════════════════════════════
# 치형 상세 확대도
# ══════════════════════════════════════════════════════════
DX, DY = 820, 130
DR = 60   # 표시 반지름 (px)

e(f'<text x="{DX+45}" y="{DY-10}" font-family="Arial" font-size="13" fill="{WHITE}" text-anchor="middle" font-weight="bold">치형 상세 (확대)</text>')

# 인접 3개 이빨 표시 (상단 0번 기준 ±1)
zoom_pts = []
for i in range(-2, 4):
    v_deg = 270 + (i - 0.5) * (360.0 / N_TEETH)
    vx, vy = pt(DX+45, DY+80, DR * (R_IN/R_OUT), v_deg)
    zoom_pts.append(f"{vx:.2f},{vy:.2f}")
    t_deg = 270 + i * (360.0 / N_TEETH)
    tx, ty = pt(DX+45, DY+80, DR, t_deg)
    zoom_pts.append(f"{tx:.2f},{ty:.2f}")

e(f'<polygon points="{" ".join(zoom_pts)}" fill="none" stroke="{YELLOW}" stroke-width="1.8"/>')
e(f'<circle cx="{DX+45}" cy="{DY+80}" r="{DR}" fill="none" stroke="{GRAY}" stroke-width="0.6" stroke-dasharray="4,2"/>')
e(f'<circle cx="{DX+45}" cy="{DY+80}" r="{DR*(R_IN/R_OUT):.2f}" fill="none" stroke="{GRAY}" stroke-width="0.6" stroke-dasharray="3,2"/>')

# 치형각 표시
tip_x, tip_y = pt(DX+45, DY+80, DR, 270)
va_x, va_y = pt(DX+45, DY+80, DR*(R_IN/R_OUT), 270-6)
vb_x, vb_y = pt(DX+45, DY+80, DR*(R_IN/R_OUT), 270+6)
e(f'<polyline points="{fmt(va_x)},{fmt(va_y)} {fmt(tip_x)},{fmt(tip_y)} {fmt(vb_x)},{fmt(vb_y)}" fill="none" stroke="{CYAN}" stroke-width="1"/>')
e(f'<text x="{fmt(tip_x+8)}" y="{fmt(tip_y+6)}" font-family="Arial" font-size="11" fill="{CYAN}">120°</text>')

# 외경/내경 화살표
e(f'<line x1="{DX+45}" y1="{DY+80}" x2="{fmt(tip_x)}" y2="{fmt(tip_y)}" stroke="{CYAN}" stroke-width="0.7" stroke-dasharray="3,2"/>')
e(f'<text x="{DX+45}" y="{DY+172}" font-family="Arial" font-size="10" fill="{CYAN}" text-anchor="middle">Ø52.6543 (외경)</text>')
e(f'<text x="{DX+45}" y="{DY+186}" font-family="Arial" font-size="10" fill="{GREEN}" text-anchor="middle">Ø49.9154 (내경)</text>')

# ══════════════════════════════════════════════════════════
# 재료 / 가공 사양 표 (우하단)
# ══════════════════════════════════════════════════════════
TX, TY = 820, 360
e(f'<rect x="{TX}" y="{TY}" width="245" height="290" fill="#0D1626" stroke="{GRAY}" stroke-width="1" rx="4"/>')
e(f'<rect x="{TX}" y="{TY}" width="245" height="28" fill="{GRAY}" rx="4"/>')
e(f'<text x="{TX+122}" y="{TY+19}" font-family="Arial" font-size="13" font-weight="bold" fill="{WHITE}" text-anchor="middle">제작 사양</text>')

specs = [
    ("구분",        "내용",               WHITE,  CYAN),
    ("품명",        "T30 브로치 펀치",    CYAN,   WHITE),
    ("잇수",        "30개",               CYAN,   WHITE),
    ("치형각",      "120°",               CYAN,   WHITE),
    ("외경",        "Ø52.6543",           CYAN,   WHITE),
    ("내경(치저)",  "Ø49.9154",           CYAN,   WHITE),
    ("치형 깊이",   f"{dep_mm:.3f} mm",   CYAN,   YELLOW),
    ("전체 길이",   "44.00 mm",           CYAN,   WHITE),
    ("샹크 길이",   "20.00 mm",           CYAN,   WHITE),
    ("치형부 길이", "6.00 mm",            CYAN,   YELLOW),
    ("피삭재",      "AL6061 t6.0",        GREEN,  WHITE),
    ("권장 경도",   "62~65 HRC",          CYAN,   WHITE),
    ("권장 코팅",   "DLC / AlCrN",        CYAN,   WHITE),
    ("권장 RPM",    "400~600",            CYAN,   WHITE),
]

row_h = 18
for idx, (k, v, kc, vc) in enumerate(specs):
    ry = TY + 30 + idx * row_h
    bg = "#1A2540" if idx % 2 == 0 else "#0D1626"
    e(f'<rect x="{TX+1}" y="{ry}" width="243" height="{row_h}" fill="{bg}"/>')
    e(f'<text x="{TX+8}" y="{ry+13}" font-family="Arial" font-size="11" fill="{kc}">{k}</text>')
    e(f'<text x="{TX+237}" y="{ry+13}" font-family="Arial" font-size="11" fill="{vc}" text-anchor="end">{v}</text>')

# ══════════════════════════════════════════════════════════
# 주의사항 박스
# ══════════════════════════════════════════════════════════
NX, NY = 30, 620
e(f'<rect x="{NX}" y="{NY}" width="{SVG_W-60}" height="82" fill="#1A0D0D" stroke="{RED}" stroke-width="1" rx="4"/>')
e(f'<text x="{NX+10}" y="{NY+18}" font-family="Arial" font-size="12" font-weight="bold" fill="{RED}">⚠ 설계 주의사항</text>')
notes = [
    "① 치형부 6mm = 피삭재 두께 6mm 동일 → 선단 챔퍼 최소화 (0.5mm×15° 이하) 또는 절삭부 7~8mm로 연장 검토",
    "② AL6061 가공 시 Built-Up Edge 방지 → DLC 또는 AlCrN 코팅 필수 / 알루미늄 전용 에멀젼 절삭유 사용",
    "③ 틸트각 1°±0.1° 유지 / 홀더 볼시트 정밀도 확인 / 가공 완료 후 전체 치형 프로파일 CMM 검사 실시",
]
for i, n in enumerate(notes):
    e(f'<text x="{NX+10}" y="{NY+34+i*16}" font-family="Arial" font-size="10.5" fill="{WHITE}">{n}</text>')

# ── 도면 테두리 및 도번 ────────────────────────────────────
e(f'<rect x="10" y="10" width="{SVG_W-20}" height="{SVG_H-20}" fill="none" stroke="{GRAY}" stroke-width="1.2"/>')
e(f'<text x="{SVG_W-20}" y="{SVG_H-15}" font-family="Arial" font-size="10" fill="{GRAY}" text-anchor="end">DWG-T30-001 | Rev.A | 2026-04-23 | DAWONRISE</text>')

e('</svg>')

# 출력
svg_content = "\n".join(lines)
with open("T30_rotary_broach_punch.svg", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(svg_content)

print("도면 생성 완료: T30_rotary_broach_punch.svg")
