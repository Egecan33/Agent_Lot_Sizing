#!/usr/bin/env python3
"""
streamlit_app.py - Simplified ChatGPT-like interface
"""

import streamlit as st
from smolagents import CodeAgent, TransformersModel
from transformers import AutoTokenizer
from tools.eptr_tool import solve_mcp


MODEL_ID = "microsoft/Phi-3-mini-128k-instruct"
all_tools = [
    solve_mcp,
]


# Initialize the agent once
@st.cache_resource(show_spinner=False)
def load_agent():
    model = TransformersModel(
        model_id=MODEL_ID,
        device_map="auto",  # M-series GPU if available
        torch_dtype="auto",
        max_new_tokens=1024,
        temperature=0.2,
    )
    agent = CodeAgent(
        model=model,
        tools=all_tools,
        max_steps=5,
    )
    return agent


def main():
    st.set_page_config(page_title="Optimization Assistant", page_icon="🤖")
    st.title("🤖 Optimization Assistant")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Handle user input
    if prompt := st.chat_input("Ask about production planning..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Generate response
        with st.spinner("Thinking..."):
            try:
                agent = load_agent()
                # Use only the current prompt - no history
                response = agent.run(prompt)

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                st.chat_message("assistant").write(response)
            except Exception as e:
                st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()

# streamlit run agent2.py
