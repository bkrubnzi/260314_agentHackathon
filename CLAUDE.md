# CLAUDE.md - Project Guidelines

## Project: Questions Only - Multi-Agent Game Demo

A hackathon educational demo showing three Claude agents interacting in a question-asking game. Built for students to fork and create their own multi-agent games.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

Requires AWS Bedrock credentials: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION=us-west-2`

## Architecture

### Three Agents
- **Sean Connery** (Player) — Asks questions, answers with questions back
- **Burt Reynolds** (Player) — Asks questions, answers with questions back
- **Alex Trebek** (Judge) — Evaluates questions for rule violations

### Game Flow
1. 3 rounds
2. Players alternate asking questions (max 10 per round or until violation)
3. Judge enforces rules silently (only speaks on violations)
4. First violation ends round, opponent scores
5. Random starting player Round 1; winner starts subsequent rounds

### Design Pattern
- **No persistent conversation state** — Each agent call includes fresh context (transparent for learning)
- **Agent class** — Wraps system prompt + LLM call
- **GameState** — Simple dataclass tracking scores, questions, round
- **Context builders** — Assemble prompts fresh each turn

## Critical Rules

### Players
- **ONLY ask questions** — No statements, no actions (*leans back*), no roleplay text
- **Answer with questions** — Respond to opponent's question by asking a question back
- **Max 10 words** — Keep questions sharp and brief
- **No rhetorical questions** — Must have genuine possible answers
- **No repeats** — Cannot ask same question twice in a round

### Judge
- **Natural language only** — NO JSON, NO code fences, NO backticks
- **Silent for valid questions** — Only speak when there's a violation
- **"VIOLATION: [reason]" format** — For rule breaks
- **Current round only** — Never reference previous rounds
- **Exact match only** — Only flag if question exactly matches previous one

## Code Quality Standards

Code must be:
- **Very clean** — Clear variable names, simple logic
- **Well documented** — Docstrings for classes/functions, inline comments where needed
- **Easy to read** — Short functions, meaningful separation, clear intent
- **Educational** — Students should immediately understand what each piece does

No over-engineering. No unnecessary abstractions. Keep it simple.

## File Organization

```
main.py              Entry point
agents.py            Agent class + three agents
game.py              GameState + game orchestration
requirements.txt     Dependencies
README.md            Full documentation
.claude/
  plans/             Implementation plans (before coding)
  progress/          Progress tracking during work
  prompts/           Prompt history and game design docs
```

## Development Guidelines

### When Adding Features
1. Use EnterPlanMode if change is non-trivial
2. Ask questions if requirements are unclear
3. Read existing code before suggesting changes
4. Prefer editing existing files over creating new ones
5. Keep changes focused and simple

### Testing
- Run `python main.py` to verify game works end-to-end
- Look for: proper turn alternation, rule enforcement, clean output, no crashes
- Watch for: judge responding in JSON, players including actions, long questions

### Common Modifications

**Change agent persona:**
- Edit system prompt in `agents.py`
- Keep rules the same, just change tone/character

**Add a new rule:**
- Update judge system prompt in `agents.py`
- Update `build_judge_context()` in `game.py` to mention the rule
- Test with manual game run

**Change game structure:**
- Modify `run_round()` and `run_game()` in `game.py`
- Update scoring logic if needed
- Keep GameState synchronized

## Known Patterns

### Judge Parsing
Judge responses start with "VIOLATION:" if there's a violation, otherwise it's silent approval.
Parser checks: `if response.upper().startswith("VIOLATION:")`

### Player Context
Shows current round, scores, previous questions, opponent's last question, and clear instruction to answer the question.

### API Setup
Uses `anthropic.AnthropicBedrock(aws_region="us-west-2")` with Haiku model for cost.
Players: `max_tokens=50` (10 words)
Judge: `max_tokens=60` (one sentence)

## Hackathon Context

This is a **template for students** to:
- See a working multi-agent example
- Understand agent communication patterns
- Fork and build their own games
- Modify personas, rules, game structure

Keep the code accessible and educational. Avoid complexity.

## References

- Full docs: `README.md`
- Game design: `.claude/prompts/game_design_prompt.md`
- Instructions: `.claude/prompts/INSTRUCTIONS.md`
- Prompts history: `.claude/prompts/`
