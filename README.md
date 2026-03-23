# Questions Only - Multi-Agent Game Demo

A hackathon example demonstrating three Claude agents interacting in a game setting. Two player agents (Sean Connery and Burt Reynolds) take turns asking each other questions while a judge agent (Alex Trebek) enforces the rules.

This serves as a template for students to build their own multi-agent games using Claude and the Claude Agent SDK.   

## Quick Start

### Prerequisites
- Python 3.8+
- AWS credentials configured (for Bedrock access)
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_DEFAULT_REGION=us-west-2`

### Installation & Run

```bash
pip install -r requirements.txt
python main.py
```

## Game Rules

**Players** can only ask questions — no statements, no commentary.

**Questions** must:
- NOT be rhetorical (must have genuine possible answers)
- NOT repeat or rephrase any previous question
- Be a real question (not a statement)

**Judge** (Alex Trebek) evaluates each question for rule violations.

**Scoring**: If a player violates a rule, the opponent scores 1 point and the round ends.

**Game Structure**:
- 3 rounds total
- Each round lasts up to 10 questions OR until someone scores
- Winner is the player with the most points after all 3 rounds

## Project Structure

```
main.py          Entry point - runs the game
agents.py        Agent class + three character agents (Sean, Burt, Alex)
game.py          Game orchestration (rounds, turns, scoring, judging)
requirements.txt Python dependencies
README.md        This file
```

## File Descriptions

### `agents.py`

Defines the `Agent` class and the three game agents.

**Agent class:**
- Takes a name and system prompt in the constructor
- Has a `respond(context)` method that calls Claude via AWS Bedrock
- Each call is independent (no persistent conversation state)

**Three agents:**
1. **Sean Connery** - Player. System prompt defines Scottish accent, Bond references, competitive personality
2. **Burt Reynolds** - Player. System prompt defines Southern charm, suave confidence, laid-back personality
3. **Alex Trebek** - Judge. System prompt defines authoritative game show host persona and rule-checking role

### `game.py`

Handles all game logic:

- **GameState** dataclass: tracks scores, round number, question history
- **build_player_context()**: assembles the prompt for a player (shows game state, history, whose turn)
- **build_judge_context()**: assembles the prompt for the judge (shows questions to evaluate for violations)
- **parse_judge_decision()**: parses the judge's JSON response into a decision dict
- **run_round()**: orchestrates a single round (alternating turns, judging, scoring)
- **run_game()**: runs all 3 rounds and announces the winner

### `main.py`

Simple entry point. Creates the player and judge agent objects, then calls `run_game()`.

## How It Works

### Agent Communication Pattern

This demo uses a simple, transparent pattern for agent communication:

1. Build a context string with game state and history
2. Pass it to an agent's `respond()` method
3. Agent returns a single response
4. Parse the response (extract JSON for judge, extract question for players)
5. Update game state

**No persistent conversation state** — each agent call includes the full relevant context. This makes the data flow obvious and easy for students to understand and modify.

### Judge Response Format

The judge returns JSON:
```json
{
  "violated": false,
  "violator": null,
  "rule": null,
  "explanation": "Well asked."
}
```

If there's a violation:
```json
{
  "violated": true,
  "violator": "Sean Connery",
  "rule": "Asked a rhetorical question",
  "explanation": "The question could not have a genuine answer."
}
```

## Extending This Demo

### Add a new game variant

1. Create new system prompts for different characters
2. Modify `build_player_context()` to change what information players see
3. Modify `build_judge_context()` to implement different rule sets
4. Change the game structure in `run_round()` (e.g., 5 rounds instead of 3, different scoring)

### Add more players

1. Create new Agent instances in `agents.py`
2. Add them to the `players` dict in `main.py`
3. Modify game logic to handle multiple players (e.g., rotating turns)

### Add new rules

Modify the system prompts in `agents.py` and the judge's evaluation logic in `game.py`.

### Use different models

In `agents.py`, change the `self.model` in the `Agent.__init__()` method. For example:
- `claude-3-5-sonnet` for better reasoning
- `claude-opus` for more capable outputs

### Use the direct Anthropic API instead of Bedrock

In `agents.py`, replace:
```python
from anthropic import AnthropicBedrock
self.client = AnthropicBedrock(aws_region="us-west-2")
```

With:
```python
from anthropic import Anthropic
self.client = Anthropic(api_key="your-api-key")
```

And set `self.model` to any standard Claude model ID.

## Key Learning Points for Students

1. **Agent abstraction**: Each agent is independent, with its own persona and role
2. **Context assembly**: Agents receive full game context fresh each turn (no stateful conversation)
3. **Structured outputs**: Judge returns JSON for easy parsing
4. **Turn orchestration**: Game controller decides whose turn it is and enforces rules
5. **Extensibility**: Easy to modify character personas, rules, game structure, or add new agents

## Troubleshooting

**ModuleNotFoundError: No module named 'anthropic'**
- Run `pip install -r requirements.txt`

**botocore.exceptions.NoCredentialsError**
- Check that AWS credentials are set: `echo $AWS_ACCESS_KEY_ID`
- Set them: `export AWS_ACCESS_KEY_ID=your-key` (and SECRET_ACCESS_KEY and DEFAULT_REGION)

**Judge's response is malformed**
- The judge agent occasionally fails to return valid JSON
- The code handles this gracefully with `parse_judge_decision()` — it treats parse errors as non-violations

## Notes

- Uses AWS Bedrock for Claude access (Haiku model for cost-effectiveness)
- Each agent call is independent (no persistent conversation objects)
- Judge responses are parsed as JSON for structured rule evaluation
- Plain text output for clarity (easy to see what's happening)
