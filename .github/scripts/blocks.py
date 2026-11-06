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
# (fichier, titre, description, icône lucide, langage, couleur du langage)
PROJETS = [
    ("fivem-jobs", "FiveM Scripts Jobs", "Scripts de métiers pour serveur FiveM", "briefcase", "Lua", "#6b7cff"),
    ("discord-bot-eti", "Discord Bot ETI", "Bot Discord pour le référencement ETI", "bot", "JavaScript", "#f1e05a"),
    ("pokerogue-extension", "PokeRogue Extension", "Extension navigateur pour PokeRogue", "puzzle", "JavaScript", "#f1e05a"),
    ("portfolio", "Portfolio", "Mon portfolio", "globe", "HTML", "#e34c26"),
]

TEXT, MUTED = "#E2E8F0", "#8B93B5"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif"

DEFS = """<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C084FC"/><stop offset=".5" stop-color="#8B5CF6"/><stop offset="1" stop-color="#3B82F6"/></linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#8B5CF6" fill-opacity=".14"/></pattern>"""


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


def lucide(name):
    src = fetch(f"https://unpkg.com/lucide-static@0.460.0/icons/{name}.svg")
    return re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", src.strip(), flags=re.S)


def project_card(slug, title, desc, ico, lang, color, delay):
    w, h = 440, 150
    body = f"""<g class="in" style="animation-delay:{delay:.2f}s">
  <rect x="26" y="26" width="52" height="52" rx="14" fill="#8B5CF6" fill-opacity=".12" stroke="url(#g)" stroke-opacity=".6"/>
  <svg x="38" y="38" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{lucide(ico)}</svg>
  <text x="96" y="48" style="font: 700 20px {SANS}; fill: {TEXT}">{escape(title)}</text>
  <text x="96" y="74" style="font: 400 15px {SANS}; fill: {MUTED}">{escape(desc)}</text>
  <circle cx="102" cy="117" r="6" fill="{color}"/>
  <text x="115" y="122" style="font: 600 14px {SANS}; fill: {TEXT}">{escape(lang)}</text>
  <svg class="arrow" x="396" y="22" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg>
</g>"""
    style = ".arrow { animation: nudge 2.4s ease-in-out infinite; } @keyframes nudge { 50% { transform: translate(3px, -3px); } }"
    (ASSETS / "projets" / f"{slug}.svg").write_text(frame(w, h, body, style))


if __name__ == "__main__":
    icon_block(LANGAGES, ASSETS / "langages.svg")
    icon_block(OUTILS, ASSETS / "outils.svg")
    (ASSETS / "projets").mkdir(exist_ok=True)
    for i, p in enumerate(PROJETS):
        project_card(*p, delay=i * .1)
    print("ok")
