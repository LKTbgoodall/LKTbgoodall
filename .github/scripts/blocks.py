"""Génère les blocs du README (langages, outils, projets) dans assets/.

À lancer à la main après avoir modifié les listes ci-dessous :
    python3 .github/scripts/blocks.py
"""
import re
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"

LANGAGES = [("cs", "C#"), ("lua", "Lua"), ("c", "C"), ("rust", "Rust"),
            ("py", "Python"), ("js", "JavaScript"), ("html", "HTML"), ("css", "CSS")]
OUTILS = [("unity", "Unity"), ("robloxstudio", "Roblox Studio"), ("@fivem", "FiveM"), ("blender", "Blender"),
          ("git", "Git"), ("vscode", "VSCode"), ("arch", "Arch Linux")]
# (fichier, titre, description, logo, couleur du visuel, langage, couleur du langage)
PROJETS = [
    ("fivem-jobs", "FiveM Scripts Jobs", "Scripts de métiers pour serveur FiveM", "si:fivem", "#F40552", "Lua", "#6b7cff"),
    ("discord-bot-eti", "Discord Bot ETI", "Bot Discord pour le référencement ETI", "si:discord", "#5865F2", "JavaScript", "#f1e05a"),
    ("maze", "Résolveur de labyrinthes", "Résout des labyrinthes en C (main gauche)", "maze", "#F59E0B", "C", "#a8b1c2"),
    ("portfolio", "Portfolio", "Mon portfolio", "portfolio", "#2DD4BF", "HTML", "#e34c26"),
]

TEXT, MUTED = "#E2E8F0", "#8B93B5"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif"

DEFS = """<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#A5F3FC"/><stop offset=".5" stop-color="#2DD4BF"/><stop offset="1" stop-color="#0891B2"/></linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#2DD4BF" fill-opacity=".14"/></pattern>"""


def frame(w, h, body, style=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  {DEFS}
</defs>
<style>
  .in {{ animation: in .6s cubic-bezier(.2,.9,.3,1.2) backwards; transform-box: fill-box; transform-origin: center; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(14px) scale(.85); }} }}
  {style}
</style>
<rect width="{w}" height="{h}" rx="18" fill="#0d1117"/>
<rect width="{w}" height="{h}" rx="18" fill="url(#dots)"/>
{body}
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/>
</svg>
"""


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})) as r:
        return r.read().decode()


def icon(name, prefix):
    """SVG de l'icône sans sa balise racine, avec des id uniques."""
    src = (ASSETS / "fivem.svg").read_text() if name == "@fivem" else fetch(f"https://skillicons.dev/icons?i={name}")
    src = re.sub(r"^\s*<svg[^>]*>|</svg>\s*$", "", src.strip())
    src = re.sub(r'id="([^"]+)"', rf'id="{prefix}\1"', src)
    return re.sub(r'(url\(#|href="#)([^)"]+)', rf"\1{prefix}\2", src)


def icon_block(items, path):
    w, h, size = 900, 150, 54
    slot = (w - 60) / len(items)
    body = []
    for i, (name, label) in enumerate(items):
        cx = 30 + slot * (i + .5)
        body.append(
            f'<g class="in" style="animation-delay:{i * .08:.2f}s">'
            f'<svg x="{cx - size / 2:.1f}" y="30" width="{size}" height="{size}" viewBox="0 0 256 256">{icon(name, f"i{i}_")}</svg>'
            f'<text x="{cx:.1f}" y="118" text-anchor="middle" style="font: 600 14px {SANS}; fill: {TEXT}">{escape(label)}</text></g>')
    path.write_text(frame(w, h, "\n".join(body)))


