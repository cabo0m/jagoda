from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class SignalInput:
    text: str
    timestamp_iso: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Features:
    msg_len: int
    sentences: int
    time_bucket: str  # "morning","day","evening","night"
    tone: str         # e.g., "ironia","projekt","obelga","neutral"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AffectState:
    valence: float     # -1..1
    arousal: float     # 0..1
    dominance: float   # 0..1
    like_score: float  # 0..1
    why: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Decision:
    policy: str        # "Task-Mode" | "Partner-Mode" | "Flow-Mode"
    response_style_hint: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class LogRow:
    timestamp_iso: str
    msg_len: int
    sentences: int
    tone: str
    valence: float
    arousal: float
    dominance: float
    like_score: float
    policy: str
    why: str

    def csv_header() -> str:
        return ("timestamp;msg_len;sentences;tone;valence;arousal;"
                "dominance;like_score;policy;why")

    def to_csv(self) -> str:
        return (f"{self.timestamp_iso};{self.msg_len};{self.sentences};"
                f"{self.tone};{self.valence:.2f};{self.arousal:.2f};"
                f"{self.dominance:.2f};{self.like_score:.2f};"
                f"{self.policy};{self.why}")

__all__ = [
    "SignalInput",
    "Features",
    "AffectState",
    "Decision",
    "LogRow",
]
