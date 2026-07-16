"""Render the published Figure 3 membership ledger."""

# ---------------------------------------------------------------------------
# themes: base colors match the fund-dividend figure (Figure 4); the four member
# hues start from Figure 4's blue and orange and extend with two flexoki
# hues (purple, teal). Holdout blocks are neutral grey; their flow ribbons
# carry the holdout's own hue.
# ---------------------------------------------------------------------------
THEMES = {
    "light": dict(bg="#fefefe", ttl="#1a1a1a", note="#777", sub="#555",
                  grid="#c9c9c9", spine="#b0b0b0",
                  out_bg="#f1f1ef", out_border="#dcdcda", out_txt="#7a7a7a",
                  out_sub="#8a8a88",
                  US="#4385BE", EU="#DA702C", UK="#8B7EC8", JKT="#3AA99F",
                  CN="#C6912E", RoW="#7C8A34"),
    "dark":  dict(bg="#1C1C1D", ttl="#e6e6e3", note="#9c9c99", sub="#b4b4b2",
                  grid="#3a3a3c", spine="#525254",
                  out_bg="#262627", out_border="#3a3a3c", out_txt="#a6a6a3",
                  out_sub="#8f8f8c",
                  US="#6aa6dd", EU="#e08a4c", UK="#a897de", JKT="#5abfb5",
                  CN="#d8b45a", RoW="#a9b866"),
}
F_TITLE, F_SUB, F_HDR = 30, 19, 21
F_NAME, F_MONEY, F_ANCH = 23, 25, 18
F_BODY, F_SMALL, F_TAG = 18, 16, 20
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

W, H = 1400, 1000
DEF_MEMBERS = ["US", "EU", "UK", "JKT"]
DEF_HOLDOUTS = ["CN", "RoW"]

MARGIN = 56
COL_W = 512
DIV_X = W / 2
BAND_TOP = 168
BAND_BOT = H - 92
GUT_L = MARGIN + COL_W                 # right edge of left column = 568
GUT_R = W - MARGIN - COL_W             # left edge of right column = 832
MEM_CAP, HOLD_CAP = 214, 240


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def money(b):
    if b >= 1000:
        return f"${b/1000:.1f}T"
    return f"${b:.0f}B"


class SVG:
    def __init__(self, theme):
        self.c = THEMES[theme]
        self.b = []

    def text(self, x, y, s, size, fill, anchor="start", weight=400,
             italic=False, opacity=1.0, spacing=None):
        st = "font-style:italic;" if italic else ""
        if spacing:
            st += f"letter-spacing:{spacing};"
        self.b.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" opacity="{opacity:.3f}" style="{st}">{esc(s)}</text>')

    def rrect(self, x, y, w, h, r, fill, stroke="none", sw=0, opacity=1.0):
        self.b.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r}" ry="{r}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" opacity="{opacity:.3f}"/>')

    def line(self, x1, y1, x2, y2, stroke, sw=1.5, dash=None, opacity=1.0, cap="butt"):
        d = f'stroke-dasharray="{dash}" ' if dash else ""
        self.b.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}" '
            f'{d}opacity="{opacity:.3f}"/>')

    def path(self, d, fill="none", stroke="none", sw=0, opacity=1.0):
        self.b.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
                      f'stroke-width="{sw}" opacity="{opacity:.3f}"/>')

    def doc(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">\n'
                '<title>How much each economy would collect under the club</title>\n'
                '<desc>Annual collections under a one-percent levy on large firms, '
                'showing four member economies and two holdouts.</desc>\n'
                f'<rect x="0" y="0" width="{W}" height="{H}" fill="{self.c["bg"]}"/>\n'
                + "\n".join(self.b) + "\n</svg>\n")


