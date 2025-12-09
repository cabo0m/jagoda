from module01.schemas import AffectState, Decision, Features

def _task_template(user_text: str, st: AffectState, feats: Features) -> str:
    # krótko, rzeczowo
    return (
        "OK. Konkret:\n"
        f"- tryb: Task-Mode\n"
        f"- wnioski: val={st.valence}, aro={st.arousal}, dom={st.dominance}, like={st.like_score}\n"
        f"- ton: {feats.tone}, pora: {feats.time_bucket}\n\n"
        "Dalszy krok: podaj jedną precyzyjną rzecz do zrobienia."
    )

def _partner_template(user_text: str, st: AffectState, feats: Features) -> str:
    # konkret + krótkie uzasadnienia
    return (
        "Jasne. Propozycja:\n"
        f"1) Interpretacja: ton={feats.tone}, pora={feats.time_bucket}\n"
        f"2) Stan: val={st.valence}, aro={st.arousal}, dom={st.dominance}, like={st.like_score}\n"
        "3) Ruch: przygotuję następny mikro-krok i jeden wariant alternatywny.\n\n"
        "Mikro-krok: uruchomić ‘affect→policy’ na Twojej realnej wiadomości i zalogować wynik.\n"
        "Alternatywa: dopisać dodatkowe słowa-klucze tonu, jeśli czegoś nie łapie."
    )

def _flow_template(user_text: str, st: AffectState, feats: Features) -> str:
    # dynamicznie, proponuj kolejny krok
    return (
        "Lecimy w rytmie Flow-Mode.\n"
        f"- Ustawienia: ton={feats.tone}, pora={feats.time_bucket}\n"
        f"- VAD: ({st.valence}, {st.arousal}, {st.dominance}), like={st.like_score}\n\n"
        "Proponuję od razu wdrożyć ‘respond.py’ i dodać automatyczne logowanie z pełnym WHY.\n"
        "Kolejny ruch: zawołaj `python -m module01.respond \"Twoja wiadomość\"`."
    )

def render_response(user_text: str, feats: Features, st: AffectState, dec: Decision) -> str:
    if dec.policy == "Task-Mode":
        return _task_template(user_text, st, feats)
    if dec.policy == "Partner-Mode":
        return _partner_template(user_text, st, feats)
    return _flow_template(user_text, st, feats)
