from source_code_files.game.state import GameState

from source_code_files.game.moves import generate_moves


def apply_move(state: GameState, move):

    from_sq, to_sq = move

    from_mask = 1 << from_sq
    to_mask = 1 << to_sq

    white = state.white
    black = state.black
    en_passant = None  # reset every move
    if state.side == 'w':
        assert (white & from_mask) != 0, "White tried to move non-white piece"
    else:
        # print("DEBUG APPLY MOVE")
        # print("Move:", move)
        # print("Black bitboard:", bin(state.black))
        # print("From square bit:", bin(from_mask))

        assert (black & from_mask) != 0, "Black tried to move non-black piece"

    # --------------------------------
    # WHITE MOVE
    # --------------------------------
    if state.side == 'w':
        white &= ~from_mask

        # Normal capture
        if to_mask & black:
            black &= ~to_mask

        # En passant capture
        elif state.en_passant is not None and to_sq == state.en_passant:
            captured_sq = to_sq - 8
            assert (1 << captured_sq) & black, "Illegal en passant by white"
            black &= ~(1 << captured_sq)

        white |= to_mask

        # Double push enables en passant
        if to_sq - from_sq == 16:
            en_passant = from_sq + 8

        next_side = 'b'

    # --------------------------------
    # BLACK MOVE
    # --------------------------------
    else:
        black &= ~from_mask

        # Normal capture
        if to_mask & white:
            white &= ~to_mask

        # En passant capture
        elif state.en_passant is not None and to_sq == state.en_passant:
            captured_sq = to_sq + 8
            assert (1 << captured_sq) & white, "Illegal en passant by black"
            white &= ~(1 << captured_sq)

        black |= to_mask

        # Double push enables en passant
        if from_sq - to_sq == 16:
            en_passant = from_sq - 8

        next_side = 'w'

    assert (white & black) == 0, "Overlap between white and black bitboards"

    # if state.side == 'w':
    #     print("AFTER WHITE MOVE")
    # else:
    #     print("AFTER BLACK MOVE")

    # print("White:", bin(white))
    # print("Black:", bin(black))

    return GameState(
        white=white,
        black=black,
        side=next_side,
        en_passant=en_passant
    )
