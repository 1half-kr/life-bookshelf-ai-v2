from promptflow.core import tool
import re
from typing import Dict, List, Optional
from rapidfuzz import fuzz

# ====== 축 감지 힌트(그대로 유지) ======
HINTS = {
    "who":   ["누가", "어떤 사람", "본인", "부모", "친구", "선생님", "상사", "동료"],
    "why":   ["왜", "이유", "계기", "동기", "목적", "결심", "결정"],
    "when":  ["언제", "시기", "연도", "해", "달", "날", "때", "초등학교", "대학", "입사"],
    "how":   ["어떻게", "방법", "방식", "과정", "절차", "수단", "전략", "구체적으로"],
    "where": ["어디", "장소", "지역", "도시", "고향", "학교", "회사", "부서", "지점"],
    "what":  ["무엇", "무슨", "어떤 일", "내용", "사건", "경험", "에피소드"],
}
EX_HINTS  = ["예시", "사례", "예를", "예로", "구체적 사례"]
CON_HINTS = ["구체적", "구체적으로", "디테일", "상세히", "세부적으로"]

# ====== A안: 룰 기반 키워드 추출(고도화) ======
STOPWORDS = {
    "그리고", "그러면", "정말", "근데", "또", "너무", "거기", "여기", "저기", "보다", "하다", "되다",
    "같다", "때문", "그때", "이번", "지난", "사실", "그래서", "그", "이", "저", "그런", "이런", "저런",
    "거의", "조금", "많이", "항상", "먼저", "다음", "먼저는", "혹시", "약간", "진짜", "그러니까"
}
KOREAN_PATTERN = re.compile(r"[가-힣]{2,10}")

def _hit_any(text: str, words: List[str]) -> bool:
    if not text or not words:
        return False
    return any(w in text for w in words)

def _dedup_similar(tokens: List[str], threshold: int = 88) -> List[str]:
    if not tokens:
        return []
    kept: List[str] = []
    for t in tokens:
        if not t:
            continue
        if any(fuzz.partial_ratio(t, k) >= threshold for k in kept):
            continue
        kept.append(t)
    return kept

def _extract_keywords_rule(answer: str, top_k: int = 5, ban: Optional[set] = None) -> List[str]:
    text = answer or ""
    toks = KOREAN_PATTERN.findall(text)
    freq = {}
    particle_pattern = r"(에게|에서|으로|으로서|부터|까지|보다|마다|처럼|이고|이며|했던|했었|하고|같은|같이|해서|해서는|하면서)$"
    
    for t in toks:
        if t in STOPWORDS: 
            continue
        if ban and t in ban:
            continue
        # 흔한 조사/어미 꼬리를 러프하게 제거
        t2 = re.sub(particle_pattern, "", t)
        if len(t2) < 2:
            continue
        freq[t2] = freq.get(t2, 0) + 1
    
    cand = [w for w, _ in sorted(freq.items(), key=lambda x: (-x[1], x[0]))]
    cand = _dedup_similar(cand, threshold=88)
    return cand[:top_k]

# ====== B안: LLM 기반 키워드 추출(옵션) ======
def _extract_keywords_llm(answer: str, top_k: int = 5) -> List[str]:
    try:
        from openai import OpenAI
        import json, os
        
        # AZURE_OPENAI_API_KEY 또는 OPENAI_API_KEY 사용
        api_key = os.environ.get("AZURE_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return []
        
        prompt = (
            "다음 한국어 답변에서 핵심 키워드 3~5개를 JSON 배열로만 추출하세요.\n"
            '형태: ["키워드1","키워드2",...]\n\n'
            f"답변:\n{answer}\n"
        )
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-5-nano"),
            temperature=0.2,
            messages=[{"role":"user","content": prompt}],
            max_tokens=128,
        )
        txt = (resp.choices[0].message.content or "[]").strip()
        arr = json.loads(txt)
        arr = [s for s in arr if isinstance(s, str)]
        return arr[:top_k]
    except Exception as e:
        print(f"[WARN] LLM 키워드 추출 실패: {str(e)}")
        return []

@tool
def parse_answer(
    question: Dict,
    answer_text: str,
    metrics: Dict,
    use_llm_keywords: bool = False,
) -> Dict:
    materials_in_metrics = (metrics or {}).get("materials", {})
    # 응답에 언급된 소재 간이 탐지
    answer = answer_text or ""
    material_hits = [m for m in materials_in_metrics if m and m in answer]
    if not material_hits and question and question.get("material"):
        material_hits = [question["material"]]

    axes_evidence = {k: _hit_any(answer_text, HINTS[k]) for k in HINTS.keys()}
    ex_flag  = 1 if _hit_any(answer_text, EX_HINTS)  else 0
    con_flag = 1 if _hit_any(answer_text, CON_HINTS) else 0
    if not con_flag and len(answer_text or "") >= 80:  # 길이 기반 보정
        con_flag = 1

    # 키워드 추출 (먼저 룰 → 부족하면 LLM 시도)
    ban = set(material_hits or [])
    kw = _extract_keywords_rule(answer_text, top_k=5, ban=ban)
    if use_llm_keywords and len(kw) < 3:
        llm_kw = _extract_keywords_llm(answer_text, top_k=5)
        if llm_kw:
            kw = llm_kw
    parsed = {
        "material_hits": material_hits,
        "keywords": kw,
        "axes_evidence": axes_evidence,   # who/why/when/how/where/what -> bool
        "ex_flag": ex_flag,               # int(0/1)
        "con_flag": con_flag              # int(0/1)
    }
    return {"parsed": parsed}
