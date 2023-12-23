from utils import load_text_file
from langchain.prompts import ChatPromptTemplate

MESSAGES = [
    ("system", load_text_file("00-system.md")),
    ("human", load_text_file("01-human.md")),
    # ("ai", load_text_file("02-ai.md")),
    # ("human", load_text_file("03-human.md")),
]


def get_prompt_template():
    return ChatPromptTemplate.from_messages(MESSAGES)
