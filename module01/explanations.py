from typing import List
from module01.schemas import Features, AffectState

def build_explanation(feats: Features, state: AffectState) -> List[str]:
    why = list(state.why)
    why.append(f"valence={state.valence}")
    why.append(f"arousal={state.arousal}")
    why.append(f"dominance={state.dominance}")
    why.append(f"like={state.like_score}")
    return why

if __name__ == "__main__":
    from module01.schemas import Features
    from module01.affect import compute_affect
    f = Features(msg_len=50, sentences=2, time_bucket="evening", tone="irony")
    s = compute_affect(f)
    print(build_explanation(f, s))

