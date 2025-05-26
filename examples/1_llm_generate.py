from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import SystemMsg, UserMsg

"""
Generate answer with OpenAI GPT model.
"""

MODEL = "gpt-4o-mini"
SYSTEM_MSG = "You answer in pure Python code, no explanations."
USER_MSG = "Compute how many items in 2 int arrays are present in both."

messages = [SystemMsg(content=SYSTEM_MSG), UserMsg(content=USER_MSG)]
gpt = GptOpenAI(model=MODEL)
response = gpt.generate(messages)

messages.append(response.message)
print(messages)