def layout(members, holdouts):
    """Block rectangles for each column. A column with enough blocks to fill
    the band packs contiguously from the top. A column with fewer, capped-
    height blocks distributes space-between so both columns still align top
    and bottom (their middle carries the flow). One block is centered."""
    band = BAND_BOT - BAND_TOP
    out = {}
    for side, ids, x, gap, cap in (("mem", members, GUT_R, 20, MEM_CAP),
                                   ("out", holdouts, MARGIN, 34, HOLD_CAP)):
        n = len(ids)
        out[side] = []
        if n == 0:
            continue
        even = (band - gap * (n - 1)) / n if n > 1 else band
        h = min(even, cap)
        if n == 1:
            ys = [BAND_TOP + (band - h) / 2]
        elif h >= even - 0.5:                 # fills the band
            ys = [BAND_TOP + k * (h + gap) for k in range(n)]
        else:                                  # capped, space-between
            ys = [BAND_TOP + k * (band - h) / (n - 1) for k in range(n)]
        for k, yv in zip(ids, ys):
            out[side].append((k, x, yv, COL_W, h))
    return out


def draw_member(s, c, bid, x, y, w, h, buckets, blong, rev, C, members,
                holdouts, anchors, maxrev):
    name = buckets[bid]
    col = c[name]
    j = bid
    s.rrect(x, y, w, h, 14, col, opacity=0.13)
    s.rrect(x, y, 10, h, 5, col)
    pad = 30
    tx = x + pad
    s.text(tx, y + 44, blong[name], F_NAME, c["ttl"], "start", 600)
    s.text(tx, y + 80, f"collects {money(rev[j])} a year", F_MONEY, col, "start", 700)
    an = anchors.get(name)
    if an and h >= 118:
        aname, aval = an
        pct = 100.0 * rev[j] / aval if aval else float("nan")
        atxt = (f"about {pct/100:.1f}x {aname}" if pct >= 150
                else f"about {pct:.0f}% of {aname}")
        s.text(tx, y + 108, atxt, F_ANCH, c["note"], "start", 400, italic=True)
    # provenance bar: total length encodes magnitude, segments encode source
    if h >= 150:
        own = C[j, j]
        mem_oth = sum(C[i, j] for i in members if i != j)
        hold = sum(C[i, j] for i in holdouts)
        segs = [("its own firms", own, 0.92),
                ("other members", mem_oth, 0.58),
                ("out-of-club", hold, 0.30)]
        segs = [sg for sg in segs if sg[1] > 0.5]
        bx = tx
        binner = w - 2 * pad
        barW = max(binner * (rev[j] / maxrev) if maxrev else 0, 64)
        by = y + h - 52
        bh = 13
        xx = bx
        seggap, nseg = 2.5, len(segs)
        for (lab, v, shade) in segs:
            sw2 = (barW - seggap * (nseg - 1)) * (v / rev[j])
            s.rrect(xx, by, max(sw2, 2), bh, 3.5, col, opacity=shade)
            xx += sw2 + seggap
        parts = "   ·   ".join(f"{lab} {money(v)}" for lab, v, _ in segs)
        s.text(bx, by + 33, parts, F_SMALL + 1, c["sub"], "start", 400)


