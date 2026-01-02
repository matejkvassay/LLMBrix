from typing import Optional

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
        if tools:
            self.tool_executor = ToolExecutor(tools=tools, max_workers=max_workers, timeout=tool_timeout)
        if loop_limit < 1:
            raise ValueError("Loop limit must be greater than 0")
        self.loop_limit = loop_limit

    def chat(
        self,
        text: str | list[BaseMsg],
        images: Optional[list[PIL.Image.Image]] = None,
        files: Optional[list[tuple[bytes, UserMsgFileTypes]]] = None,
        youtube_url: Optional[str] = None,
        gcs_uris: Optional[list[tuple[str, UserMsgFileTypes]]] = None,
    ) -> ModelMsg:
        """
        Executes one turn of chat. If history is set in constructor it will be updated with all messages.

        Note this method might execute multiple iteration of tool calls and save all messages into chat history if set.

        It will however return only last ModelMsg containing final response from the model.

        Args:
            text: Text input from user.
            images: List of PIL images to pass to LLM.
            files: List of tuples of (byte, type) representing files to be uploaded to LLM.
            youtube_url: Youtube video URL to be parsed.
            gcs_uris: List of tuple (URI, mime type) for files to be read from GCS.

        Returns: ModelMsg from final answer of the model.
        """
        user_msg = UserMsg(text=text, images=images, files=files, youtube_url=youtube_url, gcs_uris=gcs_uris)
        if self.chat_history:
            messages_hist = self.chat_history.get()
        else:
            messages_hist = []
        new_messages = [user_msg]
        tool_iter = 1
        model_msg = None
        while tool_iter <= self.loop_limit:
            model_msg = self.gemini_model.generate(
                messages=messages_hist + new_messages,
                system_instruction=self.system_instruction,
                disable_tools=tool_iter == self.loop_limit,
            )
            new_messages.append(model_msg)
            if model_msg.tool_calls:
                new_messages += self.tool_executor.execute(model_msg.tool_calls)
        if self.chat_history:
            self.chat_history.insert(new_messages)
        return model_msg
