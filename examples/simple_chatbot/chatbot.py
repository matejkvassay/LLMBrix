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
    system_instruction="You are Kevin, chatbot assistant that does fun joke puns in every response.",
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
            response = agent.chat(user_text)
            print(f"Kevin: {response.text}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    start_chat()