def draw_holdout(s, c, bid, x, y, w, h, buckets, blong, led, jd):
    name = buckets[bid]
    col = c[name]
    s.rrect(x, y, w, h, 14, c["out_bg"], stroke=c["out_border"], sw=1.5)
    pad = 30
    tx = x + pad
    paid = led["collected"][bid] * 1000.0
    uncol = led["uncollected"][bid] * 1000.0
    gain = jd["joiner_gets"] * 1000.0
    pw = w - 2 * pad
    if h >= 200:
        s.text(tx, y + 46, blong[name], F_NAME, c["out_txt"], "start", 600)
        s.text(tx, y + 80, "collects $0 while holding out", F_MONEY - 3,
               c["out_sub"], "start", 600)
        s.line(tx, y + 102, x + w - pad, y + 102, c["out_border"], 1.2, opacity=0.9)
        s.text(tx, y + 136, f"their firms still pay {money(paid)} a year into the club",
               F_BODY, c["out_txt"], "start", 400, italic=True)
        if uncol > 1 and h >= 238:
            s.text(tx, y + 164,
                   f"the cap leaves {money(uncol)} a year uncollected until they join",
                   F_SMALL, c["out_sub"], "start", 400, italic=True)
        pill_h = 46
        py = y + h - pad - pill_h + 10
        s.rrect(tx, py, pw, pill_h, pill_h / 2, col, opacity=0.14)
        s.rrect(tx, py, pw, pill_h, pill_h / 2, "none", stroke=col, sw=1.6)
        s.text(tx + pw / 2, py + pill_h / 2 + 7,
               f"Join the club, collect {money(gain)} a year", F_TAG, col, "middle", 700)
    else:
        pill_h = 38 if h >= 150 else 28
        py = y + h - 14 - pill_h
        s.rrect(tx, py, pw, pill_h, pill_h / 2, col, opacity=0.14)
        s.rrect(tx, py, pw, pill_h, pill_h / 2, "none", stroke=col, sw=1.6)
        s.text(tx + pw / 2, py + pill_h / 2 + (6 if pill_h >= 36 else 5),
               f"Join the club, collect {money(gain)} a year",
               18 if pill_h >= 36 else 15, col, "middle", 700)
        s.text(tx, y + 34, blong[name], 20, c["out_txt"], "start", 600)
        ly = y + 62
        lines = [f"collects $0, their firms pay {money(paid)} a year"]
        if uncol > 1:
            lines.append(f"the cap leaves {money(uncol)} uncollected until they join")
        for ln in lines:
            if ly + 4 <= py:
                s.text(tx, ly, ln, F_SMALL - 1, c["out_sub"], "start", 400, italic=True)
                ly += 25
    return (x + w, y + h / 2, paid, col)


def draw_flow(s, c, flows, members_layout):
    if not flows or not members_layout:
        return
    band_mid = (members_layout[0][2] +
                members_layout[-1][2] + members_layout[-1][4]) / 2
    maxflow = max(f[2] for f in flows) or 1
    wmin, wmax = 9, 52

    def rw(v):
        return wmin + (wmax - wmin) * (v / maxflow)

    total_w = sum(rw(f[2]) for f in flows)
    fx = GUT_L + 120
    intake_x = GUT_R - 14
    face_top = band_mid - total_w / 2
    for (hx, hy, paid, col) in sorted(flows, key=lambda f: f[1]):
        w0 = rw(paid)
        ft, fb = face_top, face_top + w0
        face_top += w0
        x0 = hx + 2
        c1 = x0 + (fx - x0) * 0.55
        d = (f'M {x0:.1f} {hy - w0/2:.1f} '
             f'C {c1:.1f} {hy - w0/2:.1f}, {c1:.1f} {ft:.1f}, {fx:.1f} {ft:.1f} '
             f'L {fx:.1f} {fb:.1f} '
             f'C {c1:.1f} {fb:.1f}, {c1:.1f} {hy + w0/2:.1f}, {x0:.1f} {hy + w0/2:.1f} Z')
        s.path(d, fill=col, opacity=0.42)
    tt = band_mid - total_w / 2
    tb = band_mid + total_w / 2
    ah, tip = 20, intake_x + 30
    d = (f'M {fx:.1f} {tt:.1f} L {intake_x:.1f} {tt:.1f} '
         f'L {intake_x:.1f} {tt - ah:.1f} L {tip:.1f} {(tt+tb)/2:.1f} '
         f'L {intake_x:.1f} {tb + ah:.1f} L {intake_x:.1f} {tb:.1f} '
         f'L {fx:.1f} {tb:.1f} Z')
    s.path(d, fill=c["spine"], opacity=0.30)
    sp_x = GUT_R - 3
    sp_top = members_layout[0][2]
    sp_bot = members_layout[-1][2] + members_layout[-1][4]
    s.line(sp_x, sp_top, sp_x, sp_bot, c["spine"], 3, opacity=0.6, cap="round")
    total = sum(f[2] for f in flows)
    lx = (fx + intake_x) / 2
    s.text(lx, tt - 46, f"{money(total)} a year", F_BODY, c["sub"], "middle", 700)
    s.text(lx, tt - 25, "from out-of-club firms", F_SMALL, c["note"], "middle", 400, italic=True)
    s.text(lx, tb + ah + 28, "members divide it", F_SMALL, c["note"], "middle", 400, italic=True)


