from datetime import datetime
import re
from module01.schemas import SignalInput, Features
import yaml

# Ładowanie konfiguracji
with open("config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

def bucket_from_ts(ts_iso: str) -> str:
    """Zwraca nazwę pory dnia."""
    t = datetime.fromisoformat(ts_iso)
    hour = t.hour
    tb = CONFIG["time_bucket"]
    for name, (start, end) in tb.items():
        if start <= hour < end or (start > end and (hour >= start or hour < end)):
            return name
    return "day"

def detect_tone(text: str) -> str:
    """Prosta heurystyka tonu z obsługą fraz typu 'czarny humor' i rdzeni ('ironicz', 'sarkasty')."""
    txt_low = text.lower()
    tones = CONFIG["tone_keywords"]
    for tone, words in tones.items():
        for w in words:
            if w in txt_low:
                return tone
    if "?" in text and "!" in text:
        return "emocja"
    if text.strip().endswith("?"):
        return "pytanie"
    return "neutral"

    """Bardzo prosta heurystyka tonu."""
    txt_low = text.lower()
    tones = CONFIG["tone_keywords"]

    # Kolejność ważna
    for tone, words in tones.items():
        if any(w in txt_low for w in words):
            return tone

    # fallbacki
    if "?" in text and "!" in text:
        return "emocja"
    if text.strip().endswith("?"):
        return "pytanie"
    return "neutral"

def count_sentences(text: str) -> int:
    """Zlicza zdania po prostych separatorach."""
    return max(len(re.findall(r"[.!?]", text)), 1)

def extract_features(signal: SignalInput) -> Features:
    """Konwertuje sygnał wejściowy na zestaw cech."""
    txt = signal.text
    msg_len = len(txt)
    sentences = count_sentences(txt)
    tone = detect_tone(txt)
    time_bucket = bucket_from_ts(signal.timestamp_iso)
    return Features(
        msg_len=msg_len,
        sentences=sentences,
        time_bucket=time_bucket,
        tone=tone
    )

if __name__ == "__main__":
    sig = SignalInput(text="Jagódko, to jest test ironia xd!", timestamp_iso=datetime.now().isoformat(timespec="seconds"))
    feats = extract_features(sig)
    print(feats.to_dict())
