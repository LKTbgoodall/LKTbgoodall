"""Génère stats/card.svg (activité, langages et série) à partir de l'API GitHub."""
import datetime as dt
import json
import os
import sys
import urllib.request
from html import escape

TOKEN = os.environ.get("GITHUB_TOKEN")
EXCLUDE = {"Roff", "Makefile"}  # langages à ne pas compter

W, H = 900, 300
TITLE, TEXT, MUTED, LINE = "#2DD4BF", "#E2E8F0", "#8B93B5", "#2a2e45"
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


def graphql(query, **variables):
    return api("https://api.github.com/graphql", {"query": query, "variables": variables})["data"]


def streaks(days):
    """days : liste (date, nombre) triée. Renvoie (série actuelle, record)."""
    longest = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    today = dt.date.today().isoformat()
    for date, n in reversed(days):
        if n:
            current += 1
        elif date != today:  # aujourd'hui sans contribution ne casse pas la série
            break
    return current, longest


def collect(user):
    repos = [r for r in api(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner") if not r["fork"]]
    langs = {}
    for r in repos:
        for name, size in api(r["languages_url"]).items():
            if name not in EXCLUDE:
                langs[name] = langs.get(name, 0) + size
    data = {
        "repos": len(repos),
        "stars": sum(r["stargazers_count"] for r in repos),
        "langs": sorted(langs.items(), key=lambda x: -x[1])[:6],
    }
    if not TOKEN:
        return data

    u = graphql("""query($u:String!){ user(login:$u){ createdAt
      contributionsCollection { totalCommitContributions }
      pullRequests { totalCount } followers { totalCount } } }""", u=user)["user"]
    days = []
    for year in range(int(u["createdAt"][:4]), dt.date.today().year + 1):
        cal = graphql("""query($u:String!,$f:DateTime!,$t:DateTime!){ user(login:$u){
          contributionsCollection(from:$f,to:$t){ contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }""",
                      u=user, f=f"{year}-01-01T00:00:00Z", t=f"{year}-12-31T23:59:59Z")
        for w in cal["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            days += [(d["date"], d["contributionCount"]) for d in w["contributionDays"]]
    days = sorted(d for d in dict(days).items() if d[0] <= dt.date.today().isoformat())
    data["days"] = days
    data["current"], data["longest"] = streaks(days)
    data["total"] = sum(n for _, n in days)
    data["commits"] = u["contributionsCollection"]["totalCommitContributions"]
    data["prs"] = u["pullRequests"]["totalCount"]
    data["followers"] = u["followers"]["totalCount"]
    return data


def row(i, inner):
    return f'<g class="row" style="animation-delay:{.2 + i * .1:.1f}s">{inner}</g>'


def render(d):
    # Colonne 1 : activité
    stats = [("Contributions", d.get("total", "—")), ("Commits (1 an)", d.get("commits", "—")),
             ("Pull requests", d.get("prs", "—")), ("Repos publics", d["repos"]),
             ("Étoiles", d["stars"]), ("Followers", d.get("followers", "—"))]
    col1 = "".join(row(i, f'<text x="36" y="{98 + i * 31}" class="l">{escape(k)}</text>'
                          f'<text x="264" y="{98 + i * 31}" class="v" text-anchor="end">{v}</text>')
                   for i, (k, v) in enumerate(stats))

    # Colonne 2 : langages
    total = sum(v for _, v in d["langs"]) or 1
    bar, x = [], 336
    for name, size in d["langs"]:
        w = size / total * 228
        bar.append(f'<rect class="seg" x="{x:.1f}" y="74" width="{w:.1f}" height="8" fill="{LANG_COLORS.get(name, MUTED)}"/>')
        x += w
    col2 = (f'<clipPath id="bar"><rect x="336" y="74" width="228" height="8" rx="4"/></clipPath>'
            f'<g clip-path="url(#bar)">{"".join(bar)}</g>')
    col2 += "".join(row(i, f'<circle cx="341" cy="{109 + i * 29}" r="5" fill="{LANG_COLORS.get(n, MUTED)}"/>'
                           f'<text x="354" y="{114 + i * 29}" class="v">{escape(n)}</text>'
                           f'<text x="564" y="{114 + i * 29}" class="l" text-anchor="end">{s / total * 100:.1f}%</text>')
                    for i, (n, s) in enumerate(d["langs"]))

    # Colonne 3 : série
    cur, best = d.get("current", "—"), d.get("longest", "—")
    col3 = f'''<circle cx="750" cy="146" r="52" fill="none" stroke="{LINE}" stroke-width="7"/>
<circle class="ring" cx="750" cy="146" r="52" fill="none" stroke="url(#g)" stroke-width="7" stroke-linecap="round" pathLength="1" transform="rotate(-90 750 146)"/>
<text x="750" y="160" class="big" text-anchor="middle">{cur}</text>
<text x="750" y="226" class="l" text-anchor="middle">{"jour d'affilée" if cur == 1 else "jours d'affilée"}</text>
{row(0, f'<text x="750" y="262" class="l" text-anchor="middle">Record : <tspan class="v">{best} j</tspan></text>')}'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#A5F3FC"/><stop offset=".5" stop-color="#2DD4BF"/><stop offset="1" stop-color="#0891B2"/></linearGradient>
  <linearGradient id="sep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2DD4BF" stop-opacity="0"/><stop offset=".5" stop-color="#2DD4BF" stop-opacity=".45"/><stop offset="1" stop-color="#2DD4BF" stop-opacity="0"/></linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#2DD4BF" fill-opacity=".14"/></pattern>
</defs>
<style>
  .h {{ font: 700 13px 'JetBrains Mono', 'Fira Code', Consolas, monospace; fill: {TITLE}; letter-spacing: 2.5px; }}
  .l {{ font: 400 14px 'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif; fill: {MUTED}; }}
  .v {{ font: 600 14px 'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif; fill: {TEXT}; }}
  .big {{ font: 800 40px 'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif; fill: {TEXT}; }}
  .row {{ animation: in .5s ease-out backwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(6px); }} }}
  .seg {{ animation: grow .9s ease-out backwards; transform-box: fill-box; transform-origin: left; }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} }}
  .ring {{ stroke-dasharray: {min(1, (cur if isinstance(cur, int) else 0) / max(best if isinstance(best, int) else 1, 1)):.3f} 1; animation: ring 1.4s ease-out .3s backwards; }}
  @keyframes ring {{ from {{ stroke-dasharray: 0 1; }} }}
</style>
<rect width="{W}" height="{H}" rx="18" fill="#0d1117"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
<text x="36" y="50" class="h">ACTIVITÉ</text>
<text x="336" y="50" class="h">LANGAGES</text>
<text x="636" y="50" class="h">SÉRIE</text>
<rect x="300" y="30" width="1" height="240" fill="url(#sep)"/>
<rect x="600" y="30" width="1" height="240" fill="url(#sep)"/>
{col1}
{col2}
{col3}
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/>
</svg>'''


LEVELS = ["#1b2a33", "#134e4a", "#0f766e", "#14b8a6", "#5eead4"]


def shade(color, k):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return f"#{int(r * k):02x}{int(g * k):02x}{int(b * k):02x}"


def render_contrib(days):
    """Graphique 3D isométrique des 12 derniers mois."""
    counts, today = dict(days), dt.date.today()
    start = today - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # recule au dimanche
    cells = []
    for i in range((today - start).days + 1):
        day = start + dt.timedelta(days=i)
        cells.append((i // 7, (day.weekday() + 1) % 7, counts.get(day.isoformat(), 0)))
    top = max((n for *_, n in cells), default=0) or 1

    W, H = 900, 470
    U, V = (13.5, 3.6), (-7.0, 7.5)  # axe des semaines, axe des jours
    ox, oy = 117, 170
    gap = .8
    boxes = []
    for w, d, n in sorted(cells, key=lambda c: c[0] * U[1] + c[1] * V[1]):
        lvl = 0 if n == 0 else min(4, 1 + int(n / top * 4 - 1e-9))
        h = 0 if n == 0 else 6 + (n / top) ** .6 * 70
        ax, ay = ox + w * U[0] + d * V[0], oy + w * U[1] + d * V[1]
        u, v = (U[0] * gap, U[1] * gap), (V[0] * gap, V[1] * gap)
        A, B, C, D = (ax, ay), (ax + u[0], ay + u[1]), (ax + u[0] + v[0], ay + u[1] + v[1]), (ax + v[0], ay + v[1])
        up = lambda p: (p[0], p[1] - h)
        poly = lambda pts, c: '<path d="M' + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + f'Z" fill="{c}"/>'
        col = LEVELS[lvl]
        faces = poly([up(A), up(B), up(C), up(D)], col)
        if h:
            faces = poly([D, C, up(C), up(D)], shade(col, .55)) + poly([B, C, up(C), up(B)], shade(col, .75)) + faces
        boxes.append(f'<g class="b" style="animation-delay:{w * .025:.2f}s">{faces}</g>')

    year = [n for _, _, n in cells]
    best = max(year, default=0)
    weeks = [sum(year[i:i + 7]) for i in range(0, len(year), 7)]
    legend = "".join(f'<rect x="{758 + i * 18}" y="{H - 44}" width="13" height="13" rx="3" fill="{c}"/>' for i, c in enumerate(LEVELS))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#A5F3FC"/><stop offset=".5" stop-color="#2DD4BF"/><stop offset="1" stop-color="#0891B2"/></linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#2DD4BF" fill-opacity=".1"/></pattern>
</defs>
<style>
  .h {{ font: 700 13px 'JetBrains Mono', 'Fira Code', Consolas, monospace; fill: {TITLE}; letter-spacing: 2.5px; }}
  .l {{ font: 400 14px 'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif; fill: {MUTED}; }}
  .v {{ font: 700 15px 'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif; fill: {TEXT}; }}
  .big {{ font: 800 44px 'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif; fill: url(#g); }}
  .b {{ transform-box: fill-box; transform-origin: 50% 100%; animation: grow .7s cubic-bezier(.2,.9,.3,1.15) backwards; }}
  @keyframes grow {{ from {{ transform: scaleY(0); opacity: 0; }} }}
</style>
<rect width="{W}" height="{H}" rx="18" fill="#0d1117"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
<text x="36" y="50" class="h">CONTRIBUTIONS</text>
<text x="864" y="62" class="big" text-anchor="end">{sum(year)}</text>
<text x="864" y="86" class="l" text-anchor="end">sur les 12 derniers mois</text>
{"".join(boxes)}
<text x="36" y="{H - 62}" class="l">Meilleur jour</text><text x="36" y="{H - 38}" class="v">{best} contributions</text>
<text x="200" y="{H - 62}" class="l">Meilleure semaine</text><text x="200" y="{H - 38}" class="v">{max(weeks, default=0)} contributions</text>
<text x="748" y="{H - 33}" class="l" text-anchor="end">Moins</text>{legend}<text x="854" y="{H - 33}" class="l">Plus</text>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/>
</svg>'''


if __name__ == "__main__":
    os.makedirs("stats", exist_ok=True)
    data = collect(sys.argv[1])
    open("stats/card.svg", "w").write(render(data))
    open("stats/contrib.svg", "w").write(render_contrib(data.get("days", [])))
    print("ok:", {k: v for k, v in data.items() if k not in ("langs", "days")})
