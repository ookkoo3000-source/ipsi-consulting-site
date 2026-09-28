# -*- coding: utf-8 -*-
"""블로그 대표 이미지 생성 (Gemini) — 티치핏 gen_image.py 지침을 스터디코칭 ON용으로 옮긴 것.
글자 내용은 전 글 동일 템플릿, 배경 풍경(motif)만 글마다 순환.
  python3 _tools/gen_image.py <slug> ["이미지에 넣을 학교명"] ["수학|영어|국어"]   # 1장
결과: images/blog/<slug>.webp (+ 공유 미리보기용 .jpg), 720x720
"""
import base64, io, json, os, re, sys, time, urllib.request
MODEL = "gemini-3.1-flash-image"
MOTIFS = [
 "a soft geometric small-town Korean high school building with a clock tower and a few trees",
 "a soft geometric study desk with a warm lamp, stacked books and a notebook beside a window",
 "a soft geometric bookshelf room with a ladder and a cozy reading chair",
 "a soft geometric laptop showing a friendly video call with a tutor next to a cup of tea",
 "a soft geometric quiet countryside road with rolling green hills and a small bus stop",
 "a soft geometric classroom with a chalkboard, wooden desks and sunlight through tall windows",
 "a soft geometric autumn schoolyard with ginkgo trees and a winding path",
 "a soft geometric rooftop of an old town at sunrise with mountains in the distance",
]
PROMPT = """A clean, professional graphic design template for an educational advertisement for a private tutoring service in a small Korean town. Square image with rounded corners on a slightly larger pale warm-cream background with a subtle block pattern. Color palette: deep navy, soft teal, cream white, with small coral-red accents. Scene style: {motif}. Keep the scene soft, flat and geometric, and keep it away from the center so the text stays perfectly legible. The top text in bold navy brackets reads "[{school}]". Below it is the large, very bold navy central title "{title}". Below the main title is smaller navy text "내신 관리 | 30분 무료체험". A clean white horizontal bar at the top and two small coral-red decorative dots. At the bottom, a rounded rectangular button-like element contains small navy text "무료 체험". Clean even lighting. IMPORTANT: all Korean text must be rendered exactly as written, character by character, sharp and legible, with no extra or altered text."""
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def api_key():
    return os.environ.get("GEMINI_IMAGE_KEY") or os.environ["GEMINI_API_KEY"]
def label_from_title(title):
    first = re.split(r"[ ,]", title)[0].strip("·,.")
    return first if first.endswith(("학교", "중", "고")) else first
def subject_from_title(title):
    return next((s for s in ("수학", "영어", "국어") if s in title), "")
def generate(slug, school, subject=""):
    from PIL import Image
    motif = MOTIFS[sum(ord(c) for c in slug) % len(MOTIFS)]
    title = f"1:1 {subject}과외" if subject else "1:1 과외"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key()}"
    body = {"contents": [{"parts": [{"text": PROMPT.format(motif=motif, school=school, title=title)}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    for part in d["candidates"][0]["content"]["parts"]:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline:
            raw = base64.b64decode(inline["data"]); break
    else:
        raise RuntimeError("no image: " + json.dumps(d)[:300])
    im = Image.open(io.BytesIO(raw)).convert("RGB"); im.thumbnail((720, 720))
    out = os.path.join(ROOT, "images", "blog"); os.makedirs(out, exist_ok=True)
    im.save(os.path.join(out, slug + ".webp"), "WEBP", quality=82)
    im.save(os.path.join(out, slug + ".jpg"), "JPEG", quality=85)
    print("saved", slug, f"[{school}]", title)
def generate_retry(slug, school, subject="", tries=3):
    for a in range(tries):
        try: return generate(slug, school, subject)
        except Exception as e:
            print("retry", slug, str(e)[:200]); time.sleep(10 * (a + 1))
    print("FAILED", slug)
if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: raise SystemExit(__doc__)
    generate_retry(a[0], a[1] if len(a) > 1 else label_from_title(a[0].replace("-", " ")), a[2] if len(a) > 2 else subject_from_title(a[0]))
