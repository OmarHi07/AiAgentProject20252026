from source_code_files.game.moves import generate_white_moves, generate_black_moves
from source_code_files.game.terminal import is_terminal


# -------------------------
# Weights (fixed)
# -------------------------
W_MATERIAL   = 100
W_ADVANCE    = 10
W_MOBILITY   = 5
W_PASSED     = 30
W_THREAT     = 20

def pawn_advancement(state):
    value = 0

    # white pawns
    bb = state.white
    while bb:
        sq = (bb & -bb).bit_length() - 1
        row = sq // 8
        value += row
        bb &= bb - 1

    # black pawns
    bb = state.black
    while bb:
        sq = (bb & -bb).bit_length() - 1
        row = sq // 8
        value -= (7 - row)
        bb &= bb - 1

    return value

def count_passed_white(state):
    count = 0
    bb = state.white
    while bb:
        sq = (bb & -bb).bit_length() - 1
        file = sq % 8
        rank = sq // 8

        mask = 0
        for r in range(rank + 1, 8):
            for df in (-1, 0, 1):
                f = file + df
                if 0 <= f < 8:
                    mask |= 1 << (r * 8 + f)

        if (mask & state.black) == 0:
            count += 1
        bb &= bb - 1
    return count


def count_passed_black(state):
    count = 0
    bb = state.black
    while bb:
        sq = (bb & -bb).bit_length() - 1
        file = sq % 8
        rank = sq // 8

        mask = 0
        for r in range(rank - 1, -1, -1):
            for df in (-1, 0, 1):
                f = file + df
                if 0 <= f < 8:
                    mask |= 1 << (r * 8 + f)

        if (mask & state.white) == 0:
            count += 1
        bb &= bb - 1
    return count


def threat_score(state):
    white_caps = 0
    black_caps = 0

    for _, to_sq in generate_white_moves(state):
        if (1 << to_sq) & state.black:
            white_caps += 1

    for _, to_sq in generate_black_moves(state):
        if (1 << to_sq) & state.white:
            black_caps += 1

    return white_caps - black_caps


def evaluate(state):
    """
    Evaluation function.
    Positive score = good for White
    Negative score = good for Black
    """

    # Terminal positions
    if is_terminal(state):
        # win / loss
        if state.white == 0:
            return -10_000
        if state.black == 0:
            return 10_000

        # promotion
        if state.white & 0xFF00000000000000:
            return 10_000
        if state.black & 0x00000000000000FF:
            return -10_000

    score = 0

    # -------------------------
    # 1) Material
    # -------------------------
    white_pawns = state.white.bit_count()
    black_pawns = state.black.bit_count()
    score += W_MATERIAL * (white_pawns - black_pawns)

    # -------------------------
    # 2) Advancement
    # -------------------------
    score += W_ADVANCE * pawn_advancement(state)

    # -------------------------
    # 3) Mobility
    # -------------------------
    white_moves = len(generate_white_moves(state))
    black_moves = len(generate_black_moves(state))
    score += W_MOBILITY * (white_moves - black_moves)

    # -------------------------
    # 4) Passed pawns
    # -------------------------
    score += W_PASSED * (count_passed_white(state) - count_passed_black(state))

    # -------------------------
    # 5) Immediate threats
    # -------------------------
    score += W_THREAT * threat_score(state)

    return score
