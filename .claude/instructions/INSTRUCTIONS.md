# Questions Only Game - Instructions

## Running the Game

### Prerequisites
- Python 3.8+
- AWS credentials configured:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_DEFAULT_REGION=us-west-2`

### Installation
```bash
pip install -r requirements.txt
python main.py
```

## File Structure
- `main.py` — Entry point
- `agents.py` — Agent class + three character agents (Sean, Burt, Alex)
- `game.py` — Game orchestration (GameState, round logic, scoring)
- `requirements.txt` — Dependencies (anthropic[bedrock])
- `README.md` — Full documentation

## How It Works

### Agent Communication Pattern
1. Build context string with game state and question history
2. Pass to agent's `respond()` method
3. Agent returns response (question or judgment)
4. Parse response and update game state
5. Repeat until round ends

**No persistent conversation state** — each call includes fresh context for transparency.

### Judge Evaluation
- Receives current round's questions + last question asked
- Checks: Is it rhetorical? Repeated? A statement?
- Returns natural language response
- "VIOLATION: [reason]" for rule breaks
- Silent (no response) for valid questions

### Player Turns
- Receive game state + opponent's last question
- Must answer the question by asking a question back
- Output only the question (no actions, no stage directions)
- Max 10 words

## Extending the Game

### Change Agent Personas
Edit system prompts in `agents.py`:
```python
SEAN_CONNERY_SYSTEM = """Your new persona here..."""
```

### Add New Rules
Update `build_judge_context()` in `game.py` to mention new rules:
```python
judge_context = f"""...\nNew rule: [description]"""
```

Then update judge system prompt in `agents.py` to check for it.

### Change Game Structure
- **More rounds**: Change `range(1, 4)` to `range(1, 6)` in `run_game()`
- **More questions per round**: Change `max_questions = 10` in `run_round()`
- **Different scoring**: Modify `state.scores[opponent] += 1` logic
- **Multiple players**: Extend the players dict and rotation logic in `run_round()`

### Use Different Models
In `agents.py`, change `self.model`:
```python
self.model = "anthropic.claude-3-5-sonnet-20241022"  # For better reasoning
```

### Use Direct Anthropic API Instead of Bedrock
In `agents.py`:
```python
from anthropic import Anthropic
self.client = Anthropic(api_key="your-key")
self.model = "claude-3-5-sonnet-20241022"  # Any standard Claude model
```

## Key Teaching Points for Students

1. **Agent Abstraction**: Each agent is independent with its own persona/role
2. **Context Assembly**: Fresh context each call (no stateful conversation objects)
3. **Turn Orchestration**: Game controller decides who goes when
4. **Rule Enforcement**: Judge evaluates based on provided context only
5. **Game State Management**: Simple dataclass tracks round, scores, history
6. **Natural Language Processing**: Simple pattern matching (VIOLATION: prefix)

## Troubleshooting

**ModuleNotFoundError: anthropic**
```bash
pip install -r requirements.txt
```

**botocore.exceptions.NoCredentialsError**
```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-west-2
```

**Judge outputting JSON**
- The judge system prompt explicitly forbids JSON
- If it happens, update the prompt with stronger emphasis
- Example: "NEVER OUTPUT JSON. RESPOND ONLY AS A HUMAN WOULD."

**Players including actions**
- Players are instructed to output only questions
- If they add "*leans back*" text, remind them in system prompt

**Questions too long**
- Reduce `max_tokens` for players (currently 50)
- Emphasize "10 WORDS OR FEWER" in system prompt
