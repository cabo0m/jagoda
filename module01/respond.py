"""
Użycie:
    python -m module01.respond "Treść Twojej wiadomości"
albo:
    python -m module01.respond
"""
import sys, os, yaml
from module01.collector import collect
from module01.features import extract_features
from module01.affect import compute_affect
from module01.policy import choose_policy
from module01.explanations import build_explanation
from module01.style import render_response
from module01.schemas import LogRow
from module01.mood import MoodStore, apply_mood_adjustment, update_and_persist_mood

with open("config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)
LOG_PATH = CONFIG["logging"]["csv_path"]
MOOD_PATH = CONFIG["mood"]["file"]
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
os.makedirs(os.path.dirname(MOOD_PATH), exist_ok=True)

def run_once(user_text: str):
    # pipeline bez nastroju
    sig = collect(user_text)
    feats = extract_features(sig)
    st_raw = compute_affect(feats)

    # wczytaj nastrój, zastosuj korektę, a potem zaktualizuj na podstawie bieżącego like (już skorygowanego)
    mood_store = MoodStore(MOOD_PATH)
    mood_state_before = mood_store.load()
    st_adj = apply_mood_adjustment(feats, st_raw, mood_state_before)

    # decyzja na skorygowanym stanie
    dec = choose_policy(st_adj)

    # Budowa WHY (rozszerzamy o info o nastroju)
    why = "; ".join(build_explanation(feats, st_adj) + [f"policy={dec.policy}"])

    # Na końcu aktualizujemy mood EMA na podstawie użytego like_score (po korekcie)
    mood_state_after = update_and_persist_mood(mood_store, mood_state_before, st_adj.like_score)

    # log
    file_exists = os.path.isfile(LOG_PATH)
    row = LogRow(
        timestamp_iso=sig.timestamp_iso,
        msg_len=feats.msg_len,
        sentences=feats.sentences,
        tone=feats.tone,
        valence=st_adj.valence,
        arousal=st_adj.arousal,
        dominance=st_adj.dominance,
        like_score=st_adj.like_score,
        policy=dec.policy,
        why=why
    )
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write(LogRow.csv_header() + "\n")
        f.write(row.to_csv() + "\n")

    # wydruk
    print("=== INPUT ===")
    print(user_text)
    print("\n=== FEATS ===")
    print(feats.to_dict())
    print("\n=== STATE(raw) ===")
    print(st_raw.to_dict())
    print("\n=== STATE(adjusted by mood) ===")
    print(st_adj.to_dict())
    print("\n=== MOOD ===")
    print({"before": mood_state_before.to_dict(), "after": mood_state_after.to_dict()})
    print("\n=== DECISION ===")
    print(dec.to_dict())
    print("\n=== REPLY ===")
    print(render_response(user_text, feats, st_adj, dec))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:]).strip()
    else:
        text = "Jagódko, projekt idzie dobrze — jedziemy dalej w trybie Flow?"
    run_once(text)