def logo(name):
    """Logo en viewBox 24x24 : Simple Icons ("si:nom") ou dessin maison."""
    if name.startswith("si:"):
        src = fetch(f"https://cdn.simpleicons.org/{name[3:]}/ffffff")
        return "".join(re.findall(r"<path[^>]*/>", src))
    return {
        "pokeball": '<circle cx="12" cy="12" r="10.5" fill="#fff"/><path d="M1.5 12a10.5 10.5 0 0 1 21 0z" fill="#EF4444"/>'
                    '<rect x="1.5" y="10.9" width="21" height="2.2" fill="#0d1117"/>'
                    '<circle cx="12" cy="12" r="3.6" fill="#0d1117"/><circle cx="12" cy="12" r="2.2" fill="#fff"/>',
        "maze": '<g fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round">'
                '<path d="M4 0H24V20M24 24H0V0"/><path d="M4 0V8M8 0V8M0 12H12M12 4V20M12 6H16M16 6V12M20 4V18M16 18H24M4 16H10M8 16V24M0 20H4"/></g>'
                '<path class="solve" d="M2 0V10H10V2H18V14H14V22H24" pathLength="1" fill="none" stroke="#FCD34D" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
        "browser": '<rect x="1.5" y="3" width="21" height="18" rx="3" fill="none" stroke="#fff" stroke-width="1.6"/>'
                   '<path d="M1.5 7.5h21" stroke="#fff" stroke-width="1.6"/>'
                   '<circle cx="4.5" cy="5.25" r=".8" fill="#fff"/><circle cx="7" cy="5.25" r=".8" fill="#fff"/><circle cx="9.5" cy="5.25" r=".8" fill="#fff"/>'
                   '<rect x="4.5" y="10.5" width="7" height="7.5" rx="1" fill="#fff" fill-opacity=".9"/>'
                   '<path d="M14 11.5h5.5M14 14.25h5.5M14 17h3.5" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>',
    }[name]


def portfolio_art():
    """Illustration : porte-documents ouvert d'où sortent des planches de projets (viewBox 200x140)."""
    def card(cx, angle, delay, sky):
        x, y = cx - 35, 14
        return (f'<g class="rise" style="animation-delay:{delay}s"><g transform="rotate({angle} 100 135)">'
                f'<rect x="{x}" y="{y}" width="70" height="88" rx="6" fill="#0b1220" opacity=".35" transform="translate(2 3)"/>'
                f'<rect x="{x}" y="{y}" width="70" height="88" rx="6" fill="#F1F5F9"/>'
                f'<rect x="{x + 6}" y="{y + 6}" width="58" height="42" rx="3" fill="url(#{sky})"/>'
                f'<circle cx="{x + 48}" cy="{y + 17}" r="5" fill="#FEF3C7"/>'
                f'<path d="M{x + 6} {y + 48}l14-16 9 9 12-15 21 22z" fill="#0f766e" opacity=".85"/>'
                f'<path d="M{x + 6} {y + 48}l10-9 12 9z" fill="#134e4a"/>'
                f'<rect x="{x + 6}" y="{y + 56}" width="40" height="5" rx="2.5" fill="#334155"/>'
                f'<rect x="{x + 6}" y="{y + 66}" width="52" height="3.5" rx="1.75" fill="#94A3B8"/>'
                f'<rect x="{x + 6}" y="{y + 74}" width="30" height="3.5" rx="1.75" fill="#94A3B8"/></g></g>')

    def spark(x, y, r, delay):
        return (f'<path class="spark" style="animation-delay:{delay}s" d="M{x} {y - r}C{x + r * .15} {y - r * .15} {x + r * .15} {y - r * .15} {x + r} {y}'
                f'C{x + r * .15} {y + r * .15} {x + r * .15} {y + r * .15} {x} {y + r}C{x - r * .15} {y + r * .15} {x - r * .15} {y + r * .15} {x - r} {y}'
                f'C{x - r * .15} {y - r * .15} {x - r * .15} {y - r * .15} {x} {y - r}z" fill="#A5F3FC"/>')

    return f'''<defs>
  <linearGradient id="sky1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22D3EE"/><stop offset="1" stop-color="#F59E0B"/></linearGradient>
  <linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0891B2"/><stop offset="1" stop-color="#A5F3FC"/></linearGradient>
  <linearGradient id="sky3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6366F1"/><stop offset="1" stop-color="#F472B6"/></linearGradient>
  <linearGradient id="back" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#115e59"/><stop offset="1" stop-color="#0b3b38"/></linearGradient>
  <linearGradient id="flap" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14B8A6"/><stop offset="1" stop-color="#0F766E"/></linearGradient>
  <radialGradient id="shadow"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
</defs>
<ellipse cx="100" cy="135" rx="84" ry="6" fill="url(#shadow)"/>
<rect x="34" y="42" width="46" height="18" rx="5" fill="url(#back)"/>
<rect x="28" y="50" width="144" height="84" rx="8" fill="url(#back)"/>
{card(72, -15, .3, "sky3")}{card(128, 15, .45, "sky2")}{card(100, 0, .6, "sky1")}
<g transform="translate(0 6)"><path d="M26 70H174a6 6 0 0 1 5.9 7.1L171.6 121.3a8 8 0 0 1-7.9 6.7H36.3a8 8 0 0 1-7.9-6.7L20.1 77.1A6 6 0 0 1 26 70z" fill="url(#flap)"/>
<path d="M27 71.2H173" stroke="#5EEAD4" stroke-opacity=".7" stroke-width="1.4" stroke-linecap="round"/>
<rect x="80" y="92" width="40" height="13" rx="4" fill="#042f2e" fill-opacity=".35"/>
<rect x="86" y="97" width="28" height="3" rx="1.5" fill="#99F6E4" fill-opacity=".8"/></g>
{spark(30, 26, 7, 1.1)}{spark(172, 30, 5, 1.3)}{spark(160, 12, 3.5, 1.5)}{spark(44, 8, 3, 1.7)}'''


