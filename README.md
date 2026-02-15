=============================================
===== Pawn-Only Chess – AlphaBeta Agent =====
=============================================

============= OMAR HIJAB ====================

This document explains:

1.How to run a game against the agent (our_agent.exe)

2.How to interpret the agent’s output during the game

3.How to define a custom starting position (SETUP) in humanVSouragent.exe


=================================================================
Running a Game Against the Agent (our_agent.exe) agent vs agent :
=================================================================

The agent connects to a tournament server or another agent.

Basic command:

our_agent.exe --net 127.0.0.1 9999 --side b

Parameters:

--net <HOST> <PORT>
Server IP address and port.

--side w | b
Side of the agent:
w = White
b = Black

Example full scenario (30 game tournament):

server2p.exe 9999 logs -v --accept-tournament-cmd --elo --elo-baseline 1500 --elo-k 40

ChessNet.exe --net 127.0.0.1 9999 --side w --tour 30 --random-openings --random-plies 1 --seed 1338

our_agent.exe --net 127.0.0.1 9999 --side b

In this scenario:

ChessNet plays White
Our agent plays Black

=============================
Interpreting the Agent Output
=============================

After every ply (move), the agent prints search information.

Example output:

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

Explanation of fields:

depth = k
Search depth level.

score
Board evaluation at this depth
Positive = good for White
Negative = good for Black

branching factor
Average number of moves explored from each position.

search finished
Search has completed.

clock
Remaining time for the agent (seconds).

final score
Evaluation of the chosen move.

qnodes
Number of nodes evaluated in quiescence search.

max_qdepth
Maximum depth reached in quiescence search.

Agent plays
The move selected by the agent (from-square to-square).

Example:
a7a5 means pawn from a7 moves to a5.

========================================================
Custom Starting Position (SETUP) in humanVSouragent.exe:
========================================================

humanVSouragent.exe allows playing locally against the agent using a terminal.

Run:

humanVSouragent.exe

You will be asked:

Enter total game time (minutes):

Then:

Enter SETUP (or press Enter for default):

SETUP format:

Each pawn is written as:

<Color><File><Rank>

W = White pawn
B = Black pawn

Example:

Wa2 Wb2 Wc2
Ba7 Bb7

Default setup (if Enter is pressed):

Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2
Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7

This represents the standard pawn-only starting position.

Entering moves during the game:

Your move (e2e4 / exit):

Example:

a2a4

To resign:

exit

========
Summary:
========

1.our_agent.exe – Play against another agent via connecting to the server

2.humanVSouragent.exe – Play locally against the agent

3.SETUP allows defining any starting position

4.agent output displays search depth, evaluation, and chosen move
