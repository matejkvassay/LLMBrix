from collections import deque

from llmbrix.msg import AssistantMsg, SystemMsg, ToolOutputMsg, ToolRequestMsg, UserMsg
from llmbrix.msg.msg import Msg


class ChatHistory:
    def __init__(self, max_turns: int = 5):
        self.system_msg = None
        self.max_turns = max_turns
        self.conv_turns: deque[_ConversationTurn] = deque(maxlen=max_turns)

    def add(self, msg: Msg):
        if isinstance(msg, SystemMsg):
            self.system_msg = msg
        elif isinstance(msg, UserMsg):
            self.conv_turns.append(_ConversationTurn(user_msg=msg))
        elif isinstance(msg, (AssistantMsg, ToolRequestMsg, ToolOutputMsg)):
            if len(self.conv_turns) == 0:
                raise ValueError("Conversation must start with a UserMsg.")
            self.conv_turns[-1].add_llm_response(msg)
        else:
            raise TypeError(
                f"msg has to be Assistant/Tool/User message, got: {msg.__class__.__name__}"
            )

    def add_many(self, msgs: list[Msg]):
        for m in msgs:
            self.add(m)

    def get(self, n=None) -> list[Msg]:
        messages = [self.system_msg] if self.system_msg else []
        turns = list(self.conv_turns)[-n:] if n is not None else self.conv_turns
        for turn in turns:
            messages += turn.flatten()
        return messages

    def __len__(self):
        return len(self.conv_turns)


class _ConversationTurn:
    def __init__(self, user_msg: UserMsg):
        self.user_msg = user_msg
        self.llm_responses: list[AssistantMsg | ToolRequestMsg | ToolOutputMsg] = []

    def add_llm_response(self, msg: AssistantMsg | ToolRequestMsg | ToolOutputMsg):
        self.llm_responses.append(msg)

    def flatten(self):
        return [self.user_msg] + self.llm_responses
