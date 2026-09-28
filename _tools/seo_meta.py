import re, json, glob, os
from urllib.parse import quote
BASE = "https://primeadmit.co.kr"
BRAND = "스터디코칭 ON"
def esc(s): return s.replace("&","&amp;").replace('"',"&quot;")
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + '</script>'
def tags(title, desc, path, otype="website", image=None, extra=""):
    url = BASE + "/" + quote(path) if path else BASE + "/"
    t = f'<link rel="canonical" href="{url}"><meta property="og:type" content="{otype}"><meta property="og:site_name" content="{BRAND}"><meta property="og:locale" content="ko_KR"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">'
    if image: t += f'<meta property="og:image" content="{image}">'
    t += f'<meta name="twitter:card" content="{"summary_large_image" if image else "summary"}"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}">'
    if image: t += f'<meta name="twitter:image" content="{image}">'
    return t + extra, url
def crumbs(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":u} for i,(n,u) in enumerate(items)]}
ORG = {"@type":"EducationalOrganization","@id":BASE+"/#org","name":BRAND,"url":BASE+"/","telephone":"+82-10-3131-5305","description":"초등학생·중학생·고등학생 대상 1:1 대면(방문)과외, 비대면 화상과외, 수학과외·영어과외 내신 관리"}
TOP = {
 "index.html": ("대면과외·화상과외 | 중학생 과외·고등학교 과외 | 스터디코칭 ON",
   "초등·중학생·고등학생 1:1 과외. 대면(방문)과외와 비대면 화상과외 중 맞는 방식을 상담으로 정하고, 수학과외·영어과외 내신 관리까지 30분 무료 체험수업으로 먼저 확인해 보세요."),
 "visiting.html": ("대면과외(방문과외) | 중학생·고등학교 1:1 방문 수업 | 스터디코칭 ON",
   "선생님이 직접 찾아가는 1:1 대면과외(방문과외). 중학생 과외·고등학교 과외, 수학과외·영어과외 내신 과외를 학생 상황에 맞춰 상담으로 안내해 드립니다."),
 "online.html": ("화상과외 | 중학생·고등학교 1:1 실시간 화상 수업 | 스터디코칭 ON",
   "이동 시간 없는 1:1 화상과외(비대면과외). 중학생 과외·고등학교 과외, 수학과외·영어과외 내신 관리를 실시간 화면 공유로 진행하며 지역 제약 없이 과외 선생님을 만날 수 있습니다."),
 "about.html": ("회사 소개 | 대면과외·화상과외 스터디코칭 ON",
   "스터디코칭 ON 회사 소개. 1:1 대면과외와 화상과외를 함께 운영하는 기준, 운영 철학과 선생님 선발 기준을 안내합니다."),
 "reviews.html": ("수업 사례 | 대면과외·화상과외 진행 방식 | 스터디코칭 ON",
   "대면과외와 화상과외가 실제로 어떻게 진행되는지 수업 사례로 소개합니다. 중학생·고등학생 학습 관리 흐름을 확인해 보세요."),
 "blog.html": ("블로그 | 중학생 과외·고등학교 과외 학습 전략 | 스터디코칭 ON",
   "중학생 과외·고등학교 과외, 수학과외·영어과외 내신 과외 학습 전략과 지역별 대면과외·화상과외 안내 글 모음."),
}
HERO_ADD = {
 "index.html": ('<p class="lead">1:1 방문 수업과 1:1 화상 수업 — 정하기 전에 30분 무료 수업으로 선생님과 먼저 만나보세요. 맞지 않으면 언제든 다른 선생님으로 바꿔드립니다.</p>',
   '<p class="lead">1:1 방문 수업과 1:1 화상 수업 — 정하기 전에 30분 무료 수업으로 선생님과 먼저 만나보세요. 맞지 않으면 언제든 다른 선생님으로 바꿔드립니다. 중학생 과외·고등학교 과외를 찾는 가정도 대면과외(방문과외)와 화상과외 중 맞는 방식을 상담으로 정할 수 있습니다.</p>'),
 "visiting.html": ("1:1 방문 수업입니다. 과목별 학습과 학습 습관 관리, 학부모 피드백까지 한 흐름으로 진행합니다.</p>",
   "1:1 방문 수업입니다. 과목별 학습과 학습 습관 관리, 학부모 피드백까지 한 흐름으로 진행합니다. 중학생 과외·고등학교 과외를 고민 중이라면 1:1 대면과외(방문과외)로 학습 상태를 직접 확인받을 수 있습니다.</p>"),
 "online.html": ("학습 계획이 분명하게 남도록 진행합니다.</p>",
   "학습 계획이 분명하게 남도록 진행합니다. 중학생 과외·고등학교 과외를 고민 중이라면 이동 시간 없이 시작할 수 있는 1:1 화상과외로 상담받아 보세요.</p>"),
 "blog.html": ("이 페이지는 새로운 글을 계속 추가할 수 있는 뉴스·블로그 공간입니다.</p>",
   "이 페이지는 새로운 글을 계속 추가할 수 있는 뉴스·블로그 공간입니다. 중학생 과외·고등학교 과외 학습 전략과 대면과외·화상과외 안내 글을 모았습니다.</p>"),
}
def do_top(f):
    h = open(f, encoding="utf-8").read()
    if 'rel="canonical"' in h: return "skip"
    title, desc = TOP[f]
    path = "" if f == "index.html" else f
    extra = ""
    if f == "index.html":
        extra = ld({"@context":"https://schema.org","@graph":[ORG,{"@type":"WebSite","@id":BASE+"/#site","url":BASE+"/","name":BRAND,"inLanguage":"ko-KR","publisher":{"@id":BASE+"/#org"}}]})
    else:
        extra = ld(crumbs([("홈",BASE+"/"),(title.split(" | ")[0],BASE+"/"+f)]))
    meta, _ = tags(title, desc, path, extra=extra)
    h2 = re.sub(r'<meta name="description" content="[^"]*"\s*/?><title>[^<]*</title>', lambda m: f'<meta name="description" content="{esc(desc)}"><title>{title}</title>' + meta, h, count=1)
    assert h2 != h, f
    if f in HERO_ADD:
        a, b = HERO_ADD[f]; assert a in h2, f; h2 = h2.replace(a, b, 1)
    open(f, "w", encoding="utf-8").write(h2); return "ok"
def do_post(f):
    h = open(f, encoding="utf-8").read()
    if 'rel="canonical"' in h: return "skip"
    m = re.search(r'<meta name="description" content="([^"]*)"><title>([^<]*)</title>', h)
    if not m: return "nohead"
    desc, full = m.group(1), m.group(2)
    title = full.replace(" | " + BRAND, "")
    fn = os.path.basename(f)
    d = re.search(r'(\d{4})\. (\d{2})\. (\d{2}) · ', h)
    date = f"{d.group(1)}-{d.group(2)}-{d.group(3)}" if d else None
    im = re.search(r'<img src="\.\./(images/blog/[^"]+)"', h)
    image = BASE + "/" + im.group(1) if im else None
    faqs = re.findall(r'<div class="faq">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>\s*</div>', h, re.S)
    url = BASE + "/blog/" + quote(fn)
    art = {"@context":"https://schema.org","@type":"BlogPosting","headline":title,"description":desc,"inLanguage":"ko-KR","mainEntityOfPage":url,"author":{"@type":"Organization","name":BRAND,"url":BASE+"/"},"publisher":{"@type":"Organization","name":BRAND,"url":BASE+"/"}}
    if date: art["datePublished"] = date; art["dateModified"] = date
    if image: art["image"] = [image]
    extra = ld(art) + ld(crumbs([("홈",BASE+"/"),("블로그",BASE+"/blog.html"),(title,url)]))
    if faqs:
        clean = lambda s: re.sub(r'<[^>]+>','',s).strip()
        extra += ld({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":clean(q),"acceptedAnswer":{"@type":"Answer","text":clean(a)}} for q,a in faqs]})
    meta, _ = tags(title, desc, "blog/" + fn, otype="article", image=image, extra=(f'<meta property="article:published_time" content="{date}">' if date else "") + extra)
    h2 = h.replace(m.group(0), m.group(0) + meta, 1)
    open(f, "w", encoding="utf-8").write(h2); return "ok"
if __name__ == "__main__":
    from collections import Counter
    c = Counter()
    for f in TOP: c["top:"+do_top(f)] += 1
    for f in sorted(glob.glob("blog/*.html")):
        if os.path.basename(f).startswith("_"): continue
        c["post:"+do_post(f)] += 1
    print(dict(c))
