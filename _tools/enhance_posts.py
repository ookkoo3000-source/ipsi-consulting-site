# -*- coding: utf-8 -*-
"""블로그 글 페이지를 티치핏식 구성으로 변환 (요약박스·핵심정리·섹션박스·중간CTA·관련글·목록 링크). 이미 변환된 글은 건너뜀.
  python3 _tools/enhance_posts.py            # blog/*.html 전체 (미변환 글만)
"""
import re, glob, os, hashlib
def load_titles():
    h = open("blog.html", encoding="utf-8").read()
    return {m.group(2): m.group(1) for m in re.finditer(r'<h3>(.*?)</h3>.*?<a href="blog/([^"]+)">', h, re.S)}  # href -> title
def subject_of(t):
    return next((s for s in ("수학", "영어", "국어") if s in t), "")
def pick_related(fn, titles, n=3):
    me = titles.get(fn, "")
    pool = [k for k in titles if k != fn and not k.startswith("_")]
    same = [k for k in pool if subject_of(titles[k]) == subject_of(me) and subject_of(me)]
    cand = same if len(same) >= n else pool
    cand.sort(key=lambda k: hashlib.md5((fn + k).encode()).hexdigest())
    return [(titles[k], k) for k in cand[:n]]
def enhance(html, related):
    m = re.search(r'(<article style="max-width:760px;margin:0 auto">)(.*?)(</article>)', html, re.S)
    if not m or 'summary-box' in html: return None
    head, inner, tail = m.group(1), m.group(2), m.group(3)
    im = re.match(r'\s*(<img[^>]*>)', inner)
    pm = re.search(r'<div class="prose">(.*?)(<p style="font-weight:800[^>]*>자주 묻는 질문</p>)\s*(<div class="faq-list">.*)', inner, re.S)
    if not im or not pm: return None
    prose = re.sub(r'\s*</div>\s*$', '', pm.group(1))
    label, rest = pm.group(2), pm.group(3)
    depth, end = 0, None
    for t in re.finditer(r'<div|</div>', rest):
        depth += 1 if t.group(0) == '<div' else -1
        if depth == 0: end = t.end(); break
    if end is None: return None
    faq = rest[:end]
    parts = re.split(r'(?=<h3>)', prose)
    intro, secs = parts[0], parts[1:]
    if len(secs) < 4: return None
    titles = [re.sub(r'<[^>]+>', '', re.search(r'<h3>(.*?)</h3>', s).group(1)) for s in secs]
    box = '<div class="summary-box"><strong>이 글 한눈에 보기</strong><ul>' + ''.join(f'<li>{t}</li>' for t in titles[:5]) + '<li>방문·화상 중 맞는 방식은 상담으로 먼저 확인해보실 수 있어요.</li></ul></div>'
    out = [im.group(1), box, intro]
    for i, s in enumerate(secs):
        if i in (1, 3):
            mm = next((x for x in re.finditer(r'<p>((?:(?!</p>).)*?)<strong>([^<]*)</strong>((?:(?!</p>).)*?)</p>', s, re.S)
                       if len(x.group(2)) > 20 and not any(k in x.group(2) for k in ('상상코칭', '합격', '대학', '동화세상'))), None)
            if mm:
                para = (mm.group(1).strip() + ' ' + mm.group(3).strip()).strip()
                s = s[:mm.start()] + (f'<p>{para}</p>' if para else '') + f'<div class="callout"><b>핵심 정리</b>{mm.group(2)}</div>' + s[mm.end():]
        out.append('<div class="pbox">' + s + '</div>')
        if i == 2:
            out.append('<div class="mid-cta"><span>우리 아이에게 맞는 수업 방식이 궁금하시다면<br>상담으로 먼저 확인해보세요.</span><a href="../index.html#apply">상담 신청하기 →</a></div>')
    out.append('<div class="pbox faq-box">' + label + faq + '</div>')
    if related:
        out.append('<div class="related"><b>함께 보면 좋은 글</b><ul>' + ''.join(f'<li><a href="{h}">{t}</a></li>' for t, h in related) + '</ul></div>')
    out.append('<a class="back-list" href="../blog.html">← 블로그 목록으로</a>')
    html = html[:m.start()] + head + ''.join(out) + tail + html[m.end():]
    return html.replace('<section class="detail-hero"><div class="wrap"><span class="eyebrow">', '<section class="detail-hero"><div class="wrap"><nav class="breadcrumb"><a href="../blog.html">블로그</a> / STUDY</nav><span class="eyebrow">', 1)
if __name__ == "__main__":
    titles = load_titles(); ok = skip = 0; skipped = []
    for f in sorted(glob.glob("blog/*.html")):
        fn = os.path.basename(f)
        if fn.startswith("_"): continue
        h = open(f, encoding="utf-8").read()
        r = enhance(h, pick_related(fn, titles))
        if r is None: skip += 1; skipped.append(fn); continue
        open(f, "w", encoding="utf-8").write(r); ok += 1
    print("enhanced", ok, "skipped", skip, skipped[:12])
