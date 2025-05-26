from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import AssistantMsg, SystemMsg, UserMsg
from llmbrix.tool_executor import DEFAULT_TOOL_ERROR_TEMPLATE, ToolExecutor
from llmbrix.tools import Tool


class Agent:
    def __init__(
        self,
        gpt: GptOpenAI,
        system_msg: SystemMsg,
        chat_history: ChatHistory,
        tools: list[Tool] | None = None,
        tool_call_iter_limit=1,
        tool_err_template=DEFAULT_TOOL_ERROR_TEMPLATE,
    ):
        assert tool_call_iter_limit > 0
        self.gpt = gpt
        self.tool_executor = ToolExecutor(tools=tools, error_template=tool_err_template)
        self.chat_history = chat_history
        self.chat_history.add(system_msg)
        self.tools = tools
        self.tool_call_iter_limit = tool_call_iter_limit

    def chat(self, user_msg: UserMsg) -> AssistantMsg:
        self.chat_history.add(user_msg)

        for _ in range(self.tool_call_iter_limit):
            assistant_msg = self.gpt.generate(messages=self.chat_history.get(), tools=self.tools)
            self.chat_history.add(assistant_msg)
            if not assistant_msg.tool_calls:
                return assistant_msg
            tool_msgs = self.tool_executor(assistant_msg.tool_calls)
            self.chat_history.add_many(tool_msgs)

        assistant_msg = self.gpt.generate(messages=self.chat_history.get(), tools=None)
        self.chat_history.add(assistant_msg)
        return assistant_msg
