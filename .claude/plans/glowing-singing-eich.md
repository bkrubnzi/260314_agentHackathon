# Plan: Questions-Only Game — Three-Agent Hackathon Demo

## Context
A hackathon demo showing three Claude agents interacting in a "Questions Only" game.
Two player agents (Sean Connery, Burt Reynolds) take turns asking each other questions.
A judge agent (Alex Trebek) evaluates each exchange for rule violations.
Purpose: educational example students can fork to build their own multi-agent games.

Infrastructure: AWS Bedrock, Claude Haiku (`us.anthropic.claude-haiku-4-5-20251001-v1:0`, `us-west-2`).

---

## Game Rules (implemented in agent prompts)
- Players may only ask questions — no statements
- Questions may not be rhetorical
- A player may not rephrase or repeat a previous question
- If a player violates a rule → opponent scores a point → round ends
- Each round lasts up to 10 questions OR until a point is scored
- Game = 3 rounds; final score is total points across all rounds

---

## File Structure

```
main.py           # Entry point — runs the game
agents.py         # Agent base class + the three character agents
game.py           # Game orchestrator (rounds, turns, scoring)
requirements.txt  # anthropic[bedrock]
```

---

## Agent Design (`agents.py`)

### `Agent` base class
```python
class Agent:
    def __init__(self, name: str, system_prompt: str, client, model: str)
    def respond(self, context: str) -> str
        # Single messages.create call
        # messages=[{"role": "user", "content": context}]
        # Returns agent's text response
```

No persistent conversation history per agent — context is assembled fresh each call
from the game transcript. This is intentional: makes the data flow transparent for students.

### Three character agents (instances of Agent)

**sean_connery** — Player
- System prompt: Scottish accent, Bond references, competitive, dry wit
- Role instruction: "You are playing Questions Only. You MUST only ask questions. No statements. No rhetorical questions. Do not repeat or rephrase any prior question. One question per turn. Stay in character."

**burt_reynolds** — Player
- System prompt: Southern charm, mustache confidence, laid-back swagger
- Role instruction: same game rules as Sean

**alex_trebek** — Judge
- System prompt: Formal, authoritative, game show host gravitas
- Role instruction: "Evaluate the last question for rule violations. Return ONLY valid JSON: `{\"violated\": true/false, \"violator\": \"<name>\" or null, \"rule\": \"<description>\" or null, \"explanation\": \"<one sentence>\"}`"

---

## Game Orchestrator (`game.py`)

### `GameState` dataclass
```python
@dataclass
class GameState:
    scores: dict[str, int]   # {"Sean Connery": 0, "Burt Reynolds": 0}
    round_num: int
    questions_this_round: list[str]  # ["Sean: ...", "Burt: ..."]
    all_history: list[str]   # full game transcript
```

### `build_player_context(state, current_player, opponent)` → str
Assembles the prompt passed to a player agent:
- Current round number and score
- Full question history for this round (so they don't repeat)
- Whose turn it is: "You are {name}. Ask {opponent} a question."

### `build_judge_context(state, last_question, asker)` → str
Assembles the prompt passed to Alex:
- All questions asked this round (for repetition checking)
- The last question and who asked it
- Rules reminder

### `run_round(state, players, judge)` → None
```
loop up to 10 times:
    current_player asks → get question
    print: "SEAN CONNERY: <question>"
    call judge → parse JSON judgment
    print: "ALEX TREBEK: <explanation>"
    if violated:
        opponent scores +1
        print scoring message
        break
    swap current_player
```

### `run_game(players, judge)` → None
```
for round 1..3:
    print round header + current scores
    run_round(...)
print final scores + winner
```

---

## Context Assembly Pattern (key teaching moment)

Each API call gets the full relevant transcript as a single user message.
No stateful conversation objects — just strings. This pattern is easy to understand and extend.

```python
context = f"""
Round {state.round_num} of 3. Scores: Sean {state.scores['Sean Connery']} — Burt {state.scores['Burt Reynolds']}

Questions asked this round:
{chr(10).join(state.questions_this_round) or "(none yet)"}

You are {current_player}. Ask {opponent} a question. Stay in character.
"""
response = player_agent.respond(context)
```

---

## `requirements.txt`
```
anthropic[bedrock]
```

---

## `main.py`
```python
from agents import sean_connery, burt_reynolds, alex_trebek
from game import run_game

if __name__ == "__main__":
    run_game(
        players=[sean_connery, burt_reynolds],
        judge=alex_trebek
    )
```

---

## AWS Bedrock Client Setup
```python
import anthropic
client = anthropic.AnthropicBedrock(aws_region="us-west-2")
MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
```
Uses AWS credential chain automatically (env vars `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`).

---

## Verification
1. Set env vars: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION=us-west-2`
2. `pip install anthropic[bedrock]`
3. `python main.py`
4. Observe: 3 rounds of dialogue, Alex judging each question, scores tracked
5. Game ends with final score printout

---

## Teaching Notes (for README)
- Swap character names/prompts to create new games
- Change `build_player_context` to give agents different information
- Change `build_judge_context` to implement different rule sets
- Add more agents by extending the players list
