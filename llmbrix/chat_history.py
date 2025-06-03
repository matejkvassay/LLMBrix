from collections import deque

from llmbrix.msg import AssistantMsg, SystemMsg, ToolOutputMsg, ToolRequestMsg, UserMsg
from llmbrix.msg.msg import Msg


class ChatHistory:
    """
    Contains chat message history.
    - enables adding and retrieval of last k messages from chat history
    - internally works on level of conversation turns (turn starts with user msg).
    - it makes sure user, assistant message and related tool messages are kept and removed consistently together.
    - automatically removes oldest conversation turns as new ones above "max_turns" limit are added
    - keeps system message always as first message in the chat history (if system message provided)

    Note on FIFO message trimming:
        - this strategy of history trimming might not be optimal for caching
        - adding new conversation turn above limit of "max_turns" results in immediate
          removal of oldest conversation turn
        - for caching it's necessary to leave the oldest messages for as long as possible and then
          suddenly trim multiple outdated messages (see caching in OpenAI docs)
        - there is tradeoff though because even though it makes cached tokens cheaper you still pay for them
    """

    def __init__(self, max_turns: int = 5):
        """
        :param max_turns: int, maximum number of conversation turns.
                         Conversation turns always starts with each new user message and contains all subsequent
                         non-user messages.
                         If this limit of conversation turns stored is exceeded the oldest turns are automatically
                         trimmed from the chat history.
                         System message is not part of any conversation turn and doesn't count into the max_turns limit.
        """
        self.system_msg = None
        self.max_turns = max_turns
        self._conv_turns: deque[_ConversationTurn] = deque(maxlen=max_turns)

    def add(self, msg: Msg):
        """
        Add new message to chat history.

        System message has to be added first (optionally).
        Other messages are automatically turned into bundles and increase bundle count.

        :param msg: Message of any type.
        """
        if isinstance(msg, SystemMsg):
            self.system_msg = msg
        elif isinstance(msg, UserMsg):
            self._conv_turns.append(_ConversationTurn(user_msg=msg))
        elif isinstance(msg, (AssistantMsg, ToolRequestMsg, ToolOutputMsg)):
            if len(self._conv_turns) == 0:
                raise ValueError("Conversation must start with a UserMsg.")
            self._conv_turns[-1].add_followup_message(msg)
        else:
            raise TypeError(f"msg has to be Assistant/Tool/User message, got: {msg.__class__.__name__}")

    def add_many(self, msgs: list[Msg]):
        """
        Add multiple messages to chat history.

        :param msgs: List of messages of any type.
        """
        for m in msgs:
            self.add(m)

    def get(self, n=None) -> list[Msg]:
        """
        Retrieve messages from chat history.

        :param n: (optional) Number of latest conversation turns to retrieve messages from.
                  Note 1 conversation turn typically contains more than 1 message.

        :return: List of messages from n latest conversation turns.
        """
        messages = [self.system_msg] if self.system_msg else []
        turns = list(self._conv_turns)[-n:] if n is not None else self._conv_turns
        for turn in turns:
            messages += turn.flatten()
        return messages

    def count_conv_turns(self) -> int:
        """
        Get number of conversation turns stored in this chat history.
        System message is not included in this count (not part of conversation turn).

        :return: int number of conversation turns.
        """
        return len(self._conv_turns)

    def __len__(self):
        """
        Get number of messages stored in this chat history.
        System message is included in this count.

        :return: int number of stored messages
        """
        sys_count = 0 if self.system_msg is None else 1
        return sys_count + sum(len(t) for t in self._conv_turns)


class _ConversationTurn:
    """
    Represents one conversation turn.
    Conversation turn starts with user message and contains all subsequent non-user messages added to chat history.
    Not turn does not include system msg.
    """

    def __init__(self, user_msg: UserMsg):
        """
        :param user_msg: User message
        """
        self.user_msg = user_msg
        self.llm_responses: list[AssistantMsg | ToolRequestMsg | ToolOutputMsg] = []

    def add_followup_message(self, msg: AssistantMsg | ToolRequestMsg | ToolOutputMsg):
        """
        Add non-user follow-up message.

        :param msg: one of AssistantMsg | ToolRequestMsg | ToolOutputMsg
        """
        self.llm_responses.append(msg)

    def flatten(self) -> list[Msg]:
        """
        Return all messages from this conversation turn as a list.

        :return: List of messages.
        """
        return [self.user_msg] + self.llm_responses

    def __len__(self) -> int:
        """
        Get number of messages stored in this conversation turn.

        :return: int
        """
        return 1 + len(self.llm_responses)
