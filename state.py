from dataclasses import dataclass

@dataclass
class GameState:
    white: int
    black: int
    side: str            # 'w' or 'b'
    en_passant: int | None