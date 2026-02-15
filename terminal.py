def is_terminal(state):
    if state.white == 0 or state.black == 0:
        return True

    if state.white & 0xFF00000000000000:
        return True

    if state.black & 0x00000000000000FF:
        return True

    return False