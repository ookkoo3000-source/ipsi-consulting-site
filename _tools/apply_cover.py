# -*- coding: utf-8 -*-
"""글 페이지의 대표 이미지를 생성 이미지(images/blog/<slug>.webp)로 교체하고 og:image·JSON-LD 이미지도 함께 갱신.
  python3 _tools/apply_cover.py <blog/파일명.html> [...]     # 이미지 없으면 gen_image로 생성(GEMINI_IMAGE_KEY 또는 GEMINI_API_KEY 필요)
"""
import os, re, sys
from urllib.parse import quote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_image
BASE = "https://primeadmit.co.kr"
def apply(path):
    fn = os.path.basename(path); slug = fn[:-5]
    h = open(path, encoding="utf-8").read()
    if 'class="post-cover"' in h: return "skip"
    title = re.search(r'<title>(.*?) \| 스터디코칭 ON</title>', h).group(1)
    webp = os.path.join(gen_image.ROOT, "images", "blog", slug + ".webp")
    if not os.path.exists(webp):
        gen_image.generate_retry(slug, gen_image.label_from_title(title), gen_image.subject_from_title(title))
    if not os.path.exists(webp): return "noimage"
    old = re.search(r'<img src="\.\./images/blog/(blog-\d+)\.jpg"[^>]*>', h)
    if not old: return "noimg-tag"
    q = quote(slug)
    tag = f'<img class="post-cover" src="../images/blog/{q}.webp" width="720" height="720" alt="{title} 1:1 과외 안내" loading="eager">'
    h = h.replace(old.group(0), tag, 1)
    h = h.replace(f"{BASE}/images/blog/{old.group(1)}.jpg", f"{BASE}/images/blog/{q}.jpg")
    open(path, "w", encoding="utf-8").write(h); return "ok"
if __name__ == "__main__":
    for p in sys.argv[1:]: print(p, apply(p))
