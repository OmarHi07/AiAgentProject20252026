import time

from game.state import GameState
from game.apply_move import apply_move
from game.moves import generate_moves
from game.terminal import is_terminal
from agents.alphabeta_agent import AlphaBetaAgent

# ANSI colors
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
BRIGHT = "\033[1m"
BG_GREEN = "\033[42m"


# ─────────────────────────────────────────────
# Algebraic helpers
# ─────────────────────────────────────────────

def alg_to_sq(a):
    return (int(a[1]) - 1) * 8 + (ord(a[0]) - ord('a'))


def sq_to_alg(sq):
    return f"{chr(ord('a') + sq % 8)}{sq // 8 + 1}"


# ─────────────────────────────────────────────
# ASCII board
# ─────────────────────────────────────────────

def print_board(state, last_move=None, highlight_targets=None,
                capture_targets=None, human_time=None, agent_time=None):


    """
    last_move: (from_sq, to_sq) or None
    highlight_targets: set of squares (to_sq) to mark as legal moves
    """
    highlight_targets = highlight_targets or set()
    capture_targets = capture_targets or set()


    prev_from = None
    prev_color = None
    if last_move:
        prev_from, _ = last_move
        prev_color = GREEN if state.side == 'b' else RED
        # הסבר: אם עכשיו BLACK בתור → WHITE זז קודם → ירוק

    print("\n    a  b  c  d  e  f  g  h")
    for r in range(7, -1, -1):
        row = f" {r+1} "
        for f in range(8):
            sq = r * 8 + f
            mask = 1 << sq

            # --- white pawn ---
            if state.white & mask:
                if sq in capture_targets:
                    cell = BG_GREEN + GREEN + BRIGHT + " w" + RESET
                else:
                    cell = GREEN + " w" + RESET

            # --- black pawn ---
            elif state.black & mask:
                if sq in capture_targets:
                    cell = BG_GREEN + RED + BRIGHT + " b" + RESET
                else:
                    cell = RED + " b" + RESET

            # --- empty legal target ---
            elif sq in highlight_targets:
                cell = GREEN + BRIGHT + " ■" + RESET

            # --- previous square ---
            elif prev_from == sq:
                cell = prev_color + " ." + RESET

            # --- empty ---
            else:
                cell = " ."

            row += cell + " "
        print(row)
    print("    a  b  c  d  e  f  g  h")
    print(f"\nSide to move: {BRIGHT}{'WHITE' if state.side == 'w' else 'BLACK'}{RESET}\n")
    print(f"White pawns: {bin(state.white).count('1')} | "
          f"Black pawns: {bin(state.black).count('1')}")
    if human_time is not None and agent_time is not None:
        print(f"\nHuman time: {round(human_time,2)} sec | "
              f"Agent time: {round(agent_time,2)} sec")


# ─────────────────────────────────────────────
# Setup parsing
# ─────────────────────────────────────────────

DEFAULT_SETUP = (
    "Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2 "
    "Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7"
)


def setup_to_state(setup_str):
    white = 0
    black = 0

    for t in setup_str.split():
        color = t[0]
        file = ord(t[1]) - ord('a')
        rank = int(t[2]) - 1
        sq = rank * 8 + file
        if color == 'W':
            white |= 1 << sq
        else:
            black |= 1 << sq

    return GameState(
        white=white,
        black=black,
        side='w',
        en_passant=None
    )


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("=== Human vs AlphaBetaAgent (LOCAL DEMO) ===\n")

    # ── Time control
    try:
        total_minutes = float(input("Enter total game time (minutes): ").strip())
        total_seconds = total_minutes * 60

        human_time = total_seconds / 2
        agent_time = total_seconds / 2


    except:

        total_seconds = 5.0 * 60

        human_time = total_seconds / 2

        agent_time = total_seconds / 2

    # ── Setup
    setup = input("Enter SETUP (or press Enter for default): ").strip()
    if not setup:
        setup = DEFAULT_SETUP

    state = setup_to_state(setup)

    # ── Agent
    agent = AlphaBetaAgent(depth=4)


    human_side = 'w'
    agent_side = 'b'

    print("\nGame started.\n")

    last_move = None
    while True:


        # ─────────────────────────────────────
        # HUMAN TURN (always waits)
        # ─────────────────────────────────────
        turn_start = time.time()
        if state.side == human_side:

            moves = generate_moves(state)
            legal = {(f, t): sq_to_alg(f) + sq_to_alg(t) for f, t in moves}
            targets = set()
            capture_targets = set()

            enemy = state.black if state.side == 'w' else state.white

            for f, t in moves:
                targets.add(t)
                if enemy & (1 << t):
                    capture_targets.add(t)

            print_board(state, last_move,
                        highlight_targets=targets,
                        capture_targets=capture_targets,
                        human_time=human_time,
                        agent_time=agent_time)

            print("Legal moves:")
            print(", ".join(sorted(legal.values())))

            while True:
                user = input("\nYour move (e2e4 / exit): ").strip()
                if user == "exit":
                    print("You resigned.")
                    return

                for (f, t), s in legal.items():
                    if s == user:
                        last_move = (f, t)
                        state = apply_move(state, last_move)
                        elapsed = time.time() - turn_start
                        human_time -= elapsed

                        if human_time <= 0:
                            print("\n⏰ HUMAN TIME OUT!")
                            print("Winner: BLACK 🔴")
                            return

                        if is_terminal(state):
                            print_board(state, last_move)
                            print("\n=== GAME OVER ===")
                            print("Winner: WHITE 🟢")
                            return

                        break
                else:
                    print("Invalid move, try again.")
                    continue
                break

        # ─────────────────────────────────────
        # AGENT TURN
        # ─────────────────────────────────────
        else:
            print_board(state, last_move,
                        human_time=human_time,
                        agent_time=agent_time)



            agent.set_time_left(agent_time)
            move = agent.choose_move(state)
            agent_time = agent.get_time_left()

            if move is None:
                print("Agent resigns / timeout.")
                break

            print(f"Agent plays: {sq_to_alg(move[0])}{sq_to_alg(move[1])}")
            last_move = move
            state = apply_move(state, move)

            if agent_time <= 0:
                print("\n⏰ AGENT TIME OUT!")
                print("Winner: WHITE 🟢")
                return

            if is_terminal(state):
                print_board(state, last_move)
                print("\n=== GAME OVER ===")
                print("Winner: BLACK 🔴")
                return


if __name__ == "__main__":
    main()
