"""
Test Day 5 – mood tracker (EMA)
Uruchom: python test_day5.py
Scenariusz:
  1) Dwa komunikaty „projektowe” rozgrzewają nastrój → rośnie like
  2) Później obelga – zobaczysz, że korekta nastroju minimalnie łagodzi spadek
  3) Neutralne pytanie – decyzja na lekko podniesionym nastroju
"""
import os, yaml, time
from module01.respond import run_once

with open("config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)
MOOD_PATH = CONFIG["mood"]["file"]

# Start: wyczyść nastrój (opcjonalnie – jeśli chcesz świeży test)
if os.path.isfile(MOOD_PATH):
    os.remove(MOOD_PATH)
    print(f"(reset) removed mood file: {MOOD_PATH}")

cases = [
    ("Projekt wygląda świetnie, jedziemy dalej!", "Flow boost #1"),
    ("Dobra, plan jest dobry – wdrażamy kolejne kroki.", "Flow boost #2"),
    ("Jesteś idiotą, pacanie!", "obelga po flow"),
    ("Pomożesz mi, bez gadania, krok po kroku?", "neutralne pytanie"),
]

print("=== START: test_day5 ===")
for txt, label in cases:
    print(f"\n--- CASE: {label} ---")
    run_once(txt)
    time.sleep(0.2)  # tylko dla czytelności logu/ISO

print("\n✅ test_day5 done.")
