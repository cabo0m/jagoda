"""
Test Day 3 – affect + policy + explanations
Run as: python test_day3.py
"""
import os, yaml
from module01.collector import collect
from module01.features import extract_features
from module01.affect import compute_affect
from module01.policy import choose_policy
from module01.explanations import build_explanation
from module01.schemas import LogRow

with open("config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)
LOG_PATH = CONFIG["logging"]["csv_path"]
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

tests = [
  ("Jagódko, jak Ci mija wieczór?", "neutralne pytanie"),
  ("Jagódko, Ty wiesz, że lubię czarny humor?", "ironia"),
  ("Jesteś idiotą, pacanie!", "obelga"),
  ("Projekt wygląda świetnie, jedziemy dalej!", "projekt"),
]

print("=== START: test_day3 ===")

for txt, desc in tests:
    sig = collect(txt)
    feats = extract_features(sig)
    st = compute_affect(feats)
    dec = choose_policy(st)
    why = "; ".join(build_explanation(feats, st))
    print(f"\n--- {desc} ---")
    print("feats:", feats.to_dict())
    print("state:", st.to_dict())
    print("decision:", dec.to_dict())
    # log
    row = LogRow(
      timestamp_iso=sig.timestamp_iso,
      msg_len=feats.msg_len,
      sentences=feats.sentences,
      tone=feats.tone,
      valence=st.valence,
      arousal=st.arousal,
      dominance=st.dominance,
      like_score=st.like_score,
      policy=dec.policy,
      why=why
    )
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write(LogRow.csv_header() + "\n")
        f.write(row.to_csv() + "\n")

print("\n✅ test_day3 done. Log:", LOG_PATH)
