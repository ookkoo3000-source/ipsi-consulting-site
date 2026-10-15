"""
Review gate for blog posts before publishing.

Catches two classes of problems found in the 2026-10-15 content audit:
1. Unsubstantiated school-specific claims ("OO고등학교의 출제 경향/난이도/채점 기준"
   style sentences) that assert knowledge of a real school's actual exams without
   any official source.
2. Unconfirmed service claims (specific tutoring techniques the business has not
   actually confirmed it offers, e.g. reviewing the student's own test papers,
   classifying wrong answers by type, grading-rubric-based correction, diagnostic
   tests, study planners) stated as settled fact.

Usage: python3 _tools/claim_lint.py blog/some-post.html [blog/another.html ...]
Exits non-zero if any file has findings, printing each match with context.
"""
import re
import sys

AND_SCHOOL_NOUN = r"(?:고등학교|중학교)"  # a literal school-level noun must appear in-sentence

# claim keyword must co-occur, in the SAME sentence, with a school-level noun
# (고등학교/중학교) to be flagged -- a bare "난이도"/"기출" in a generic sentence
# like "고등 수학은 난이도가 높다" is not itself a problem.
SCHOOL_CLAIM_PATTERNS = [
    r"출제\s*경향",
    r"시험\s*경향",
    r"기출\s*(?:데이터|문제|경향|유형)[^.]{0,20}(?:분석|파악|입수|보유|기반)",
    r"내신\s*분위기",
    r"채점\s*기준표",
    r"[가-힣]+만의\s*(?:차별화된|독자적인|고유한|특화된)\s*(?:교수법|강점|비법|전략)",
]

# these are standalone (don't require a school noun) because they describe an
# unconfirmed *service*, not a claim about a specific school's exams
UNCONFIRMED_SERVICE_PATTERNS = [
    r"(?:학생의|우리가|저희가|저희는)[^.]{0,15}시험지를?\s*(?:함께\s*)?(?:확인|검토|분석)",
    r"오답(?:을|의)\s*유형별로\s*분류",
    r"정밀\s*진단\s*검사",
    r"학습\s*플래너",
    r"채점\s*기준표에?\s*기반",
    r"전자\s*칠판.{0,15}실시간\s*첨삭",
]


def _split_sentences(text):
    # crude sentence split good enough for a lint pass over generated prose
    return re.split(r"(?<=[.!?])\s+", re.sub(r"<[^>]+>", " ", text))


def lint(path):
    text = open(path, encoding="utf-8").read()
    findings = []
    for sentence in _split_sentences(text):
        has_school_noun = re.search(AND_SCHOOL_NOUN, sentence)
        for pattern in SCHOOL_CLAIM_PATTERNS:
            if has_school_noun and re.search(pattern, sentence):
                findings.append(("학교별 근거없는 주장", sentence.strip()[:160]))
        for pattern in UNCONFIRMED_SERVICE_PATTERNS:
            if re.search(pattern, sentence):
                findings.append(("미확인 서비스 claim", sentence.strip()[:160]))
    return findings


def main(paths):
    had_findings = False
    for p in paths:
        findings = lint(p)
        if findings:
            had_findings = True
            print(f"=== {p} ({len(findings)}건) ===")
            for label, ctx in findings:
                print(f"  [{label}] ...{ctx}...")
    if not had_findings:
        print(f"{len(paths)}개 파일 전부 통과.")
    return 1 if had_findings else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 _tools/claim_lint.py <blog-post.html> [...]")
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
