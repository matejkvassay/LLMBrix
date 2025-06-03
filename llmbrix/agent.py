from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import AssistantMsg, SystemMsg, UserMsg
from llmbrix.tool import Tool
from llmbrix.tool_executor import ToolExecutor


class Agent:
    """
    Tool calling LLM Chatbot Agent.

    Takes request from user, calls LLM, executes tool calls and answers to the user.
    Internally operates chat history to store and remember messages.

    Operates in ReAct fashion with multiple tool call iterations.
    """

    def __init__(
        self,
        gpt: GptOpenAI,
        chat_history: ChatHistory,
        system_msg: SystemMsg = None,
        tools: list[Tool] | None = None,
        max_tool_call_iter=1,
    ):
        """
        :param gpt: Instance of GptOpenAI LLM wrapper.
        :param chat_history: ChatHistory instance. Will be used to store new messages (both user and agent produced).
                             If passed chat history is not empty it will be used and system_mgs argument will be
                             ignored. Can be used to restore agent form previous state.
        :param system_msg: System message to set up general agent instructions.
                           Optional but highly recommended.
                           Ignored if chat_history passed already contains some messages.
        :param tools: List of tools to register to the chatbot agent. Agent will decide on its own to use these tools
                      when needed to answer user's question.
        :param max_tool_call_iter: Maximum number of tool call loops Agent is allowed to do.
                                   Each loop can include multiple tool calls. Agent can decide to repeat tool calls
                                   if context to answer user's question was not successfully provided or the answer
                                   requires multiple subsequent tool calls.
        """
        assert max_tool_call_iter > 0
        self.gpt = gpt
        self.chat_history = chat_history
        if (len(self.chat_history) == 0) and (system_msg is not None):
            self.chat_history.add(system_msg)
        self.tools = tools
        if tools:
            self.tool_executor = ToolExecutor(tools=tools)
        self.max_tool_call_iter = max_tool_call_iter

    def chat(self, user_msg: UserMsg) -> AssistantMsg:
        """
        Executes new turn of conversation.
        Can add multiple messages in chat history - tool calls, tool outputs, assistant message.

        :param user_msg: UserMsg containing user's response / question/
        :return: AssistantMsg instance containing final answer from LLM
        """
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
