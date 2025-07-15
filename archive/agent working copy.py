# agent.py
from smolagents import CodeAgent, TransformersModel
from tools.lot_sizing_tool import solve_lot_sizing, solve_lot_sizing_basic

# Choose and configure the language model for the agent:
# Option 1: Use Anthropic Claude via official API (online).
# Option 2: Use an OpenAI/OpenRouter API for Claude or GPT-4 (online).
# Option 3: Use a local LLM via transformers (offline).


# Example: Use Phi-3-mini for macOS (M-series, no load_4bit)
model = TransformersModel(
    model_id="microsoft/Phi-3-mini-128k-instruct",  # 3.8 B params
    device_map="auto",  # will use M-series GPU via Metal
    torch_dtype="auto",  # fp16 on GPU, bf16 on CPU
    max_new_tokens=1024,
    temperature=0.2,
)

# If you have internet/API access and want Claude or GPT-4:
# model = OpenAIServerModel(model_id="anthropic/claude-2", api_base="https://api.anthropic.com/", api_key="YOUR_ANTHROPIC_KEY")
# (The above would be if Anthropic provided an OpenAI-compatible endpoint, otherwise use anthropic's SDK.)
# Or using OpenRouter (single key for many models):
# model = OpenAIServerModel(model_id="openai/gpt-4", api_base="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
# (OpenRouter can route to various models including GPT-4 or Claude with the proper model_id.)

# Initialize the agent with our tool
agent = CodeAgent(
    model=model,
    tools=[solve_lot_sizing, solve_lot_sizing_basic],
    max_steps=4,
)

# Example query to the agent:
question = (
    "Given monthly demands of 100, 150, 80, 130 units and a setup cost of $1000, "
    "unit cost $50, and holding cost $2 per unit per month, "
    "what is the optimal production plan and total cost?"
)
response = agent.run(question)
print("Agent answer:", response)


# python agent.py
