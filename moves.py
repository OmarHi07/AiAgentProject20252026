from source_code_files.game.state import GameState

# Masks to prevent wrap-around on files
NOT_A_FILE = ~0x0101010101010101 & ((1 << 64) - 1)
NOT_H_FILE = ~0x8080808080808080 & ((1 << 64) - 1)
FULL_BOARD = (1 << 64) - 1


def iter_bits(bb):
    while bb:
        lsb = bb & -bb
        yield lsb.bit_length() - 1
        bb &= bb - 1


def sanity_check_move(f, t):
    df = abs((f % 8) - (t % 8))
    dr = abs((f // 8) - (t // 8))
    assert dr in (1, 2), f"illegal rank diff {f}->{t}"
    assert df <= 1, f"illegal file diff {f}->{t}"


def generate_white_moves(state: GameState):
    moves = []

    white = state.white
    black = state.black
    empty = ~(white | black) & FULL_BOARD

    # ---------- single push ----------
    single = (white << 8) & empty
    for to_sq in iter_bits(single):
        from_sq = to_sq - 8
        moves.append((from_sq, to_sq))

    # ---------- double push ----------
    rank2 = white & 0x000000000000FF00
    double = ((rank2 << 8) & empty) << 8 & empty
    for to_sq in iter_bits(double):
        from_sq = to_sq - 16
        moves.append((from_sq, to_sq))

    # ---------- captures ----------
    diag_left = ((white & NOT_A_FILE) << 7) & (black)
    diag_right = ((white & NOT_H_FILE) << 9) & (black)

    for to_sq in iter_bits(diag_left):
        moves.append((to_sq - 7, to_sq))

    for to_sq in iter_bits(diag_right):
        moves.append((to_sq - 9, to_sq))

    # ---------- en passant ----------
    if state.en_passant is not None:
        ep = state.en_passant
        ep_rank = ep // 8
        if ep_rank == 5:
            for delta in (7, 9):
                from_sq = ep - delta
                if 0 <= from_sq < 64 and (white >> from_sq) & 1:
                    # verify diagonal
                    if abs((from_sq % 8) - (ep % 8)) == 1:
                        moves.append((from_sq, ep))

    return moves


def generate_black_moves(state: GameState):
    moves = []

    black = state.black
    white = state.white
    empty = ~(black | white) & FULL_BOARD

    # ---------- 1) Single forward push ----------
    single = (black >> 8) & empty
    bb = single
    while bb:
        to_sq = (bb & -bb).bit_length() - 1
        from_sq = to_sq + 8
        moves.append((from_sq, to_sq))
        bb &= bb - 1

    # ---------- 2) Double forward push (from rank 7) ----------
    rank7 = black & 0x00FF000000000000  # black pawns on rank 7
    double = ((rank7 >> 8) & empty) >> 8 & empty
    bb = double
    while bb:
        to_sq = (bb & -bb).bit_length() - 1
        from_sq = to_sq + 16
        moves.append((from_sq, to_sq))
        bb &= bb - 1

    # ---------- 3) Diagonal captures ----------
    diag_right = ((black & NOT_H_FILE) >> 7) & (white)
    diag_left = ((black & NOT_A_FILE) >> 9) & (white)

    for to_sq in iter_bits(diag_right):
        moves.append((to_sq + 7, to_sq))

    for to_sq in iter_bits(diag_left):
        moves.append((to_sq + 9, to_sq))

    # ---------- 4) En passant ----------
    if state.en_passant is not None:
        ep = state.en_passant
        ep_rank = ep // 8

        # Black can capture en passant only on rank 3
        if ep_rank == 2:
            for delta in (7, 9):
                from_sq = ep + delta
                if 0 <= from_sq < 64 and ((black >> from_sq) & 1):
                    # must be exactly one file away
                    if abs((from_sq % 8) - (ep % 8)) == 1:
                        moves.append((from_sq, ep))

    return moves


def generate_moves(state: GameState):
    moves = generate_white_moves(state) if state.side == 'w' else generate_black_moves(state)

    DEBUG = False
    # --- SANITY CHECK (DEBUG ONLY) ---
    if DEBUG:
        for f, t in moves:
            sanity_check_move(f, t)

    return moves


