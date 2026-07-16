#!/usr/bin/env python3
"""Render separate Figure 4 assets for the two model alternatives."""

from __future__ import annotations

import html
from pathlib import Path

W, H = 1400, 900
X0, X1, Y0, Y1 = 150.0, W - 40.0, H - 100.0, 150.0
YMAX = 60_000.0

THEMES = {
    "light": dict(bg="#fefefe", title="#1a1a1a", text="#555", note="#777",
                  grid="#dadada", axis="#999", base="#7a7a7a",
                  act="#4385BE", agg="#DA702C", bench="#a93226"),
    "dark": dict(bg="#1C1C1D", title="#e6e6e3", text="#b4b4b2", note="#999",
                 grid="#3a3a3c", axis="#8a8a8a", base="#aaa",
                 act="#6aa6dd", agg="#e08a4c", bench="#e8978a"),
}

MODEL_META = {
    "simple": dict(
        filename="fund-dividend-simple",
        subtitle="U.S. analysis · Listed-market proxy held at its opening ratio to GDP",
        desc=("Simple labor-linked cash-yield Figure 4 alternative. U.S. public dividends in "
              "three AI scenarios, using an approximately $62.186 trillion "
              "listed-market proxy and a rising payout yield as labor share falls.")),
    "dcf": dict(
        filename="fund-dividend-dcf",
        subtitle="U.S. analysis · Payout-valued DCF with permanent-policy pricing",
        desc=("Payout-valued DCF used for Figure 4. U.S. public dividends in "
              "three AI scenarios, using an explicit ownership "
              "ledger and permanent dilution in the valuation kernel.")),
}


def x(year: float) -> float:
    return X0 + year / 50.0 * (X1 - X0)


def y(value: float) -> float:
    return Y0 + min(value, YMAX) / YMAX * (Y1 - Y0)


def model_results(source, model_name: str) -> list[tuple[dict, list[dict]]]:
    if model_name == "simple":
        return [(scenario, source.simulate_simple(scenario))
                for scenario in source.SCENARIOS]
    return [(scenario, source.simulate_dcf(scenario)["rows"])
            for scenario in source.SCENARIOS]


def svg_document(source, model_name: str, theme: str) -> str:
    colors, meta = THEMES[theme], MODEL_META[model_name]
    results = model_results(source, model_name)
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">',
        f'  <title>{html.escape("How fast can a labor-indexed tax fund a livable dividend?")}</title>',
        f'  <desc>{html.escape(meta["desc"])}</desc>',
        "  <metadata>",
        f'    <model-basis>{html.escape(meta["subtitle"])}</model-basis>',
        "  </metadata>",
        "  <style>",
        f"    .title {{ fill:{colors['title']};font:600 30px system-ui,sans-serif }}",
        f"    .subtitle {{ fill:{colors['note']};font:19px system-ui,sans-serif }}",
        f"    .axistext {{ fill:{colors['text']};font:20px system-ui,sans-serif }}",
        "    .label { font:600 21px system-ui,sans-serif }",
        f"    .note {{ fill:{colors['note']};font:italic 18px system-ui,sans-serif }}",
        f"    .grid {{ stroke:{colors['grid']};stroke-width:1.5 }}",
        f"    .axis {{ stroke:{colors['axis']};stroke-width:1.5 }}",
        f"    .benchmark {{ stroke:{colors['bench']};stroke-width:2.8;stroke-dasharray:10 7 }}",
        "    .curve { fill:none;stroke-width:4;stroke-linejoin:round;stroke-linecap:round }",
        "  </style>",
        f'  <rect width="{W}" height="{H}" fill="{colors["bg"]}"/>',
        f'  <text class="title" x="{W/2:.0f}" y="54" text-anchor="middle">How fast can a labor-indexed tax fund a livable dividend?</text>',
        f'  <text class="subtitle" x="{W/2:.0f}" y="88" text-anchor="middle">{html.escape(meta["subtitle"])}</text>',
    ]
    for value in range(0, 60_001, 10_000):
        yy = y(value)
        label = "$0" if value == 0 else f"${value // 1000}k"
        body.extend([
            f'  <line class="grid" x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}"/>',
            f'  <text class="axistext" x="{X0-14}" y="{yy+7:.1f}" text-anchor="end">{label}</text>',
        ])
    body.append(f'  <line class="axis" x1="{X0}" y1="{Y0}" x2="{X1}" y2="{Y0}"/>')
    for year in range(0, 51, 10):
        body.append(f'  <text class="axistext" x="{x(year):.1f}" y="{Y0+36}" text-anchor="middle">{year}</text>')
    body.extend([
        f'  <text class="axistext" x="{(X0+X1)/2:.1f}" y="{Y0+76}" text-anchor="middle">Years after the tax is enacted</text>',
        f'  <text class="axistext" x="46" y="{(Y0+Y1)/2:.1f}" text-anchor="middle" transform="rotate(-90 46 {(Y0+Y1)/2:.1f})">Dividend per person (real 2026 $)</text>',
        f'  <line class="benchmark" x1="{X0}" y1="{y(35000):.1f}" x2="{X1}" y2="{y(35000):.1f}"/>',
        f'  <text class="label" fill="{colors["bench"]}" x="{X0+16}" y="{y(35000)-12:.1f}">Livable income (~$35k)</text>',
    ])
    keys = (("baseline", "base"), ("moderate", "act"), ("strong", "agg"))
    for (scenario, rows), (_, color_key) in zip(results, keys):
        points = " ".join(f"{x(row['year']):.2f},{y(row['per_capita_payout']):.2f}"
                          for row in rows)
        color = colors[color_key]
        body.append(f'  <polyline class="curve" stroke="{color}" points="{points}"/>')
        last = rows[-1]
        label_lift = 40 if scenario["key"] == "strong" else 12
        body.append(f'  <text class="label" fill="{color}" x="{X1-8}" y="{y(last["per_capita_payout"])-label_lift:.1f}" text-anchor="end">{html.escape(scenario["label"])}&#8201;·&#8201;${last["per_capita_payout"]:,.0f}</text>')
    strong_rows = results[-1][1]
    for year in (25, 50):
        row = strong_rows[year - 1]
        body.append(f'  <circle cx="{x(year):.1f}" cy="{y(row["per_capita_payout"]):.1f}" r="6" fill="{colors["agg"]}"/>')
        if year == 25:
            note_x = x(year) - 14
            note_y = y(row["per_capita_payout"]) - 16
        else:
            # Treat terminal ownership as the second line of the endpoint
            # annotation, between the lifted scenario label and the path.
            note_x = X1 - 8
            note_y = y(row["per_capita_payout"]) - 12
        body.append(f'  <text class="note" x="{note_x:.1f}" y="{note_y:.1f}" text-anchor="end">fund owns {row["q_end"]:.0%}</text>')
    body.append("</svg>\n")
    return "\n".join(body)


def write_assets(source, output_dir: str | Path) -> list[Path]:
    import cairosvg

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    written = []
    for model_name, meta in MODEL_META.items():
        for theme in THEMES:
            svg = svg_document(source, model_name, theme)
            base = destination / f"{meta['filename']}-{theme}"
            svg_path, png_path = base.with_suffix(".svg"), base.with_suffix(".png")
            svg_path.write_text(svg)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png_path),
                             output_width=W, output_height=H)
            written.extend((svg_path, png_path))
    return written


if __name__ == "__main__":
    import figure4

    for path in write_assets(figure4, Path(__file__).with_name("final")):
        print(f"wrote {path}")
