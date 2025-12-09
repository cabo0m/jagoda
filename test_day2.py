"""
Test Day 2 – Jagoda Mini
Sprawdza collector, features i logowanie.
Uruchamiaj z katalogu głównego repo:
    python test_day2.py
"""

import os
from datetime import datetime
from module01.collector import collect
from module01.features import extract_features
from module01.schemas import LogRow
import yaml

# ======== konfiguracja ========
with open("config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

LOG_PATH = CONFIG["logging"]["csv_path"]
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# ======== funkcje pomocnicze ========

def log_result(sig, feats, extra="manual-test"):
    """Tworzy LogRow i dopisuje do pliku CSV."""
    row = LogRow(
        timestamp_iso=sig.timestamp_iso,
        msg_len=feats.msg_len,
        sentences=feats.sentences,
        tone=feats.tone,
        valence=0.0,
        arousal=0.0,
        dominance=0.0,
        like_score=0.0,
        policy="N/A",
        why=extra,
    )
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write(LogRow.csv_header() + "\n")
        f.write(row.to_csv() + "\n")
    return row

def show(feats, label):
    print(f"\n=== {label} ===")
    print(f"Tekst: {feats}")
    print(f"msg_len={feats.msg_len}, sentences={feats.sentences}, "
          f"tone={feats.tone}, time_bucket={feats.time_bucket}")

# ======== scenariusze testowe ========

tests = [
    ("Jagódko, jak Ci mija wieczór?", "neutralne pytanie"),
    ("Jagódko, Ty wiesz, że lubię czarny humor?", "ironia"),
    ("Jesteś idiotą, pacanie!", "obelga"),
    ("Projekt wygląda świetnie, jedziemy dalej!", "projekt"),
]

print("=== START: test_day2 ===")

for txt, desc in tests:
    sig = collect(txt)
    feats = extract_features(sig)
    show(feats, desc)
    log_result(sig, feats, extra=desc)

print("\n=== Podsumowanie ===")
print(f"Sprawdź plik logu: {LOG_PATH}")

if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()[-len(tests):]
        for l in lines:
            print("LOG:", l.strip())

print("\n✅ Testy Dnia 2 zakończone.\n")
