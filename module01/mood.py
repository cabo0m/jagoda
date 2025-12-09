from __future__ import annotations
import os, json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any
import yaml
from module01.schemas import AffectState, Features

with open("config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

@dataclass
class MoodState:
    ema: float          # [0..1], średnia ruchoma nastroju
    last_ts: str        # ISO
    samples: int        # ile punktów trafiło do EMA

    def to_dict(self) -> Dict[str, Any]:
        return {"ema": self.ema, "last_ts": self.last_ts, "samples": self.samples}

class MoodStore:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def load(self) -> MoodState:
        if not os.path.isfile(self.path):
            return MoodState(ema=0.5, last_ts=datetime.now().isoformat(timespec="seconds"), samples=0)
        with open(self.path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        return MoodState(ema=float(obj.get("ema", 0.5)),
                         last_ts=obj.get("last_ts", datetime.now().isoformat(timespec="seconds")),
                         samples=int(obj.get("samples", 0)))

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
    # Pierwsza próbka: startuj z wartości x
    if samples <= 0:
        return clamp(x, 0.0, 1.0)
    # Klasyczne EMA
    return clamp(alpha * x + (1 - alpha) * prev, 0.0, 1.0)

def apply_mood_adjustment(feats: Features, st: AffectState, mood: MoodState) -> AffectState:
    """
    Koryguje delikatnie like_score i (lekko) valence na podstawie EMA nastroju.
    """
    k_like = float(CONFIG["mood"]["k_like"])
    k_val = float(CONFIG["mood"]["k_valence"])
    # odchylenie od środka
    delta = (mood.ema - 0.5)
    adj_like = clamp(st.like_score + k_like * delta, 0.0, 1.0)
    adj_val = clamp(st.valence + k_val * delta, -1.0, 1.0)
    # zbuduj nowy obiekt (why uzupełnimy w respond/logu)
    return AffectState(
        valence=round(adj_val, 3),
        arousal=st.arousal,
        dominance=st.dominance,
        like_score=round(adj_like, 3),
        why=st.why + [f"mood_ema={round(mood.ema,3)}", f"like_adj={round(adj_like - st.like_score,3)}", f"val_adj={round(adj_val - st.valence,3)}"]
    )

def update_and_persist_mood(store: MoodStore, mood: MoodState, like_score: float) -> MoodState:
    # ew. wygaszanie po bezczynności
    if _should_decay(mood.last_ts, int(CONFIG["mood"]["decay_if_idle_hours"])):
        target = float(CONFIG["mood"]["reset_to"])
        # łagodny krok do środka (tu 50% odchyłki)
        mood.ema = clamp((mood.ema + target) / 2.0, 0.0, 1.0)
    # aktualizacja EMA
    alpha = float(CONFIG["mood"]["alpha"])
    new_ema = ema_update(mood.ema, like_score, alpha, mood.samples)
    new_state = MoodState(ema=new_ema, last_ts=datetime.now().isoformat(timespec="seconds"), samples=mood.samples + 1)
    store.save(new_state)
    return new_state
