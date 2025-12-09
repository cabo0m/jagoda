from __future__ import annotations
import math
import yaml
from module01.schemas import Features, AffectState

with open("config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def baseline_valence(feats: Features) -> float:
    v = 0.0
    tone = feats.tone
    if tone == "project":
        v += 0.20  # było 0.15
    elif tone == "neutral":
        v += 0.05
    elif tone == "pytanie":
        v += 0.00
    elif tone in ("irony", "emocja"):
        v += 0.08  # było 0.05
    if tone == "insult":
        v -= 0.80  # było -0.6 (mocniejsza kara)
    if feats.sentences >= 3 and feats.msg_len / feats.sentences > 140:
        v -= 0.1
    return clamp(v, -1.0, 1.0)
    v = 0.0
    tone = feats.tone
    if tone in ("project", "neutral", "pytanie"):
        v += 0.15 if tone == "project" else (0.05 if tone == "neutral" else 0.0)
    if tone in ("irony", "emocja"):
        v += 0.05
    if tone in ("insult",):
        v -= 0.6
    # long chaotic lowers valence slightly
    if feats.sentences >= 3 and feats.msg_len / feats.sentences > 140:
        v -= 0.1
    return clamp(v, -1.0, 1.0)

def baseline_arousal(feats: Features) -> float:
    a = 0.3
    # length raises arousal
    if feats.msg_len > 60: a += 0.1
    if feats.msg_len > 180: a += 0.1
    if feats.tone in ("emocja", "insult", "irony"): a += 0.1
    # time bucket tweak
    tb = feats.time_bucket
    if tb == "evening": a += 0.05
    if tb == "night": a += 0.1
    return clamp(a, 0.0, 1.0)

def baseline_dominance(feats: Features) -> float:
    d = 0.4
    if feats.tone == "project": d += 0.25  # było +0.2
    if feats.tone == "pytanie": d -= 0.05
    if feats.tone == "insult": d -= 0.25   # było -0.2
    if feats.msg_len < 40: d += 0.05
    return clamp(d, 0.0, 1.0)

def context_bonus(feats: Features) -> float:
    # project anchor bonus if keywords hit already baked in tone via features,
    # give a tiny extra
    if feats.tone == "project":
        return 0.15
    return 0.0

def compute_affect(feats: Features) -> AffectState:
    w = CONFIG["weights"]
    v = baseline_valence(feats)
    a = baseline_arousal(feats)
    d = baseline_dominance(feats)
    z = w["w_valence"]*v + w["w_arousal"]*a + w["w_dominance"]*d + w["bias"] + context_bonus(feats)
    like = clamp(sigmoid(z), 0.0, 1.0)

    # (opcjonalnie) twardy bezpiecznik: obelga nie podbija trybu
    if feats.tone == "insult" and like >= CONFIG["thresholds"]["like_low"]:
        like = CONFIG["thresholds"]["like_low"] - 0.01

    why = [f"tone={feats.tone}", f"time_bucket={feats.time_bucket}", f"len={feats.msg_len}"]
    if feats.tone == "project": why.append("project_anchor(+)")
    if feats.tone == "insult": why.append("penalty(insult)")
    return AffectState(valence=round(v, 3), arousal=round(a, 3), dominance=round(d, 3),
                       like_score=round(like, 3), why=why)

if __name__ == "__main__":
    # tiny demo
    demo = Features(msg_len=41, sentences=1, time_bucket="night", tone="irony")
    st = compute_affect(demo)
    print(st.to_dict())
