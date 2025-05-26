from openai import OpenAI
from openai.types.responses import ResponseFunctionToolCall

from llmbrix.msg import AssistantMsg, Msg
from llmbrix.tool import Tool

client = OpenAI()


class GptOpenAI:
    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI()

    def generate(self, messages: list[Msg], tools: list[Tool] = None) -> AssistantMsg:
        messages = [m.to_openai() for m in messages]
        if tools is not None:
            tools = [t.openai_schema for t in tools]
        else:
            tools = []
        response = self.client.responses.create(input=messages, model=self.model, tools=tools)
        if response.error:
            raise RuntimeError(
                f"Error during OpenAI API cal: "
                f"code={response.error}, "
                f'msg="{response.error.message}"'
            )
        tool_calls = [t for t in response.output if isinstance(t, ResponseFunctionToolCall)]
        tool_calls = tool_calls if tool_calls else None
        return AssistantMsg(content=response.output_text, tool_calls=tool_calls)

    # def generate_structured(self, messages: list[Msg], output_format: Type[BaseModel],
    #                         tools: list[Tool] = None) -> BaseModel:
    #     messages = [m.to_openai() for m in messages]
    #     if tools is not None:
    #         tools = [t.openai_schema for t in tools]
    #     else:
    #         tools = []
    #
    #     response = self.client.responses.parse(
    #         input=messages,
    #         model=self.model,
    #         tools=tools,
    #         text_format=output_format
    #     )
    #
    #     return response.output_parsed
