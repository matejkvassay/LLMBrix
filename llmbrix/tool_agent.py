from typing import Iterator, Optional

import PIL.Image

from llmbrix.chat_history import ChatHistory
from llmbrix.gemini_model import GeminiModel
from llmbrix.msg import BaseMsg, ModelMsg, UserMsg, UserMsgFileTypes
from llmbrix.tool_calling import BaseTool, ToolExecutor


class ToolAgent:
    """
    Tool calling agent. Can either act as a chatbot or single turn agent.
    """

    def __init__(
        self,
        gemini_model: GeminiModel,
        system_instruction: str,
        chat_history: Optional[ChatHistory] = None,
        tools: Optional[list[BaseTool]] = None,
        loop_limit: int = 3,
        tool_timeout: int = 120,
        max_workers: int = 4,
    ):
        """
        Args:
            gemini_model: Gemini model. System instruction will be overridden on runtime with the one passed here.
            system_instruction: System instruction to be used for the agent.
            chat_history: Chat history containing previous messages.
            tools: List of LLM tools.
            loop_limit: Maximum number of iterations LLM can do when tool calling. 1 iteration = 1 call of LLM.
            tool_timeout: Maximum timeout to set for single tool execution.
            max_workers: Number of threads to use for tool execution.
        """
        self.gemini_model = gemini_model
        self.system_instruction = system_instruction
        self.chat_history = chat_history
        self.tool_executor = None
        self.tools = tools
        if tools:
            self.tool_executor = ToolExecutor(tools=tools, max_workers=max_workers, timeout=tool_timeout)
        if loop_limit < 1:
            raise ValueError("Loop limit must be greater than 0")
        self.loop_limit = loop_limit

    def chat(
        self,
        user_input: str | UserMsg,
        images: Optional[list[PIL.Image.Image]] = None,
        files: Optional[list[tuple[bytes, UserMsgFileTypes]]] = None,
        youtube_url: Optional[str] = None,
        gcs_uris: Optional[list[tuple[str, UserMsgFileTypes]]] = None,
    ) -> ModelMsg:
        """
        Executes one turn of chat and returns only the final response of the model.
        Chat history will also be updated with new messages if provided in constructor.

        Args:
            user_input:
                If str is passed it will be used as text input from user, other args will be used as well if provided.
                If UserMsg is passed then other args will be ignored and this instance of UserMsg will be used as input.
            images: List of PIL images to pass to LLM.
            files: List of tuples of (byte, type) representing files to be uploaded to LLM.
            youtube_url: Youtube video URL to be parsed.
            gcs_uris: List of tuple (URI, mime type) for files to be read from GCS.

        Returns: Final ModelMsg with agent's answer.
        """
        msg = None
        for msg in self.chat_iter(
            user_input=user_input, images=images, files=files, youtube_url=youtube_url, gcs_uris=gcs_uris
        ):
            pass
        if isinstance(msg, ModelMsg):
            return msg
        raise RuntimeError("Agent failed to produce a ModelMsg as the last response.")

    def chat_iter(
        self,
        user_input: str | UserMsg,
        images: Optional[list[PIL.Image.Image]] = None,
        files: Optional[list[tuple[bytes, UserMsgFileTypes]]] = None,
        youtube_url: Optional[str] = None,
        gcs_uris: Optional[list[tuple[str, UserMsgFileTypes]]] = None,
    ) -> Iterator[BaseMsg]:
        """
        Executes one turn of chat and provides iterator over all produced messages (User, Model & Tool messages).
        Chat history will also be updated with new messages if provided in constructor.

        Args:
            user_input:
                If str is passed it will be used as text input from user, other args will be used as well if provided.
                If UserMsg is passed then other args will be ignored and this instance of UserMsg will be used as input.
            images: List of PIL images to pass to LLM.
            files: List of tuples of (byte, type) representing files to be uploaded to LLM.
            youtube_url: Youtube video URL to be parsed.
            gcs_uris: List of tuple (URI, mime type) for files to be read from GCS.

        Returns: Iterator over all BaseMsg objects (User, Model & ToolMsg) produced during this chat turn execution.
        """
        user_msg = user_input
        if isinstance(user_msg, UserMsg):
            if images or files or youtube_url or gcs_uris:
                raise ValueError(
                    "Cannot combine multimodal inputs (image, file,...) with UserMsg user_input."
                    "Either pass user_input as str or set all inputs inside UserMsg object."
                )
        else:
            user_msg = UserMsg(text=user_input, images=images, files=files, youtube_url=youtube_url, gcs_uris=gcs_uris)
        if self.chat_history:
            messages_hist = self.chat_history.get()
        else:
            messages_hist = []
        yield user_msg
        new_messages: list[BaseMsg] = [user_msg]
        iteration = 1
        model_msg = None
        while iteration <= self.loop_limit:
            current_tools = self.tools if not (iteration == self.loop_limit) else None
            model_msg = self.gemini_model.generate(
                messages=messages_hist + new_messages, tools=current_tools, system_instruction=self.system_instruction
            )
            yield model_msg
            new_messages.append(model_msg)
            if model_msg.tool_calls:
                if not current_tools:
                    raise ValueError("Model hallucinated tool calls when no tools were provided.")
                for tool_msg in self.tool_executor.execute_iter(model_msg.tool_calls):
                    yield tool_msg
                    new_messages.append(tool_msg)
                iteration += 1
            else:
                break
        if self.chat_history:
            self.chat_history.insert_batch(new_messages)
        return model_msg
