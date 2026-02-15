<div align="center">

# ♟ Pawn-Only Chess – AlphaBeta Agent

### OMAR HIJAB

---

### A Pawn-Only Chess AI using Alpha-Beta Search & Quiescence Search

---

</div>

---

## 📌 This Document Explains

1. How to run a game against the agent (`our_agent.exe`)  
2. How to interpret the agent’s output during the game  
3. How to define a custom starting position (SETUP) in `humanVSouragent.exe`

---

<div align="center">

---

# ▶ Running a Game Against the Agent (Agent vs Agent)

---

</div>

The agent connects to a tournament server or another agent.

### 🔹 Basic Command

```bash
our_agent.exe --net 127.0.0.1 9999 --side b

🔹 Parameters
--net <HOST> <PORT>   Server IP address and port
--side w | b          Side of the agent
                      w = White
                      b = Black
🔹 Example Full Scenario (30-Game Tournament)
server2p.exe 9999 logs -v --accept-tournament-cmd --elo --elo-baseline 1500 --elo-k 40

ChessNet.exe --net 127.0.0.1 9999 --side w --tour 30 --random-openings --random-plies 1 --seed 1338

our_agent.exe --net 127.0.0.1 9999 --side b

In this scenario:

1.ChessNet plays White

2.Our agent plays Black

<div align="center">

📊 Interpreting the Agent Output

</div>

After every ply (move), the agent prints search information.

🔹 Example Output

COMPUTER MOVE !!!!!!!!!!!!!!!!!!!!!!!!!
I'm thinking ........
depth = 1 | score = 10
branching factor = 16
depth = 2 | score = -5
branching factor = 7
depth = 3 | score = 10
branching factor = 7
depth = 4 | score = -5
branching factor = 5

search finished
clock: 1019.94 seconds

final score: -5

qnodes: 890 | max_qdepth: 3
Agent plays: a7a5

🔹 Explanation

| Field            | Meaning                           |
| ---------------- | --------------------------------- |
| depth = k        | Search depth                      |
| score            | Evaluation of position            |
| Positive score   | Good for White                    |
| Negative score   | Good for Black                    |
| branching factor | Avg. number of moves per position |
| clock            | Remaining time (seconds)          |
| final score      | Evaluation of chosen move         |
| qnodes           | Quiescence nodes evaluated        |
| max_qdepth       | Max quiescence depth              |
| Agent plays      | Selected move                     |

Move format example:
a7a5 → pawn moves from a7 to a5

<div align="center">

⚙ Custom Starting Position (SETUP)

</div>

Play locally using:

humanVSouragent.exe

You will be asked:

Enter total game time (minutes):
Enter SETUP (or press Enter for default):

🔹 SETUP Format

Each pawn:
<Color><File><Rank>
W = White pawn
B = Black pawn
🔹 Example
Wa2 Wb2 Wc2
Ba7 Bb7
🔹 Default Setup
Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2
Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7
🔹 Entering Moves
Your move (e2e4 / exit):
Example:
a2a4
To resign:
exit
<div align="center">

✅ Summary
</div>

our_agent.exe → Play vs other agents

humanVSouragent.exe → Play locally

SETUP allows any custom starting position

Agent prints depth, evaluation, and chosen move

