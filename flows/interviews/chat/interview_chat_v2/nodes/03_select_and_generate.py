from promptflow.core import tool, Flow
from typing import Dict
import random
from uuid import uuid4
from pathlib import Path

TYPE2W = {"when":"w1","how":"w2","who":"w3","what":"w4","where":"w5","why":"w6"}
W_KEYS = ["w1","w2","w3","w4","w5","w6"]

def _sum_progress(m: Dict) -> int:
    return sum(int(m.get(w,0)) for w in W_KEYS) + int(m.get("ex",0)) + int(m.get("con",0))

def _choose_material(metrics: Dict) -> str:
    mats = (metrics or {}).get("materials", {}) or {}
    chunks = (metrics or {}).get("chunks", {}) or {}
    glb = (metrics or {}).get("global", {}) or {}

    last = glb.get("last_material")
    streak = int(glb.get("last_material_streak", 0))

    if last and streak < 3:
        m = mats.get(last, {})
        if int(m.get("material_count",0)) == 0:
            return last

    if chunks:
        best_ck = max(chunks.items(), key=lambda kv: int((kv[1] or {}).get("chunk_weight",0)))[0]
        cat, chk = best_ck.split("::", 1)
        cands = [name for name, m in mats.items() if m.get("category_name")==cat and m.get("chunk_name")==chk and int(m.get("material_count",0))==0]
        if cands:
            cands.sort(key=lambda name: _sum_progress(mats[name]))
            minv = _sum_progress(mats[cands[0]])
            top = [n for n in cands if _sum_progress(mats[n]) == minv]
            return random.choice(top)

    remaining = [name for name, m in mats.items() if int(m.get("material_count",0))==0]
    if remaining:
        remaining.sort(key=lambda name: _sum_progress(mats[name]))
        minv = _sum_progress(mats[remaining[0]])
        top = [n for n in remaining if _sum_progress(mats[n]) == minv]
        return random.choice(top)

    return list(mats.keys())[0] if mats else ""

def _choose_type(m_entry: Dict) -> str:
    missing = []
    for t, w in TYPE2W.items():
        if int(m_entry.get(w,0)) == 0:
            missing.append(t)
    if int(m_entry.get("ex",0)) == 0: missing.append("ex")
    if int(m_entry.get("con",0)) == 0: missing.append("con")
    if not missing:
        return ""

    if "how" in missing: return "how"
    if "ex"  in missing: return "ex"
    if "con" in missing: return "con"
    return random.choice(missing)

def _generate_question_llm(material: str, t: str, keywords: list) -> str:
    import traceback
    
    try:
        current_dir = Path(__file__).parent
        flows_dir = current_dir.parent.parent.parent.parent
        flow_path = flows_dir / "interviews" / "standard" / "generate_interview_questions_v2" / "flow.dag.yaml"
        
        print(f"[DEBUG] Current file: {__file__}")
        print(f"[DEBUG] Flow path: {flow_path}")
        print(f"[DEBUG] Flow path exists: {flow_path.exists()}")
        print(f"[DEBUG] Absolute path: {flow_path.absolute()}")
        
        if not flow_path.exists():
            raise FileNotFoundError(f"Flow not found: {flow_path}")
        
        flow = Flow.load(str(flow_path.absolute()))
        print(f"[DEBUG] Flow loaded successfully")
        
        result = flow(
            material=material,
            type=t,
            keywords=keywords[:3] if keywords else [],
            tone="따뜻하고 존중하는 어조",
            max_len=120,
            model="gpt-4o-mini",
            temperature=0.8
        )
        print(f"[DEBUG] Flow result: {result}")
        question_text = result.get("question", {}).get("text", "")
        print(f"[DEBUG] Question text: {question_text}")
        return question_text
    except Exception as e:
        print(f"[ERROR] LLM 오류: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        if t == "ex":  return f"{material}에 대한 구체적인 사례를 한 가지 들려주실 수 있을까요?"
        if t == "con": return f"{material}과(와) 관련된 내용을 좀 더 구체적으로 설명해 주실 수 있을까요?"
        head = {"who":"누가/어떤 사람(주체)","why":"이유/계기","when":"시기/때","how":"방법/과정","where":"장소/배경","what":"무슨 일/내용"}.get(t, "내용")
        return f"{material}에 대해 {head}를 더 자세히 들려주실 수 있을까요?"

@tool
def select_and_generate(metrics_updated: Dict) -> Dict:
    mats = (metrics_updated or {}).get("materials", {}) or {}
    glb  = (metrics_updated or {}).get("global", {}) or {}

    mat_name = _choose_material(metrics_updated)
    if not mat_name:
        return {"next_question": None}

    m = mats.get(mat_name, {})
    t = _choose_type(m)
    if not t:
        remaining = [n for n, mm in mats.items() if int(mm.get("material_count",0))==0 and n != mat_name]
        if not remaining:
            return {"next_question": None}
        mat_name = remaining[0]
        m = mats[mat_name]
        t = _choose_type(m)
        if not t:
            return {"next_question": None}

    keywords = m.get("keywords", [])
    text = _generate_question_llm(mat_name, t, keywords)

    last = glb.get("last_material")
    if last == mat_name:
        glb["last_material_streak"] = int(glb.get("last_material_streak",0)) + 1
    else:
        glb["last_material"] = mat_name
        glb["last_material_streak"] = 1

    return {
        "next_question": {
            "id": f"q-{uuid4().hex[:8]}",
            "material": mat_name,
            "type": t,
            "text": text
        }
    }
