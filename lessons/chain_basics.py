import argparse

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from cashbot.llm import complete
from cashbot.settings import ensure_dirs

parser = argparse.ArgumentParser()
parser.add_argument("--live", action="store_true")
parser.add_argument("--provider", choices=["openai", "anthropic"], default="openai")
args = parser.parse_args()
ensure_dirs()

# 1. A prompt template turns variables into messages.
prompt = ChatPromptTemplate.from_messages([
    ("system", "Explain business bookkeeping in plain English. Do not invent legal rules."),
    ("human", "Explain {topic} in two sentences.")
])

# 2. A Runnable is a component with an invoke() interface.
# The fixture lets you learn chaining without paying for an API call.
def fixture_model(prompt_value):
    print("Messages sent to the model:", len(prompt_value.to_messages()))
    return AIMessage(content="A partial payment settles part of an amount owed. Record the payment and keep the remaining balance visible.")

model = RunnableLambda((lambda value: complete(value, args.provider)) if args.live else fixture_model)

# 3. The pipe operator | sends each step's output into the next step.
chain = prompt | model | StrOutputParser()
print(chain.invoke({"topic": "a partial customer payment"}))
