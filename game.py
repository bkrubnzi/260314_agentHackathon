"""
Game orchestration for Questions Only.

Manages game state, turns, scoring, and communication with player and judge agents.
"""

import json
import random
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GameState:
    """
    Tracks the current state of the game.

    Attributes:
        scores: Dict mapping player names to their current score
        round_num: The current round (1, 2, or 3)
        questions_this_round: List of questions asked in the current round
        all_history: Full transcript of all questions across all rounds (for context)
    """
    scores: dict = field(default_factory=lambda: {"Sean Connery": 0, "Burt Reynolds": 0})
    round_num: int = 1
    questions_this_round: List[str] = field(default_factory=list)
    all_history: List[str] = field(default_factory=list)


def build_player_context(state: GameState, current_player: str, opponent: str) -> str:
    """
    Build the context prompt for a player agent.

    Shows the player the current round, scores, question history, and the last question asked,
    so they can respond to it. The player uses this to generate their next question.

    Args:
        state: Current game state
        current_player: Name of the player whose turn it is
        opponent: Name of the opposing player

    Returns:
        A formatted context string for the player agent
    """
    score_str = f"Sean Connery: {state.scores['Sean Connery']}, Burt Reynolds: {state.scores['Burt Reynolds']}"

    question_history = ""
    opponent_last_question = ""

    if state.questions_this_round:
        question_history = "\nQuestions asked this round:\n"
        for i, q in enumerate(state.questions_this_round, 1):
            question_history += f"{i}. {q}\n"

        # Get the last question (opponent's question to us)
        last_q = state.questions_this_round[-1]
        opponent_last_question = f"\n{opponent} asked: {last_q.split(': ', 1)[1] if ': ' in last_q else last_q}"
        instruction = f"\nAnswer {opponent}'s question by asking a question back."
    else:
        question_history = ""
        opponent_last_question = ""
        instruction = f"\nYou start! Ask {opponent} a question."

    context = f"""Round {state.round_num} of 3 | Scores: {score_str}

{question_history}{opponent_last_question}{instruction}

You are {current_player}. Ask ONE question (genuine, not rhetorical, not a repeat). Max 10 words. Stay in character."""

    return context


def build_judge_context(state: GameState, last_question: str, asker: str, opponent: str) -> str:
    """
    Build the context prompt for the judge agent.

    Shows the judge the question history and the last question to evaluate,
    so the judge can check for rule violations.

    Args:
        state: Current game state
        last_question: The question to evaluate
        asker: Name of the player who asked the question
        opponent: Name of the opponent

    Returns:
        A formatted context string for the judge agent
    """
    question_history = ""
    for i, q in enumerate(state.questions_this_round, 1):
        question_history += f"{i}. {q}\n"

    context = f"""Round {state.round_num}, Question {len(state.questions_this_round)}

Previous questions this round:
{question_history if question_history else "(None yet)"}

Now {asker} asked {opponent}: "{last_question}"

Evaluate this question:
1. Is it rhetorical? (Does it have a genuine possible answer?)
2. Is it a repeat or rephrase of a previous question?
3. Is it actually a question (not a statement)?

Return ONLY JSON."""

    return context


def parse_judge_decision(judge_response: str) -> dict:
    """
    Parse the judge's natural language response.

    Checks if the response starts with "VIOLATION:" to determine if a rule was broken.

    Args:
        judge_response: The text response from the judge agent

    Returns:
        A dict with keys: violated (bool), explanation (str)
    """
    judge_response = judge_response.strip()

    # Check if there's a violation (response starts with "VIOLATION:")
    if judge_response.upper().startswith("VIOLATION:"):
        # Extract explanation after "VIOLATION:"
        explanation = judge_response[10:].strip()
        return {
            "violated": True,
            "explanation": explanation
        }
    else:
        # No violation
        return {
            "violated": False,
            "explanation": judge_response
        }


