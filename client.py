import argparse
import socket

from game.state import GameState
from game.apply_move import apply_move
from game.terminal import is_terminal
from agents.alphabeta_agent import AlphaBetaAgent


def send_msg(sock, msg):
    sock.sendall((msg + "\n").encode())
    print(f">>> {msg}")


def recv_msg(sock):
    buf = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            raise ConnectionError("Server closed connection")
        if ch == b"\n":
            break
        buf += ch
    msg = buf.decode().strip()
    print(f"<<< {msg}")
    return msg


def recv_game_msg(sock):
    """
    Tournament-safe:
    - ignores TournamentAccepted
    - when Reset arrives: sends Ready AND RETURNS "Reset" so caller can reset local state
    """
    while True:
        msg = recv_msg(sock)
        if msg.startswith("TournamentAccepted"):
            continue
        if msg == "Reset":
            send_msg(sock, "Ready")
            return "Reset"
        return msg


def setup_to_state(msg):
    tokens = msg.split()[1:]
    white = 0
    black = 0

    for t in tokens:
        color = t[0]
        file = ord(t[1]) - ord('a')
        rank = int(t[2]) - 1
        sq = rank * 8 + file
        if color == 'W':
            white |= 1 << sq
        else:
            black |= 1 << sq

    return GameState(white=white, black=black, side='w', en_passant=None)


def alg_to_sq(a):
    return (int(a[1]) - 1) * 8 + (ord(a[0]) - ord('a'))


def sq_to_alg(sq):
    return f"{chr(ord('a') + sq % 8)}{sq // 8 + 1}"


def clone_state(s: GameState) -> GameState:
    return GameState(white=s.white, black=s.black, side=s.side, en_passant=s.en_passant)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--net", nargs=2, metavar=("HOST", "PORT"),
                        required=True, help="host port")

    parser.add_argument("--side", choices=["w", "b"],
                        required=True, help="w or b")

    args = parser.parse_args()

    args.host = args.net[0]
    args.port = int(args.net[1])
    my_color = args.side

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.host, args.port))
    print("[connected]")

    agent = AlphaBetaAgent(depth=4)

    # ── Initial handshake
    send_msg(sock, "OK")

    setup_msg = recv_msg(sock)          # Setup ...
    initial_state = setup_to_state(setup_msg)
    send_msg(sock, "OK")

    time_msg = recv_msg(sock)           # Time N
    total_minutes = float(time_msg.split()[1])
    send_msg(sock, "OK")

    # We reset these at every round start (after Reset)
    state = clone_state(initial_state)
    last_move = None

    # Start the first round clock
    agent.start_game(total_minutes)

    # ───────────────── TOURNAMENT LOOP ─────────────────
    while True:
        msg = recv_game_msg(sock)

        # Handle Reset between rounds (MOST IMPORTANT FIX)
        if msg == "Reset":
            state = clone_state(initial_state)
            last_move = None
            agent.start_game(total_minutes)  # new round gets a fresh clock
            continue

        # Some servers may resend Setup/Time between rounds (support it safely)
        if msg.startswith("Setup"):
            initial_state = setup_to_state(msg)
            state = clone_state(initial_state)
            last_move = None
            send_msg(sock, "OK")

            msg2 = recv_msg(sock)  # expect Time ...
            if not msg2.startswith("Time"):
                raise RuntimeError(f"Expected Time, got {msg2}")
            total_minutes = float(msg2.split()[1])
            send_msg(sock, "OK")

            agent.start_game(total_minutes)
            continue

        # End conditions
        if msg == "exit":
            break
        if msg.startswith("GameOver"):
            # Don't exit tournament; server will send Reset next
            continue

        # Round start:
        # - "Begin" means we are WHITE and must move now
        # - otherwise it's opponent's first move, and then it's our turn
        if msg == "Begin":
            my_color = args.side
            state.side = 'w'
            my_turn = True
        else:
            my_color = args.side
            state.side = 'w'
            frm = alg_to_sq(msg[:2])
            to = alg_to_sq(msg[2:])
            state = apply_move(state, (frm, to))
            last_move = (frm, to)
            my_turn = True

        # ─────────────── SINGLE GAME LOOP ───────────────
        while True:
            if my_turn:
                move = agent.choose_move(state, last_move)
                if move is None:
                    send_msg(sock, "exit")   # resignation
                    break

                send_msg(sock, sq_to_alg(move[0]) + sq_to_alg(move[1]))
                state = apply_move(state, move)
                last_move = move
                my_turn = False
            else:
                msg = recv_game_msg(sock)

                if msg == "Reset":
                    # round ended; reset and go to outer loop
                    state = clone_state(initial_state)
                    state.side = 'w'
                    last_move = None
                    agent.start_game(total_minutes)
                    break

                if msg.startswith("GameOver"):
                    # wait for Reset next (handled above)
                    continue

                if msg == "Begin":
                    my_turn = True
                    continue

                if msg == "exit":
                    return

                frm = alg_to_sq(msg[:2])
                to = alg_to_sq(msg[2:])
                state = apply_move(state, (frm, to))
                last_move = (frm, to)
                my_turn = True

    sock.close()
    print("[done]")


if __name__ == "__main__":
    main()
