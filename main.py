#!/usr/bin/env python3
"""
Questions Only - Multi-Agent Game Demo

A hackathon example showing three Claude agents interacting:
- Sean Connery (player)
- Burt Reynolds (player)
- Alex Trebek (judge)

Students can fork this to build their own multi-agent games.

To run:
    pip install -r requirements.txt
    python main.py

You will need AWS credentials configured (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION).
"""

from agents import sean_connery, burt_reynolds, alex_trebek
from game import run_game


def main():
    """Run a complete game of Questions Only."""
    players = {
        "Sean Connery": sean_connery,
        "Burt Reynolds": burt_reynolds
    }
    judge = alex_trebek

    run_game(players, judge)


if __name__ == "__main__":
    main()
