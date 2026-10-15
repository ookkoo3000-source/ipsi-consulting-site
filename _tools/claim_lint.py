"""
Suspect-phrase finder for blog posts, built from the 2026-10-15 content audit.

IMPORTANT — what this script is and is not:
  - It is a pattern-matching HELPER that flags sentences LIKELY to contain an
    unverified claim, so a human can review them. It has no access to any
    school's real records.
  - A clean run ("0건") means no known risky pattern matched -- it does NOT
    mean the content has been fact-checked or is true. Never report "lint
    passed" as if it were verification. Only an actual source (NEIS, a
    school's own site, something the business owner confirmed) verifies a
    claim.
  - It checks the whole page text, which includes <h3> subheadings, visible
    FAQ text, and the JSON-LD <script> blocks (their tag wrapper is stripped
    but the JSON string content is plain text to this scanner, so headline/
    description/FAQ fields inside JSON-LD are covered too).

Two findings categories:
  1. "학교/지역별 근거없는 주장" -- a sentence asserts something specific about
     a named school's or region's actual exams, difficulty, grading, or
     academy environment (출제 경향/난이도/채점 기준/학원 밀집도/학군 등),
     or uses a reputation-by-hearsay phrase ("~로 알려진/알려져 있다"), or
     refers to "이 학교/해당 학교" as if it has inside knowledge of it.
     None of this is itself confirmed by any source this script can check.
  2. "미확인 서비스 claim" -- a sentence states a specific tutoring technique
     as settled fact (reviewing the student's test papers, classifying wrong
     answers by type, grading-rubric-based correction, diagnostic tests,
     study planners, live annotation on an electronic board) that the
     business has not confirmed it actually offers.

Usage: python3 _tools/claim_lint.py blog/some-post.html [blog/another.html ...]
Exits non-zero if any file has findings.
"""
import re
import sys

# A specific named entity in the sentence raises confidence but is NOT
# required -- many risky sentences describe "그 지역 고등학교들은..." or
# "이 학교는..." without literally saying 고등학교/중학교 right there, and
# those must still be caught.
NAMED_ENTITY_HINTS = r"(?:고등학교|중학교|이 학교|해당 학교|그 학교)"

SCHOOL_OR_REGION_CLAIM_PATTERNS = [
    r"출제\s*경향",
    r"시험\s*경향",
    r"기출\s*(?:데이터|문제|경향|유형)",
    r"내신\s*분위기",
    r"채점\s*기준표",
    r"난이도가?\s*(?:높|낮|가파르|상당)",
    r"학원\s*(?:밀집도|환경|선택지)[^.]{0,10}(?:높|낮|많|적|좋|제한)",
    r"학군[^.]{0,10}(?:좋|높|치열|유명)",
    r"경쟁이?\s*(?:매우\s*)?치열",
    r"로\s*알려(?:져|진)",
    r"[가-힣]+만의\s*(?:차별화된|독자적인|고유한|특화된)\s*(?:교수법|강점|비법|전략)",
    r"자율형\s*사립|전국\s*단위에서[^.]{0,15}모이는",
    # school/region-specific difficulty asserted as settled fact, either word order
    r"(?:내신|시험|문제)[^.]{0,10}(?:어렵|까다롭|힘들)",
    r"(?:어려운|까다로운|힘든|상당한|높은|가파른)[^.]{0,10}(?:내신|시험\s*수준|난이도)",
    r"감점[^.]{0,10}(?:심하|많)",
    r"(?:특수한|독특한|남다른|유별난)[^.]{0,10}(?:내신|문제|시험|스타일|유형)",
    r"내신\s*특성(?:을|에|과|부터)?\s*(?:분석|반영|파악|맞춰|맞춘)?",
    r"(?:시험\s*범위|출제\s*스타일|기출\s*문항)(?:을|를)?\s*(?:철저히|완벽히|정확히)?\s*(?:분석|파악)",
    r"출제\s*스타일",  # broad catch-all: this phrase almost always implies claimed knowledge of a
                        # specific school/teacher's exam patterns, which this business does not have.
    r"학교별?\s*특이\s*(?:사항|점)",
    r"학교\s*특성",
]

UNCONFIRMED_SERVICE_PATTERNS = [
    r"(?:학생의|우리가|저희가|저희는)[^.]{0,15}시험지를?\s*(?:함께\s*)?(?:확인|검토|분석)",
    r"오답(?:을|의)\s*유형별로\s*분류",
    r"오답\s*노트를?\s*(?:분석|관리)",
    r"정밀\s*진단\s*검사",
    r"학습\s*플래너",
    r"채점\s*기준표에?\s*기반",
    r"전자\s*칠판.{0,15}실시간\s*첨삭",
]

ALL = [("학교/지역별 근거없는 주장", p) for p in SCHOOL_OR_REGION_CLAIM_PATTERNS] + [
    ("미확인 서비스 claim", p) for p in UNCONFIRMED_SERVICE_PATTERNS
]


def _split_sentences(text):
    text = re.sub(r"<[^>]+>", " ", text)
    return re.split(r"(?<=[.!?])\s+", text)


def lint(path):
    """Return a list of (category, sentence, has_named_entity) findings.
    This is a suspicion list, not a verification result -- see module docstring."""
    text = open(path, encoding="utf-8").read()
    findings = []
    for sentence in _split_sentences(text):
        if not sentence.strip():
            continue
        named = bool(re.search(NAMED_ENTITY_HINTS, sentence))
        for label, pattern in ALL:
            m = re.search(pattern, sentence)
            if m:
                # Show a window around the actual match, not just the
                # sentence's first 200 chars -- long merged JSON-LD "sentences"
                # otherwise hide where the match really is.
                start = max(0, m.start() - 60)
                end = min(len(sentence), m.end() + 60)
                ctx = sentence[start:end].strip()
                if start > 0:
                    ctx = "..." + ctx
                if end < len(sentence):
                    ctx = ctx + "..."
                findings.append((label, ctx, named))
    return findings


def main(paths):
    had_findings = False
    for p in paths:
        findings = lint(p)
        if findings:
            had_findings = True
            print(f"=== {p} ({len(findings)}건, 의심 표현 -- 사실 검증 아님) ===")
            for label, ctx, named in findings:
                tag = "특정 대상 언급" if named else "일반화 주장"
                print(f"  [{label} / {tag}] ...{ctx}...")
    if not had_findings:
        print(f"{len(paths)}개 파일에서 알려진 패턴은 안 걸림 (사실 검증된 것은 아님 -- 수동 검토 필요).")
    return 1 if had_findings else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 _tools/claim_lint.py <blog-post.html> [...]")
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
