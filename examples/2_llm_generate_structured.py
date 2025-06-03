from pydantic import BaseModel

from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import SystemMsg, UserMsg

"""
Generate answer with OpenAI GPT model.
"""

MODEL = "gpt-4o-mini"
SYSTEM_MSG = "You name 3 colors that are most similar to color from user."
USER_MSG = "I chooose yellow!"


class OutputModel(BaseModel):
    users_color: str
    most_similar_colors: list[str]


messages = [SystemMsg(content=SYSTEM_MSG), UserMsg(content=USER_MSG)]
gpt = GptOpenAI(model=MODEL)
output: OutputModel = gpt.generate_structured(messages, output_format=OutputModel)

print(messages)
print(output)