def run_round(state: GameState, players: dict, judge, starting_player: str) -> Optional[str]:
    """
    Run a single round of the game.

    Players take turns asking questions up to 10 questions or until a rule violation.
    The judge evaluates each question. If a violation occurs, the opponent scores and round ends.

    Args:
        state: Current game state (will be modified)
        players: Dict mapping player names to Agent objects
        judge: The judge Agent object
        starting_player: Name of the player who starts this round

    Returns:
        The name of the player who scored a point, or None if round ended without a score
    """
    max_questions = 10
    player_names = list(players.keys())
    # Find the starting player's index
    current_player_idx = player_names.index(starting_player)

    print(f"\n{'='*70}")
    print(f"ROUND {state.round_num}")
    print(f"{'='*70}")
    print(f"Scores: Sean Connery {state.scores['Sean Connery']} | Burt Reynolds {state.scores['Burt Reynolds']}")
    print()

    while len(state.questions_this_round) < max_questions:
        current_player = player_names[current_player_idx]
        opponent = player_names[1 - current_player_idx]

        # Get the player's question
        context = build_player_context(state, current_player, opponent)
        question = players[current_player].respond(context)

        print(f"{current_player}: {question}")

        # Judge the question (before adding to history, so judge doesn't see it as "previous")
        judge_context = build_judge_context(state, question, current_player, opponent)
        judge_response = judge.respond(judge_context)
        decision = parse_judge_decision(judge_response)

        # Add to question history after judging
        state.questions_this_round.append(f"{current_player}: {question}")
        state.all_history.append(f"{current_player}: {question}")

        if decision["violated"]:
            # Rule violation - opponent scores
            print(f"Alex Trebek: {decision['explanation']}")

            opponent_score = state.scores[opponent]
            state.scores[opponent] = opponent_score + 1
            print(f"\n{opponent} scores! New score: {opponent} {state.scores[opponent]}")
            print(f"Round ends.\n")
            return opponent  # Return the player who scored
        else:
            # No violation - Alex stays silent, game continues
            print()

        # Alternate turns
        current_player_idx = 1 - current_player_idx

    # Round over - show final scores
    if len(state.questions_this_round) >= max_questions:
        print(f"Round complete (10 questions reached).")
        print(f"Scores: Sean Connery {state.scores['Sean Connery']} | Burt Reynolds {state.scores['Burt Reynolds']}\n")

    return None  # No one scored this round


def run_game(players: dict, judge) -> None:
    """
    Run a complete game of Questions Only (3 rounds).

    Args:
        players: Dict mapping player names to Agent objects
        judge: The judge Agent object
    """
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "QUESTIONS ONLY - Multi-Agent Game Demo" + " "*15 + "║")
    print("╚" + "="*68 + "╝")
    print()

    state = GameState()
    player_names = list(players.keys())

    # Round 1: Randomly select starting player
    starting_player = random.choice(player_names)
    print(f"Starting player for Round 1 (randomly selected): {starting_player}\n")

    # Play 3 rounds
    for round_num in range(1, 4):
        state.round_num = round_num
        state.questions_this_round = []  # Reset questions for new round

        # Run the round and get the player who scored (if any)
        scoring_player = run_round(state, players, judge, starting_player)

        # Next round starts with the player who scored, or keep current if no score
        if scoring_player:
            starting_player = scoring_player
        # If no one scored, starting_player stays the same (or we could randomize)

    # Game over - announce winner
    print("="*70)
    print("GAME OVER - FINAL SCORES")
    print("="*70)
    sean_score = state.scores["Sean Connery"]
    burt_score = state.scores["Burt Reynolds"]
    print(f"Sean Connery:    {sean_score}")
    print(f"Burt Reynolds:   {burt_score}")
    print()

    if sean_score > burt_score:
        print(f"🏆 Sean Connery wins {sean_score} to {burt_score}!")
    elif burt_score > sean_score:
        print(f"🏆 Burt Reynolds wins {burt_score} to {sean_score}!")
    else:
        print(f"🤝 It's a tie! Both players scored {sean_score} points.")

    print()
