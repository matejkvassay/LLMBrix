from llmbrix.msg import AssistantMsg, SystemMsg, ToolMsg, UserMsg
from llmbrix.base.msg_base import MsgBase


class ConvTurn:
    def __init__(self, user_msg: UserMsg):
        self.user_msg = user_msg
        self.llm_responses: list[AssistantMsg | ToolMsg] = []

    def add_llm_response(self, msg: AssistantMsg | ToolMsg):
        self.llm_responses.append(msg)

    def flatten(self):
        res = [self.user_msg]
        if len(self.llm_responses) > 0:
            res += self.llm_responses
        return res


class ConvTurnHist:
    def __init__(self, system_msg: SystemMsg, max_turns: int = 5):
        self.system_msg = system_msg
        self.max_turns = max_turns
        self.conv_turns: list[ConvTurn] = []

    def add(self, msg: MsgBase):
        if isinstance(msg, SystemMsg):
            raise ValueError("System message has to be set in constructor of ConversationHistory.")
        elif isinstance(msg, UserMsg):
            self.conv_turns.append(ConvTurn(user_msg=msg))
        elif isinstance(msg, AssistantMsg) or isinstance(msg, ToolMsg):
            if len(self) == 0:
                raise ValueError(
                    "At least 1 user message has to be added first"
                    " before follow-up assistant/tool messages."
                )
            self.conv_turns[-1].add_llm_response(msg)
        else:
            raise TypeError(
                f"msg has to be Assistant/Tool/User message, got: {msg.__class__.__name__}"
            )
        self._trim()

    def add_many(self, msgs: list[MsgBase]):
        for m in msgs:
            self.add(m)

    def get(self):
        res = [self.system_msg]
        for turn in self.conv_turns:
            res += turn.flatten()
        return res

    def _trim(self):
        self.conv_turns = self.conv_turns[-self.max_turns :]

    def __len__(self):
        return len(self.conv_turns)