def render_theme(model, theme, V, S, buckets, blong, tau, cap, anchors,
                 members=None, holdouts=None):
    c = THEMES[theme]
    s = SVG(theme)
    idx = {n: buckets.index(n) for n in buckets}
    if members is None:
        members = DEF_MEMBERS
        holdouts = DEF_HOLDOUTS if holdouts is None else holdouts
    elif holdouts is None:
        holdouts = [b for b in buckets if b not in members]
    mi = [idx[n] for n in members]
    hi = [idx[n] for n in holdouts]
    rev = model.member_revenue(V, S, mi, tau, cap) * 1000.0
    mi.sort(key=lambda j: -rev[j])            # ledger reads high to low
    led = model.bucket_ledger(V, S, mi, tau, cap)
    C = model.collection_matrix(V, S, mi, tau, cap) * 1000.0
    maxrev = max((rev[i] for i in mi), default=1.0) or 1.0

    s.text(W/2, 52, "How much each economy would collect under the club",
           F_TITLE, c["ttl"], "middle", 600)
    s.text(W/2, 84,
           "An annual 1% levy on large firms, apportioned by where each firm "
           "sells. Every member collects from covered firms worldwide.",
           F_SUB, c["note"], "middle", 400, italic=True)

    s.text(MARGIN + COL_W/2, 138, "HOLDING OUT", F_HDR, c["out_txt"],
           "middle", 700, spacing="0.06em")
    s.text(W - MARGIN - COL_W/2, 138, "CLUB MEMBERS", F_HDR, c["ttl"],
           "middle", 700, spacing="0.06em")
    s.line(DIV_X, 156, DIV_X, BAND_BOT, c["grid"], 1.5, dash="9 8", opacity=0.7)

    lay = layout(mi, hi)
    flows = []
    for (bid, x, y, w, h) in lay["out"]:
        jd = model.join_delta(V, S, mi, tau, cap, bid)
        flows.append(draw_holdout(s, c, bid, x, y, w, h, buckets, blong, led, jd))
    draw_flow(s, c, [f for f in flows if f[2] > 0.5], lay["mem"])
    for (bid, x, y, w, h) in lay["mem"]:
        draw_member(s, c, bid, x, y, w, h, buckets, blong, rev, C, mi, hi,
                    anchors, maxrev)

    total = led["collected"].sum() * 1000.0
    s.text(MARGIN, H - 40,
           f"Together the club would collect {money(total)} a year.",
           F_BODY, c["sub"], "start", 600)
    s.text(MARGIN, H - 16,
           "A holdout's firms are charged on their member-market sales plus a capped "
           "share of the rest, and members divide it until the holdout joins and claims its share.",
           F_SMALL, c["note"], "start", 400, italic=True)
    return s.doc()


def write_assets(model, V, S, buckets, blong, tau, cap, anchors, outdir):
    import cairosvg
    import os
    os.makedirs(f"{outdir}/final", exist_ok=True)
    for theme in ("light", "dark"):
        svg = render_theme(
            model, theme, V, S, buckets, blong, tau, cap, anchors)
        base = f"{outdir}/final/club-ledger-{theme}"
        with open(base + ".svg", "w") as f:
            f.write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=base + ".png",
                         output_width=W, output_height=H)
    print(f"wrote {outdir}/final/club-ledger-{{light,dark}}.{{svg,png}}")
