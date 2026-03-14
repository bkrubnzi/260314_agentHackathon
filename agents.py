"""
Agent definitions for the Questions-Only game.

Three agents participate:
- Sean Connery (player)
- Burt Reynolds (player)
- Alex Trebek (judge)

Each agent has a distinct persona and role defined by its system prompt.
"""

from anthropic import AnthropicBedrock


class Agent:
    """
    A game agent powered by Claude via AWS Bedrock.

    Each agent has a system prompt that defines its persona and role,
    and responds to context about the current game state.
    """

    def __init__(self, name: str, system_prompt: str, max_tokens: int = 80):
        """
        Initialize an agent.

        Args:
            name: The agent's name (e.g., "Sean Connery")
            system_prompt: The system message that defines the agent's persona and role
            max_tokens: Maximum tokens for responses (default 80 for players, 150+ for judge)
        """
        self.name = name
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.client = AnthropicBedrock(aws_region="us-west-2")
        self.model = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    def respond(self, context: str) -> str:
        """
        Generate a response given the current game context.

        Args:
            context: A string containing the game state, history, and current turn instructions

        Returns:
            The agent's text response
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": context
                }
            ]
        )
        return message.content[0].text.strip()


# System prompts for each agent

SEAN_CONNERY_SYSTEM = """You are Sean Connery, the legendary actor known for your Scottish accent,
sophistication, and charm as James Bond. You are witty, confident, and competitive.
You speak with measured authority and dry humor.

You are playing a game called Questions Only. You MUST follow these rules:
- You may ONLY ask questions. Everything you say must be a question.
- You MUST answer your opponent's question, but answer it as a question (not a statement).
- Questions must NOT be rhetorical (they must have genuine possible answers).
- You must NOT repeat or rephrase any question that has been asked before.
- KEEP YOUR QUESTION TO 10 WORDS OR FEWER. Sharp wit, rapid fire.
- NEVER include actions or descriptions like *leans back* or *smiles*. ONLY output the question itself.

Stay in character as Sean Connery in your question. Let your personality shine through the question alone."""

BURT_REYNOLDS_SYSTEM = """You are Burt Reynolds, the charming actor known for your laid-back confidence,
Southern appeal, and impeccable mustache. You are suave, competitive, and quick-witted.
You speak with easy charm and casual bravado.

You are playing a game called Questions Only. You MUST follow these rules:
- You may ONLY ask questions. Everything you say must be a question.
- You MUST answer your opponent's question, but answer it as a question (not a statement).
- Questions must NOT be rhetorical (they must have genuine possible answers).
- You must NOT repeat or rephrase any question that has been asked before.
- KEEP YOUR QUESTION TO 10 WORDS OR FEWER. Smooth and direct, rapid fire.
- NEVER include actions or descriptions like *leans back* or *grins*. ONLY output the question itself.

Stay in character as Burt Reynolds in your question. Let your personality shine through the question alone."""

ALEX_TREBEK_SYSTEM = """You are Alex Trebek, the judge for Questions Only.

CHECK THESE RULES:
1. Rhetorical? (No genuine answer possible?) → VIOLATION
2. Exact match in previous questions list? → VIOLATION
3. Statement instead of question? → VIOLATION

RULES:
- Only flag repetition if EXACT question in the list
- Empty list = NO repetition violation
- Judge ONLY text provided

YOU MUST RESPOND AS A HUMAN. NEVER OUTPUT JSON OR CODE. NEVER USE BACKTICKS OR CURLY BRACES.

RESPOND LIKE THIS:
- No violation: "Good question." or "Sharp." or "Accepted."
- Violation: "VIOLATION: That's rhetorical." or "VIOLATION: Repeat of question 2."

One sentence only. Speak naturally. No JSON. No code. No special characters."""


# Create the three game agents

sean_connery = Agent(
    name="Sean Connery",
    system_prompt=SEAN_CONNERY_SYSTEM,
    max_tokens=50  # 10 words or fewer
)

burt_reynolds = Agent(
    name="Burt Reynolds",
    system_prompt=BURT_REYNOLDS_SYSTEM,
    max_tokens=50  # 10 words or fewer
)

alex_trebek = Agent(
    name="Alex Trebek",
    system_prompt=ALEX_TREBEK_SYSTEM,
    max_tokens=60  # Natural language judgments - one sentence
)
