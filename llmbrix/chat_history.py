from collections import deque

from llmbrix.msg import BaseMsg, ModelMsg, ToolMsg, UserMsg


class ChatHistory:
    """
    Contains chat message history with automatically applied trimming based on number conversation turns.
    Each new user message begins new conversation turn.
    Note this strategy of message trimming might not optimally leverage Gemini API caching.
    """

    def __init__(self, max_turns: int = 5):
        """
        Args:
            max_turns: Maximum number of conversation turns stored in this conversation history.
                       Limit is applied automatically when messages are added.
                       Each conversation turn starts with UserMsg and contains subsequent related
                       ModelMsg/ToolMsg objects.
        """
        self.max_turns = max_turns
        self._conv_turns: deque[_ConversationTurn] = deque(maxlen=max_turns)

    def insert(self, message: BaseMsg):
        """
        Add a message to the conversation history.
        If UserMsg is added, new conversation turn is started.
        If other msg is added its appended to latest conversation turn.

        Args:
            message: BaseMsg instance.
        """
        if isinstance(message, UserMsg):
            self._conv_turns.append(_ConversationTurn(user_msg=message))
        elif isinstance(message, (ToolMsg, ModelMsg)):
            if len(self._conv_turns) == 0:
                raise ValueError("Conversation must start with a UserMsg.")
            self._conv_turns[-1].add_followup_message(message)
        else:
            raise TypeError(f"Message has to be one of [ModelMsg, ToolMsg, UserMsg], got: {type(message)}")

    def insert_batch(self, messages: list[BaseMsg]):
        """
        Add multiple messages to the conversation history.
        Args:
            messages: List of BaseMsg instances.
        """
        for m in messages:
            self.insert(m)

    def get(self, n=None) -> list[BaseMsg]:
        """
        Fetch messages from conversation history.
        If

        Args:
            n: Number of last conversation turns to fetch messages from.

        Returns: List of messages from chat history.

        """
        turns = list(self._conv_turns)
        if n is not None:
            start_index = max(0, len(turns) - n)
            turns = turns[start_index:]
        return [msg for turn in turns for msg in turn.flatten()]

    def pop(self) -> list[BaseMsg]:
        """
        Remove and return messages from the last conversation turn.
        Useful for "undo" operations.

        Returns: List of messages from the last conversation turn.
        """
        if self.count_conversation_turns() > 0:
            return self._conv_turns.pop().flatten()
        return []

    def count_conversation_turns(self) -> int:
        """
        Count number of conversation turns stored in this conversation history.

        Returns: Number of conversation turns stored.
        """
        return len(self._conv_turns)

    def count_messages(self):
        """
        Count how many messages are stored in this conversation history.

        Returns: Number of messages stored.
        """
        return sum(len(t) for t in self._conv_turns)

    def __len__(self):
        """
        Count how many messages are stored in this conversation history.

        Returns: Number of messages stored.
        """
        return self.count_messages()


class _ConversationTurn:
    """
    Hold messages for a single conversation turn.
    Conversation turn starts with user message and contains all subsequent non-user messages added to chat history.
    """

    def __init__(self, user_msg: UserMsg):
        self.user_msg = user_msg
        self.llm_responses: list[ModelMsg | ToolMsg] = []

    def add_followup_message(self, msg: ModelMsg | ToolMsg):
        self.llm_responses.append(msg)

    def flatten(self) -> list[BaseMsg]:
        return [self.user_msg] + self.llm_responses

    def __len__(self) -> int:
        return 1 + len(self.llm_responses)
