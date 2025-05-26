from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import AssistantMsg, SystemMsg, UserMsg
from llmbrix.tool_executor import ToolExecutor
from llmbrix.tools import Tool


class Agent:
    def __init__(
        self,
        gpt: GptOpenAI,
        system_msg: SystemMsg,
        chat_history: ChatHistory,
        tools: list[Tool] | None = None,
        max_tool_call_iter=1,
    ):
        assert max_tool_call_iter > 0
        self.gpt = gpt
        self.chat_history = chat_history
        self.chat_history.add(system_msg)
        self.tools = tools
        if tools:
            self.tool_executor = ToolExecutor(tools=tools)
        self.max_tool_call_iter = max_tool_call_iter

    def chat(self, user_msg: UserMsg) -> AssistantMsg:
        self.chat_history.add(user_msg)

        for _ in range(self.max_tool_call_iter):
            assistant_msg = self.gpt.generate(messages=self.chat_history.get(), tools=self.tools)
            self.chat_history.add(assistant_msg)
            if not assistant_msg.tool_calls:
                return assistant_msg
            tool_msgs = self.tool_executor(assistant_msg.tool_calls)
            self.chat_history.add_many(tool_msgs)

        assistant_msg = self.gpt.generate(messages=self.chat_history.get(), tools=None)
        self.chat_history.add(assistant_msg)
        return assistant_msg
