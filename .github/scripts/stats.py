"""Génère stats/overview.svg et stats/languages.svg à partir de l'API GitHub."""
import json
import os
import sys
import urllib.request
from html import escape

USER = sys.argv[1]
OUT = "stats"
TOKEN = os.environ.get("GITHUB_TOKEN")
EXCLUDE = {"Roff", "Makefile"}  # langages à ne pas compter

BG, BORDER, TITLE, TEXT, MUTED = "#1a1b27", "#2a2e45", "#A78BFA", "#c0caf5", "#7a82a6"
LANG_COLORS = {
    "C#": "#3fb950", "Lua": "#6b7cff", "C": "#a8b1c2", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#8b5cf6", "Python": "#3572A5",
    "Rust": "#dea584", "ShaderLab": "#9aa5ce", "HLSL": "#aace60", "Shell": "#89e051",
}


def api(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def card(width, height, title, inner):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  .t {{ font: 600 17px 'Segoe UI', Ubuntu, sans-serif; fill: {TITLE}; }}
  .l {{ font: 400 13px 'Segoe UI', Ubuntu, sans-serif; fill: {MUTED}; }}
  .v {{ font: 700 13px 'Segoe UI', Ubuntu, sans-serif; fill: {TEXT}; }}
  .row {{ animation: in .5s ease-out backwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateX(-8px); }} to {{ opacity: 1; transform: none; }} }}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<text x="25" y="35" class="t">{escape(title)}</text>
{inner}
</svg>"""


repos = [r for r in api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]

# Langages : somme des octets de code par langage sur tous les repos
langs = {}
for r in repos:
    for name, size in api(r["languages_url"]).items():
        if name not in EXCLUDE:
            langs[name] = langs.get(name, 0) + size
top = sorted(langs.items(), key=lambda x: -x[1])[:8]
total = sum(v for _, v in top) or 1

bar, x = [], 25
for name, size in top:
    w = size / total * 370
    bar.append(f'<rect x="{x:.1f}" y="52" width="{w:.1f}" height="8" fill="{LANG_COLORS.get(name, MUTED)}"/>')
    x += w
rows = []
for i, (name, size) in enumerate(top):
    cx, cy = 25 + (i % 2) * 190, 88 + (i // 2) * 26
    rows.append(
        f'<g class="row" style="animation-delay:{i * 120}ms">'
        f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{LANG_COLORS.get(name, MUTED)}"/>'
        f'<text x="{cx + 16}" y="{cy}" class="v">{escape(name)}</text>'
        f'<text x="{cx + 170}" y="{cy}" class="l" text-anchor="end">{size / total * 100:.1f}%</text></g>'
    )
lang_svg = card(420, 88 + ((len(top) + 1) // 2) * 26, "Langages les plus utilisés",
                f'<clipPath id="c"><rect x="25" y="52" width="370" height="8" rx="4"/></clipPath>'
                f'<g clip-path="url(#c)">{"".join(bar)}</g>' + "".join(rows))

# Vue d'ensemble
stats = [("Repos publics", len(repos)), ("Étoiles reçues", sum(r["stargazers_count"] for r in repos))]
if TOKEN:
    q = """query($u:String!){ user(login:$u){
      contributionsCollection { totalCommitContributions contributionCalendar { totalContributions } }
      pullRequests { totalCount } followers { totalCount } } }"""
    u = api("https://api.github.com/graphql", {"query": q, "variables": {"u": USER}})["data"]["user"]
    stats = [
        ("Contributions (1 an)", u["contributionsCollection"]["contributionCalendar"]["totalContributions"]),
        ("Commits (1 an)", u["contributionsCollection"]["totalCommitContributions"]),
        ("Pull requests", u["pullRequests"]["totalCount"]),
        *stats,
        ("Followers", u["followers"]["totalCount"]),
    ]
rows = []
for i, (label, value) in enumerate(stats):
    y = 70 + i * 26
    rows.append(
        f'<g class="row" style="animation-delay:{i * 120}ms">'
        f'<text x="25" y="{y}" class="l">{escape(label)}</text>'
        f'<text x="395" y="{y}" class="v" text-anchor="end">{value}</text></g>'
    )
overview_svg = card(420, 52 + len(stats) * 26 + 8, f"Stats GitHub de {USER}", "".join(rows))

os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/languages.svg", "w").write(lang_svg)
open(f"{OUT}/overview.svg", "w").write(overview_svg)
print("ok:", ", ".join(n for n, _ in top))
