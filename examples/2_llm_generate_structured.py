import os

from openai import OpenAI
from pydantic import BaseModel

from llmbrix.gpt_openai import GptOpenAI
from llmbrix.gpt_response import GptResponse
from llmbrix.msg import SystemMsg, UserMsg

"""
Generate answer with OpenAI GPT model.
"""

MODEL = "gpt-5-mini"
SYSTEM_MSG = "You name 3 colors that are most similar to color from user."
USER_MSG = "I chooose yellow!"


class SelectedColor(BaseModel):
    users_color: str
    most_similar_colors: list[str]


messages = [SystemMsg(content=SYSTEM_MSG), UserMsg(content=USER_MSG)]
gpt = GptOpenAI(model=MODEL, openai_client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
output: GptResponse = gpt.generate(messages, output_format=SelectedColor)
messages.append(output.message)

for m in messages:
    print(f"\n\n{m.role.upper()}:")
    print(m.content)

print("\n\nPARSED: ")
p = output.message.content_parsed
print(f'VAL="{p}", TYPE="{type(p)}"')
