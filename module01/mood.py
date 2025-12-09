from __future__ import annotations
import os
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any
import yaml
from module01.schemas import AffectState, Features

# wczytanie konfiguracji
with open("config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class MoodState:
    ema: float          # [0..1] średnia ruchoma nastroju
    last_ts: str        # znacznik czasu ISO
    samples: int        # liczba zaktualizowanych próbek

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ema": round(self.ema, 3),
            "last_ts": self.last_ts,
            "samples": self.samples
        }


class MoodStore:
    """Prosty magazyn nastroju (plik JSON)."""

    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def load(self) -> MoodState:
        if not os.path.isfile(self.path):
            return MoodState(
                ema=0.5,
                last_ts=datetime.now().isoformat(timespec="seconds"),
                samples=0
            )
        with open(self.path, "r", encoding="utf-8") as f:
            try:
                obj = json.load(f)
            except json.JSONDecodeError:
                return MoodState(ema=0.5,
                                 last_ts=datetime.now().isoformat(timespec="seconds"),
                                 samples=0)
        return MoodState(
            ema=float(obj.get("ema", 0.5)),
            last_ts=obj.get("last_ts", datetime.now().isoformat(timespec="seconds")),
            samples=int(obj.get("samples", 0))
        )

    def save(self, state: MoodState):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)


def _should_decay(last_iso: str, hours: int) -> bool:
    try:
        last = datetime.fromisoformat(last_iso)
    except Exception:
        return True
    return (datetime.now() - last) >= timedelta(hours=hours)


def ema_update(prev: float, x: float, alpha: float, samples: int) -> float:
    """Klasyczna aktualizacja EMA (exponential moving average)."""
    if samples <= 0:
        return clamp(x, 0.0, 1.0)
    return clamp(alpha * x + (1 - alpha) * prev, 0.0, 1.0)


def apply_mood_adjustment(feats: Features, st: AffectState, mood: MoodState) -> AffectState:
    """
    Delikatnie koryguje like_score i valence na podstawie aktualnego nastroju (EMA).
    """
    k_like = float(CONFIG["mood"]["k_like"])
    k_val = float(CONFIG["mood"]["k_valence"])
    delta = mood.ema - 0.5  # odchylenie od środka (0.5)

    adj_like = clamp(st.like_score + k_like * delta, 0.0, 1.0)
    adj_val = clamp(st.valence + k_val * delta, -1.0, 1.0)

    return AffectState(
        valence=round(adj_val, 3),
        arousal=st.arousal,
        dominance=st.dominance,
        like_score=round(adj_like, 3),
        why=st.why + [
            f"mood_ema={round(mood.ema, 3)}",
            f"like_adj={round(adj_like - st.like_score, 3)}",
            f"val_adj={round(adj_val - st.valence, 3)}"
        ]
    )


def update_and_persist_mood(store: MoodStore, mood: MoodState, like_score: float) -> MoodState:
    """
    Aktualizuje EMA, ewentualnie wykonuje łagodne wygaszanie nastroju po długiej przerwie,
    a następnie zapisuje nowy stan.
    """
    # czy trzeba zredukować emocję po dłuższej przerwie
    if _should_decay(mood.last_ts, int(CONFIG["mood"]["decay_if_idle_hours"])):
        target = float(CONFIG["mood"]["reset_to"])
        mood.ema = clamp((mood.ema + target) / 2.0, 0.0, 1.0)

    alpha = float(CONFIG["mood"]["alpha"])
    new_ema = ema_update(mood.ema, like_score, alpha, mood.samples)
    new_state = MoodState(
        ema=new_ema,
        last_ts=datetime.now().isoformat(timespec="seconds"),
        samples=mood.samples + 1
    )

    store.save(new_state)
    return new_state


if __name__ == "__main__":
    # Krótki test ręczny
    store = MoodStore("data/mood.json")
    mood = store.load()
    print("Before:", mood.to_dict())

    fake_feats = Features(msg_len=40, sentences=1, time_bucket="day", tone="project")
    fake_affect = AffectState(0.2, 0.3, 0.5, 0.6, ["demo"])
    adj = apply_mood_adjustment(fake_feats, fake_affect, mood)
    print("Adjusted:", adj.to_dict())

    mood2 = update_and_persist_mood(store, mood, adj.like_score)
    print("After:", mood2.to_dict())
