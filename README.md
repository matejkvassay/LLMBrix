# About

Low abstraction LLM framework focused on simple chat / agentic applications.

Supports only Gemini API.

In early alpha development.

# Install

```bash
pip install llmbrix
```

# Example usage

(see `llmbrix/examples/simple_chatbot/`)

```python
import dotenv

from llmbrix.chat_history import ChatHistory
from llmbrix.gemini_model import GeminiModel
from llmbrix.tool_agent import ToolAgent
from llmbrix.tools import CalculatorTool, DatetimeTool

dotenv.load_dotenv()

model = GeminiModel(model="gemini-2.5-flash-lite")
chat_history = ChatHistory(max_turns=5)

agent = ToolAgent(
    gemini_model=model,
    system_instruction="You are Kevin, super brief to the point chatbot assistant. Speak in corporate words.",
    chat_history=ChatHistory(max_turns=5),
    tools=[CalculatorTool(), DatetimeTool()],
    loop_limit=2,
    tool_timeout=30,
    max_workers=2,
)


def start_chat():
    print("--- Kevin is online! (Type 'exit' or 'quit' to stop) ---")

    while True:
        user_text = input("You: ")
        if user_text.lower() in ["exit", "quit"]:
            response = agent.chat("I'm leaving, see you!")
            print(f"Kevin: {response.text}")
            break
        try:
            for agent_msg in agent.chat_iter(user_text):
                if agent_msg.is_model() and agent_msg.text:
                    print(f"Kevin: {agent_msg.text}")
                elif agent_msg.is_tool():
                    print(f"Kevin used tool: {agent_msg.tool_name} with args: {agent_msg.tool_args}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    start_chat()

```
