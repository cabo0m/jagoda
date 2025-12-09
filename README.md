# Jagoda Mini – Moduł 01 (MVP)

Minimalny prototyp: z tekstu + czasu wylicza stan afektywny (VAD), `like_score` i dobiera profil odpowiedzi.

## Struktura
jagoda/
├─ data/
│ └─ logs/
├─ module01/
│ └─ schemas.py
├─ config.yaml
└─ evaluate.md
## Dzień 1 – co jest gotowe
- `schemas.py` – definicje typów danych (sygnały, cechy, stan afektywny, decyzja, log).
- `config.yaml` – progi, wagi, słowa-klucze tonu, ścieżka logu.
- `evaluate.md` – szablon checklisty testowej.

## Jak używać (demo w Pythonie)
from module01.schemas import SignalInput, Features, AffectState

s = SignalInput(text="Jagódko, odpal Dzień 1", timestamp_iso="2025-12-09T02:30:00")
print(s.to_dict())
## Konwencje
- zakresy: `valence ∈ [-1,1]`, `arousal, dominance, like_score ∈ [0,1]`
- trzy profile stylu: Task-Mode, Partner-Mode, Flow-Mode
- log CSV: `timestamp;msg_len;sentences;tone;valence;arousal;dominance;like_score;policy;why`

## Następne kroki (Dzień 2+)
- `collector.py` (zbieranie sygnałów)
- `features.py` (cechy: ton, długość, pora)
- `affect.py` (VAD + like_score)
- `policy.py` (mapowanie stanu na styl)
