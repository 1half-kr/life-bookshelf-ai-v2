from promptflow.core import tool
from typing import Dict, List

TYPE2W = {"when":"w1","how":"w2","who":"w3","what":"w4","where":"w5","why":"w6"}
W_KEYS = ["w1","w2","w3","w4","w5","w6"]

def _ensure_material(mats: Dict, name: str):
    m = mats.setdefault(name, {})
    m.setdefault("category_name", "")
    m.setdefault("chunk_name", "")
    for w in W_KEYS: m.setdefault(w, 0)
    m.setdefault("ex", 0)
    m.setdefault("con", 0)
    m.setdefault("utter_freq", 0)
    m.setdefault("material_count", 0)
    m.setdefault("themes", [])
    m.setdefault("keywords", [])
    return m

def _ensure_chunk(chunks: Dict, cat: str, chk: str):
    ck = f"{cat}::{chk}"
    c = chunks.setdefault(ck, {"category_name": cat, "chunk_name": chk, "chunk_weight": 0})
    return ck, c

def _initialize_theme(metrics: Dict, mats: Dict, chunks: Dict, glb: Dict):
    theme = metrics.get("theme")
    if not theme:
        return
    for mname, ment in mats.items():
        cat, chk = ment.get("category_name",""), ment.get("chunk_name","")
        if not cat or not chk:
            continue
        _, c = _ensure_chunk(chunks, cat, chk)
        if theme in (ment.get("themes") or []):
            c["chunk_weight"] = max(c.get("chunk_weight",0), 10)
    glb["theme_initialized"] = True

def _update_material(m: Dict, axes_ev: Dict, ex_flag: int, con_flag: int, chunks: Dict, keywords: List[str]):
    m["utter_freq"] = int(m.get("utter_freq", 0)) + 1
    for typ, wkey in TYPE2W.items():
        if axes_ev.get(typ, False):
            m[wkey] = 1
    m["ex"] = 1 if (m.get("ex",0) or ex_flag) else 0
    m["con"] = 1 if (m.get("con",0) or con_flag) else 0
    
    existing_kws = m.get("keywords", [])
    for kw in keywords:
        if kw and kw not in existing_kws:
            existing_kws.append(kw)
    m["keywords"] = existing_kws[:5]
    
    _, c = _ensure_chunk(chunks, m.get("category_name",""), m.get("chunk_name",""))
    c["chunk_weight"] = int(c.get("chunk_weight", 0)) + 1
    s6 = sum(int(m.get(w,0)) for w in W_KEYS)
    m["material_count"] = 1 if (s6 >= 3 and m["ex"] == 1 and m["con"] == 1) else m.get("material_count",0)

def _collect_missing_cells(mats: Dict) -> List[Dict]:
    missing_cells = []
    for mname, m in mats.items():
        for typ, wkey in TYPE2W.items():
            if int(m.get(wkey, 0)) == 0:
                missing_cells.append({"material": mname, "type": typ})
        if int(m.get("ex",0)) == 0:
            missing_cells.append({"material": mname, "type": "ex"})
        if int(m.get("con",0)) == 0:
            missing_cells.append({"material": mname, "type": "con"})
    return missing_cells

@tool
def update_metrics(parsed: Dict, metrics: Dict) -> Dict:
    metrics = (metrics or {}).copy()
    mats: Dict = metrics.setdefault("materials", {})
    chunks: Dict = metrics.setdefault("chunks", {})
    glb: Dict = metrics.setdefault("global", {})

    if not glb.get("theme_initialized"):
        _initialize_theme(metrics, mats, chunks, glb)

    hits: List[str] = (parsed or {}).get("material_hits", []) or []
    axes_ev: Dict = (parsed or {}).get("axes_evidence", {}) or {}
    ex_flag: int  = int((parsed or {}).get("ex_flag", 0))
    con_flag: int = int((parsed or {}).get("con_flag", 0))
    keywords: List[str] = (parsed or {}).get("keywords", []) or []

    for mname in hits:
        m = _ensure_material(mats, mname)
        _update_material(m, axes_ev, ex_flag, con_flag, chunks, keywords)

    missing_cells = _collect_missing_cells(mats)
    return {"metrics_updated": metrics, "missing_cells": missing_cells}
