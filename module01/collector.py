from datetime import datetime
from module01.schemas import SignalInput

def collect(raw_text: str) -> SignalInput:
    """Przyjmuje surowy tekst i zwraca SignalInput z aktualnym timestampem ISO."""
    now = datetime.now().isoformat(timespec="seconds")
    return SignalInput(text=raw_text.strip(), timestamp_iso=now)

def collect_with_time(raw_text: str, ts: datetime) -> SignalInput:
    """Alternatywa, gdy chcemy ręcznie podać czas."""
    return SignalInput(text=raw_text.strip(), timestamp_iso=ts.isoformat(timespec="seconds"))

if __name__ == "__main__":
    demo = collect("Jagódko, testujemy kolektor.")
    print(demo.to_dict())
