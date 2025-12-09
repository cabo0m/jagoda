from module01.schemas import AffectState, Decision
import yaml

with open("config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

def choose_policy(state: AffectState) -> Decision:
    th = CONFIG["thresholds"]
    s = state.like_score
    if s < th["like_low"]:
        pol = "Task-Mode"; hint = "krótko, rzeczowo, bez ozdobników"
    elif s < th["like_high"]:
        pol = "Partner-Mode"; hint = "konkret + krótkie uzasadnienia"
    else:
        pol = "Flow-Mode"; hint = "dynamicznie, proponuj kolejny krok"
    return Decision(policy=pol, response_style_hint=hint)

if __name__ == "__main__":
    from module01.schemas import Features
    from module01.affect import compute_affect
    feats = Features(msg_len=20, sentences=1, time_bucket="evening", tone="project")
    st = compute_affect(feats)
    dec = choose_policy(st)
    print(st.to_dict()); print(dec.to_dict())
