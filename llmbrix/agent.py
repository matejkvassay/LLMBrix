from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import AssistantMsg, SystemMsg, UserMsg
from llmbrix.tool import Tool
from llmbrix.tool_executor import ToolExecutor


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
            gpt_response = self.gpt.generate(messages=self.chat_history.get(), tools=self.tools)
            self.chat_history.add(gpt_response.message)
            if not gpt_response.tool_calls:
                return gpt_response.message
            self.chat_history.add_many(gpt_response.tool_calls)
            tool_output_msgs = self.tool_executor(gpt_response.tool_calls)
            self.chat_history.add_many(tool_output_msgs)

        gpt_response = self.gpt.generate(messages=self.chat_history.get(), tools=None)
        self.chat_history.add(gpt_response.message)
        return gpt_response.message
