from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_logo_mark(draw: ImageDraw.ImageDraw, origin: tuple[int, int], scale: float = 1.0) -> None:
    ox, oy = origin
    def p(x: float, y: float) -> tuple[int, int]:
        return int(ox + x * scale), int(oy + y * scale)

    shield_outer = [p(256, 62), p(405, 118), p(405, 230), p(386, 314), p(332, 394), p(256, 450), p(180, 394), p(126, 314), p(107, 230), p(107, 118)]
    shield_inner = [p(256, 104), p(363, 144), p(363, 226), p(348, 290), p(310, 352), p(256, 392), p(202, 352), p(164, 290), p(149, 226), p(149, 144)]
    draw.line(shield_outer + [shield_outer[0]], fill=(139, 92, 246), width=max(2, int(20 * scale)), joint="curve")
    draw.polygon(shield_inner, fill=(5, 5, 5), outline=(31, 41, 55))

    trace = [p(177, 245), p(231, 245), p(261, 177), p(296, 307), p(321, 245), p(370, 245)]
    draw.line(trace, fill=(248, 250, 252), width=max(2, int(17 * scale)), joint="curve")
    for xy, color in [
        (p(177, 245), (6, 182, 212)),
        (p(261, 177), (139, 92, 246)),
        (p(296, 307), (236, 72, 153)),
        (p(370, 245), (34, 197, 94)),
    ]:
        r = int(14 * scale)
        draw.ellipse((xy[0]-r, xy[1]-r, xy[0]+r, xy[1]+r), fill=color)
    check = [p(226, 354), p(250, 378), p(299, 320)]
    draw.line(check, fill=(34, 197, 94), width=max(2, int(18 * scale)), joint="curve")


def make_logo_png() -> None:
    img = Image.new("RGB", (1024, 1024), (5, 5, 5))
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((162, 112, 862, 862), fill=(88, 28, 135, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(46))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    draw = ImageDraw.Draw(img)
    draw_logo_mark(draw, (0, 0), 2.0)
    img.save(ASSETS / "aegiseval-logo.png")


def make_social_png() -> None:
    w, h = 1200, 420
    img = Image.new("RGB", (w, h), (5, 5, 5))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((-160, -220, 680, 620), fill=(49, 46, 129, 150))
    od.ellipse((680, 120, 1440, 680), fill=(8, 145, 178, 90))
    overlay = overlay.filter(ImageFilter.GaussianBlur(42))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)
    for x in range(0, w, 40):
        draw.line((x, 0, x, h), fill=(255, 255, 255, 3), width=1)
    for y in range(0, h, 40):
        draw.line((0, y, w, y), fill=(255, 255, 255, 3), width=1)
    draw_logo_mark(draw, (74, 76), 0.52)
    draw.text((372, 126), "AegisEval", fill=(248, 250, 252), font=font(74, bold=True))
    draw.text((376, 198), "Reliable infrastructure for agentic knowledge-work evals", fill=(203, 213, 225), font=font(26))
    labels = [(376, "traces", (139, 92, 246)), (532, "artifacts", (6, 182, 212)), (688, "eval audits", (34, 197, 94))]
    for x, label, color in labels:
        draw.line((x, 278, x + 126, 278), fill=color, width=3)
        draw.text((x, 303), label, fill=(229, 231, 235), font=font(22, bold=True))
    img.convert("RGB").save(ASSETS / "social-preview.png")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    make_logo_png()
    make_social_png()
    print("wrote", ASSETS / "aegiseval-logo.png")
    print("wrote", ASSETS / "social-preview.png")