def project_card(slug, title, desc, logo_name, accent, lang, color, delay):
    w, h, ch = 440, 260, 150  # ch : hauteur du visuel
    body = f"""<defs>
  <clipPath id="cover"><path d="M18 0H{w - 18}a18 18 0 0 1 18 18V{ch}H0V18A18 18 0 0 1 18 0z"/></clipPath>
  <radialGradient id="spot" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="{accent}" stop-opacity=".55"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="{accent}" stop-opacity=".7"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#cover)">
  <rect width="{w}" height="{ch}" fill="#0a0f1a"/>
  <rect width="{w}" height="{ch}" fill="url(#spot)"/>
  <rect width="{w}" height="{ch}" fill="url(#dots)"/>
  <g fill="none" stroke="{accent}">
    <circle class="ring" cx="{w / 2}" cy="{ch / 2}" r="52" stroke-opacity=".35"/>
    <circle class="ring" cx="{w / 2}" cy="{ch / 2}" r="82" stroke-opacity=".2" style="animation-delay:.6s"/>
    <circle class="ring" cx="{w / 2}" cy="{ch / 2}" r="116" stroke-opacity=".1" style="animation-delay:1.2s"/>
  </g>
  <g class="in">
    <circle cx="{w / 2}" cy="{ch / 2}" r="60" fill="url(#halo)"/>
    {f'<svg x="{w / 2 - 100}" y="6" width="200" height="140" viewBox="0 0 200 140">{portfolio_art()}</svg>' if logo_name == "portfolio" else
     f'<svg x="{w / 2 - 36}" y="{ch / 2 - 36}" width="72" height="72" viewBox="0 0 24 24" fill="#fff" color="#E2E8F0">{logo(logo_name)}</svg>'}
  </g>
</g>
<rect y="{ch}" width="{w}" height="1.5" fill="url(#g)" opacity=".6"/>
<g class="in" style="animation-delay:{delay:.2f}s">
  <text x="26" y="{ch + 42}" style="font: 700 20px {SANS}; fill: {TEXT}">{escape(title)}</text>
  <text x="26" y="{ch + 68}" style="font: 400 15px {SANS}; fill: {MUTED}">{escape(desc)}</text>
  <circle cx="32" cy="{ch + 91}" r="6" fill="{color}"/>
  <text x="45" y="{ch + 96}" style="font: 600 14px {SANS}; fill: {TEXT}">{escape(lang)}</text>
  <svg class="arrow" x="{w - 46}" y="{ch + 24}" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2DD4BF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg>
</g>"""
    style = """.solve { stroke-dasharray: 1 1; stroke-dashoffset: 1; animation: solve 2.4s ease-in-out .6s forwards; } @keyframes solve { to { stroke-dashoffset: 0; } }
  .rise { animation: rise .8s cubic-bezier(.2,.9,.3,1.1) backwards; } @keyframes rise { from { transform: translateY(46px); opacity: 0; } }
  .spark { transform-box: fill-box; transform-origin: center; animation: spark .6s ease-out backwards; } @keyframes spark { from { transform: scale(0) rotate(-90deg); opacity: 0; } }
  .ring { transform-box: fill-box; transform-origin: center; animation: ring 1s ease-out backwards; } @keyframes ring { from { transform: scale(.6); opacity: 0; } }"""
    (ASSETS / "projets" / f"{slug}.svg").write_text(frame(w, h, body, style))


if __name__ == "__main__":
    icon_block(LANGAGES, ASSETS / "langages.svg")
    icon_block(OUTILS, ASSETS / "outils.svg")
    (ASSETS / "projets").mkdir(exist_ok=True)
    for i, p in enumerate(PROJETS):
        project_card(*p, delay=i * .1)
    print("ok")
