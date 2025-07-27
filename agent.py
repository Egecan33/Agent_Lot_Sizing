from smolagents import CodeAgent, TransformersModel
from tools.eptr_tool import fetch_mcp

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


# Initialize the agent with our tool
agent = CodeAgent(
    model=model,
    tools=[fetch_mcp],  # can use more tools
    max_steps=4,
    additional_authorized_imports=[
        "os"
    ],  # Allows os for file checks if agent generates them (optional but prevents errors)
)

# Example query to the agent:
question = "What is the market clearing price (PTF) for today?"
response = agent.run(question)
print("Agent answer:", response)
