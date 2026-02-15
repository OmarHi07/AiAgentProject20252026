# agents/alphabeta_agent.py
WINDOW = 50
INF = 10**9

from source_code_files.game.moves import generate_moves
from source_code_files.game.apply_move import apply_move
from source_code_files.game.terminal import is_terminal
from source_code_files.game.evaluation import evaluate
import time

MAX_QDEPTH = 8

def pos_key(state):
    return (state.white, state.black, state.side, state.en_passant)


def is_capture(state, move):
    _, to_sq = move
    to_mask = 1 << to_sq
    if state.side == 'w':
        return (to_mask & state.black) != 0 or (state.en_passant is not None and to_sq == state.en_passant)
    else:
        return (to_mask & state.white) != 0 or (state.en_passant is not None and to_sq == state.en_passant)


def immediate_recapture_possible(next_state, target_sq):
    target_mask = 1 << target_sq
    for _, to_sq in generate_moves(next_state):
        if (1 << to_sq) & target_mask:
            return True
    return False

def capture_moves_only(state):
    moves = generate_moves(state)
    caps = []
    for m in moves:
        if is_capture(state, m):
            caps.append(m)
    return caps



class AlphaBetaAgent:
    def __init__(self, depth=3):
        self.nodes = 0
        self.last_completed_depth = 0

        self.qnodes = 0
        self.max_qdepth_reached = 0

        self.depth = depth

        # total game clock (set once from server "Time N")
        self.game_start = None
        self.game_time_limit_sec = None  # FIXED

        self._agent_time_left = None   # seconds
        self._agent_running_since = None  # timestamp when agent clock resumed


        self.tt_best = {}
        self.counter_move = {}
        self.killers = {}
        self.history = {}

    def set_time_left(self, seconds: float):
        self._agent_time_left = max(0.0, float(seconds))
        self._agent_running_since = None

    def get_time_left(self) -> float:
        return float(self._agent_time_left or 0.0)


    # called once after receiving "Time N"
    def start_game(self, time_limit_minutes: float):
        # total time the agent is allowed to consume in the whole game
        self._agent_time_left = float(time_limit_minutes) * 60.0
        self._agent_running_since = None

    def resume_clock(self):
        # call right before agent starts thinking
        if self._agent_time_left is None:
            return
        if self._agent_running_since is None:
            self._agent_running_since = time.time()

    def pause_clock(self):
        # call right after agent finishes thinking (or when it's human's turn)
        if self._agent_time_left is None:
            return
        if self._agent_running_since is not None:
            spent = time.time() - self._agent_running_since
            self._agent_time_left -= spent
            self._agent_running_since = None
            if self._agent_time_left < 0:
                self._agent_time_left = 0

    def _timed_out(self) -> bool:
        if self._agent_time_left is None:
            return False

        # if clock is running, compute current remaining
        if self._agent_running_since is not None:
            remaining = self._agent_time_left - (time.time() - self._agent_running_since)
        else:
            remaining = self._agent_time_left

        return remaining <= 0



    def _quiesce(self, state, alpha, beta, qdepth=0):
        # timed out
        if self._timed_out():
            raise TimeoutError
        if is_terminal(state):
            s = evaluate(state)
            return s if state.side == 'w' else -s

        self.qnodes += 1
        if qdepth > self.max_qdepth_reached:
            self.max_qdepth_reached = qdepth

        # stand-pat evaluation
        stand = evaluate(state)
        stand = stand if state.side == 'w' else -stand

        if qdepth >= 6:
            return stand

        if stand >= beta:
            return beta
        if stand > alpha:
            alpha = stand

        if qdepth >= MAX_QDEPTH:
            return stand

        # only captures (incl. en passant via is_capture)
        caps = capture_moves_only(state)
        if not caps:
            return alpha

        # order captures using your existing ordering (works fine)
        caps = self._order_moves(state, caps, depth_remaining=0, last_move=None)

        for mv in caps:
            if self._timed_out():
                raise TimeoutError
            nxt = apply_move(state, mv)
            score = -self._quiesce(nxt, -beta, -alpha, qdepth + 1)

            if score >= beta:
                return beta

            if score > alpha:
                alpha = score

            # 🔥 EARLY EXIT — חשוב מאוד
            if alpha >= beta:
                return alpha

        return alpha

    def choose_move(self, state, last_move=None):
        # If game time already over, stop (client decides what to do)
        if self._timed_out():
            return None
        self.resume_clock()
        self.qnodes = 0
        self.max_qdepth_reached = 0

        print("\nCOMPUTER MOVE !!!!!!!!!!!!!!!!!!!!!!!!!")
        print("I'm thinking ........")

        move_start = time.time()
        self.nodes = 0

        best_move = None
        best_val = 0

        # Start with wide window first time
        alpha = -INF
        beta = INF

        # Iterative deepening up to self.depth (IMPORTANT)
        depth = 1
        while depth <= self.depth:
            if self._timed_out():
                break

            try:
                # Search once in current window
                move, val = self._root_alphabeta(state, depth, alpha, beta, last_move)

                if move is None:
                    break

                if self._timed_out():
                    break

                # Aspiration handling (improved): only widen the side that failed
                if val >= beta:
                    beta = val + WINDOW
                    continue
                if val <= alpha:
                    alpha = val - WINDOW
                    continue

                # Success: accept result
                best_move = move
                best_val = val

                self.last_completed_depth = depth

                elapsed = time.time() - move_start
                bf = int(self.nodes ** (1 / depth)) if self.nodes > 0 else 0

                print(f"depth = {depth} | score = {best_val}")
                print(f"branching factor = {bf}")

                # Prepare next iteration window around val
                alpha = best_val - WINDOW
                beta = best_val + WINDOW
                depth += 1

            except TimeoutError:
                break



        self.pause_clock()
        remaining = round(self._agent_time_left, 2)

        if self._timed_out():
            print("\ntime is done (timeout)")
        else:
            print("\nsearch finished")

        print(f"clock: {remaining} seconds")
        print(f"\nfinal score: {best_val}\n")
        print(f"qnodes: {self.qnodes} | max_qdepth: {self.max_qdepth_reached}")

        return best_move

    # -------------------------
    # Move ordering (5 layers)
    # -------------------------
    def _order_moves(self, state, moves, depth_remaining, last_move):
        key = pos_key(state)
        hash_move = self.tt_best.get(key)

        cmove = None
        if last_move is not None:
            cmove = self.counter_move.get((last_move[0], last_move[1], state.side))

        killer1, killer2 = self.killers.get(depth_remaining, [None, None])

        scored = []
        for m in moves:
            s = 0

            if hash_move is not None and m == hash_move:
                s += 1_000_000

            cap = is_capture(state, m)
            if cap:
                next_state = apply_move(state, m)
                _, to_sq = m
                recaptured = immediate_recapture_possible(next_state, to_sq)
                s += 900_000 if not recaptured else 800_000
                s += (to_sq // 8) if state.side == 'w' else (7 - (to_sq // 8))
            else:
                if cmove is not None and m == cmove:
                    s += 700_000
                if killer1 is not None and m == killer1:
                    s += 600_000
                elif killer2 is not None and m == killer2:
                    s += 590_000

                f, t = m
                s += self.history.get((state.side, f, t), 0)

            scored.append((s, m))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored]

    # -------------------------
    # Alpha–Beta (Negamax)
    # -------------------------
    def _alphabeta(self, state, depth_remaining, alpha, beta, last_move):
        self.nodes += 1

        if self._timed_out():
            raise TimeoutError

        if is_terminal(state):
            s = evaluate(state)
            return s if state.side == 'w' else -s

        if depth_remaining == 0:
            return self._quiesce(state, alpha, beta)



        moves = generate_moves(state)
        if not moves:
            s = evaluate(state)
            return s if state.side == 'w' else -s
        # -------------------------
        # Null Move Pruning (SAFE)
        # -------------------------
        # total_pawns = bin(state.white).count("1") + bin(state.black).count("1")
        #
        # if (
        #         depth_remaining >= 3
        #         and total_pawns > 6
        #         and moves
        # ):
        #     null_state = state.__class__(
        #         white=state.white,
        #         black=state.black,
        #         side='b' if state.side == 'w' else 'w',
        #         en_passant=None
        #     )
        #
        #     R = 2
        #     null_depth = depth_remaining - 1 - R
        #
        #     if null_depth > 0:
        #         score = -self._alphabeta(
        #             null_state,
        #             null_depth,
        #             -beta,
        #             -beta + 1,
        #             last_move=None
        #         )
        #
        #         if score >= beta:
        #             return beta

        moves = self._order_moves(state, moves, depth_remaining, last_move)
        best_move_local = None

        for move in moves:
            if self._timed_out():
                raise TimeoutError

            next_state = apply_move(state, move)
            new_depth = depth_remaining - 1
            val = -self._alphabeta(next_state, new_depth, -beta, -alpha, last_move=move)

            if val >= beta:
                self.tt_best[pos_key(state)] = move

                if not is_capture(state, move):
                    k1, k2 = self.killers.get(depth_remaining, [None, None])
                    if move != k1:
                        self.killers[depth_remaining] = [move, k1]

                    f, t = move
                    self.history[(state.side, f, t)] = self.history.get((state.side, f, t), 0) + (depth_remaining * depth_remaining)

                if last_move is not None:
                    self.counter_move[(last_move[0], last_move[1], state.side)] = move

                return beta

            if val > alpha:
                alpha = val
                best_move_local = move

                if not is_capture(state, move):
                    f, t = move
                    self.history[(state.side, f, t)] = self.history.get((state.side, f, t), 0) + depth_remaining

        if best_move_local is not None:
            self.tt_best[pos_key(state)] = best_move_local

        return alpha

    def _root_alphabeta(self, state, depth, alpha, beta, last_move=None):
        best_move = None

        moves = generate_moves(state)
        if not moves:
            return None, alpha

        # 0) Fast win check (promotion / terminal in 1)
        for mv in moves:
            nxt = apply_move(state, mv)
            if is_terminal(nxt):
                v = evaluate(nxt)
                v = v if nxt.side == 'w' else -v
                if v > 0:  # only pick if winning
                    return mv, 1000000

        moves = self._order_moves(state, moves, depth, last_move)

        for move in moves:
            next_state = apply_move(state, move)
            val = -self._alphabeta(next_state, depth - 1, -beta, -alpha, last_move=move)

            if val > alpha:
                alpha = val
                best_move = move

        if best_move is not None:
            self.tt_best[pos_key(state)] = best_move

        return best_move, alpha
