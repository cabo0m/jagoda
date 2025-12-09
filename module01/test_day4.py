"""
Test Day 4 – renderowanie odpowiedzi w trzech trybach.
Uruchom: python test_day4.py
"""
from module01.respond import run_once

cases = [
    ("Pomożesz mi, bez gadania, krok po kroku?", "Partner-Mode (pytanie)"),
    ("Jesteś idiotą, pacanie!", "Task-Mode (obelga)"),
    ("Projekt wygląda świetnie, jedziemy dalej!", "Flow-Mode (projekt)"),
]

print("=== START: test_day4 ===")

for txt, label in cases:
    print(f"\n--- CASE: {label} ---")
    run_once(txt)

print("\n✅ test_day4 done.")
