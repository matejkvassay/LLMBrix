from llmbrix.chat.gpt_openai import LLM
from llmbrix.conv_hist import ConvTurnHist
from llmbrix.msg import AssistantMsg, SystemMsg, UserMsg
from llmbrix.tools import Tool
from llmbrix.tools.tool_executor import DEFAULT_TOOL_ERROR_TEMPLATE, ToolExecutor


class Agent:
    def __init__(
        self,
        gpt: LLM,
        system_msg: SystemMsg,
        tools: list[Tool] | None = None,
        conv_hist_limit=5,
        tool_call_iter_limit=1,
        tool_err_template=DEFAULT_TOOL_ERROR_TEMPLATE,
    ):
        self.gpt = gpt
        self.tool_executor = ToolExecutor(tools=tools, error_template=tool_err_template)
        self.conv_hist = ConvTurnHist(system_msg=system_msg, max_turns=conv_hist_limit)
        self.tools = tools
        self.max_iter = tool_call_iter_limit

    def chat(self, user_msg: UserMsg) -> AssistantMsg:
        self.conv_hist.add(user_msg)
        assistant_msg = self.gpt.generate(messages=self.conv_hist.get(), tools=self.tools, n=1)
        self.conv_hist.add(assistant_msg)

        n_iter = 1
        while (assistant_msg.tool_calls is not None) and n_iter <= self.max_iter:
            tool_msgs = self.tool_executor(assistant_msg.tool_calls)
            self.conv_hist.add_many(tool_msgs)
            assistant_msg = self.gpt.generate(messages=self.conv_hist.get(), tools=self.tools, n=1)

            if n_iter == self.max_iter:
                assistant_msg.tool_calls = None

            self.conv_hist.add(assistant_msg)
            n_iter += 1
        return assistant_msg
