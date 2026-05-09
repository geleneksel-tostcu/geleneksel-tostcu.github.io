"""Generate a 1200x630 Open Graph cover image for Geleneksel Tostçu."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1200, 630

# --- Background: blurred & darkened tost photo -----------------------------
bg_src = Image.open(os.path.join(ROOT, "images", "tost", "tamkav.webp")).convert("RGB")

# Cover-fit crop to 1200x630
src_ratio = bg_src.width / bg_src.height
dst_ratio = W / H
if src_ratio > dst_ratio:
    new_h = H
    new_w = int(src_ratio * new_h)
else:
    new_w = W
    new_h = int(new_w / src_ratio)
bg = bg_src.resize((new_w, new_h), Image.LANCZOS)
left = (new_w - W) // 2
top = (new_h - H) // 2
bg = bg.crop((left, top, left + W, top + H))

# Blur + darken
bg = bg.filter(ImageFilter.GaussianBlur(radius=14))
bg = ImageEnhance.Brightness(bg).enhance(0.45)
bg = ImageEnhance.Color(bg).enhance(0.85)

# Warm overlay gradient (dark brown -> dark green) for cohesive brand feel
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
for x in range(W):
    t = x / (W - 1)
    # left: deep brown (#3a1f10) ; right: deep green (#0e2a1f)
    r = int((1 - t) * 58 + t * 14)
    g = int((1 - t) * 31 + t * 42)
    b = int((1 - t) * 16 + t * 31)
    a = 165  # ~65% opacity
    od.line([(x, 0), (x, H)], fill=(r, g, b, a))

canvas = bg.convert("RGBA")
canvas = Image.alpha_composite(canvas, overlay)

# Subtle vignette
vignette = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vignette)
vd.ellipse((-200, -200, W + 200, H + 200), fill=255)
vignette = vignette.filter(ImageFilter.GaussianBlur(160))
black = Image.new("RGBA", (W, H), (0, 0, 0, 120))
canvas = Image.composite(canvas, Image.alpha_composite(canvas, black),
                         vignette)

draw = ImageDraw.Draw(canvas)

# --- Logo on the left -------------------------------------------------------
logo = Image.open(os.path.join(ROOT, "images", "diger", "logo.webp")).convert("RGBA")
# Logo image has lots of whitespace; use it directly but resize
logo_h = 380
ratio = logo_h / logo.height
logo_w = int(logo.width * ratio)
logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

# Soft white circular backdrop behind logo for contrast
disc_d = 420
disc = Image.new("RGBA", (disc_d, disc_d), (0, 0, 0, 0))
dd = ImageDraw.Draw(disc)
dd.ellipse((0, 0, disc_d, disc_d), fill=(255, 255, 255, 235))
disc_x = 60
disc_y = (H - disc_d) // 2
canvas.alpha_composite(disc, (disc_x, disc_y))

logo_x = disc_x + (disc_d - logo_w) // 2
logo_y = disc_y + (disc_d - logo_h) // 2
canvas.alpha_composite(logo, (logo_x, logo_y))

# --- Text on the right ------------------------------------------------------
def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

font_title = load_font(96, bold=True)
font_sub = load_font(40, bold=False)
font_tag = load_font(30, bold=True)

text_x = disc_x + disc_d + 50
draw = ImageDraw.Draw(canvas)

# Small tag pill: SIRKECI · SINCE 2004
tag_text = "SIRKECI  ·  SINCE 2004"
bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
pad_x, pad_y = 22, 10
pill_w = tw + pad_x * 2
pill_h = th + pad_y * 2
pill_x = text_x
pill_y = 130
pill = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
pd = ImageDraw.Draw(pill)
pd.rounded_rectangle((0, 0, pill_w, pill_h), radius=pill_h // 2,
                     fill=(212, 165, 100, 255))  # warm gold
canvas.alpha_composite(pill, (pill_x, pill_y))
draw = ImageDraw.Draw(canvas)
draw.text((pill_x + pad_x - bbox[0], pill_y + pad_y - bbox[1]),
          tag_text, font=font_tag, fill=(40, 22, 10, 255))

# Title
title_y = pill_y + pill_h + 25
draw.text((text_x, title_y), "Geleneksel",
          font=font_title, fill=(255, 255, 255, 255))
title2_y = title_y + 100
draw.text((text_x, title2_y), "Tostçu",
          font=font_title, fill=(238, 180, 110, 255))  # warm orange

# Subtitle
sub_y = title2_y + 130
draw.text((text_x, sub_y),
          "Sirkeci'nin meşhur lezzeti",
          font=font_sub, fill=(235, 230, 220, 255))

# --- Save -------------------------------------------------------------------
out_webp = os.path.join(ROOT, "images", "diger", "og-image.webp")
out_jpg = os.path.join(ROOT, "images", "diger", "og-image.jpg")
canvas.convert("RGB").save(out_webp, "WEBP", quality=90, method=6)
canvas.convert("RGB").save(out_jpg, "JPEG", quality=88, optimize=True)
print("WROTE", out_webp)
print("WROTE", out_jpg)
print("SIZE", os.path.getsize(out_webp), "/", os.path.getsize(out_jpg))
