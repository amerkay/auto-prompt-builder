import re
import os
import inspect

from langchain.chat_models import ChatOpenAI
from langchain.llms import Together
from langchain_core.messages.base import BaseMessage
from langchain.callbacks.openai_info import OpenAICallbackHandler


def load_model(name, temperature, max_tokens):
    """
    Load model If MODEL_EVALUATE_NAME starts with `gpt-`, use ChatOpenAI,
    otherwise use Together.ai.

    Args:
        name (str): Model name
        temperature (float): Model temperature
        max_tokens (int): Model max tokens

    Returns:
        LangChainModel: LangChain model
    """
    if name.startswith("gpt-"):
        print(f"Loading ChatOpenAI model: {name}")
        model = ChatOpenAI(
            model=name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        print(f"Loading Together model: {name}")
        model = Together(
            model=name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    return model


def extract_prompt_from_answer(answer):
    """
    Extract the generated prompt from the LangChain answer.

    Args:
    answer (str): The response from the LangChain model.

    Returns:
    str: The extracted prompt or None if not found.
    """
    matches = re.findall(r"<prompt>(.*?)</prompt>", answer, re.DOTALL)
    if len(matches) == 1:
        return matches[0].strip()
    elif len(matches) > 1:
        raise ValueError("More than one match found")
    else:
        raise ValueError("No match found")


def extract_changes_made_from_answer(answer):
    """
    Extract the generated prompt from the LangChain answer.

    Args:
    answer (str): The response from the LangChain model.

    Returns:
    str: The extracted prompt or None if not found.
    """
    matches = re.findall(r"<changes_made>(.*?)</changes_made>", answer, re.DOTALL)
    if len(matches) == 1:
        return matches[0].strip()
    elif len(matches) > 1:
        raise ValueError("More than one match found")
    else:
        raise ValueError("No match found")


def save_log_file(filename, content, dir="_log"):
    """
    Saves the file `./_log/{filename}` with the specified content.

    Parameters:
    filename (str): The name of the file to be saved.
    content (str or list): The content to be written to the file.
        Can be list of BaseMessage objects.

    Returns:
    None
    """

    # Create the log directory if it doesn't exist
    os.makedirs(dir, exist_ok=True)

    # Define the full path for the file
    file_path = os.path.join(dir, filename)

    # Format content_str as JSON string if it is a list
    content_str = ""
    if isinstance(content, list):
        content_str = convert_messages_to_markdown(content)
    elif isinstance(content, str):
        content_str = content
    else:
        raise ValueError(f"Content is not a list or string: {content}")

    # Write the content to the file
    with open(file_path, "w") as file:
        file.write(content_str)


def convert_messages_to_markdown(messages):
    """
    Convert a list of BaseMessages to a string representation in Markdown format.

    Args:
        messages (list): A list of BaseMessage objects.

    Returns:
        str: A string representation of the messages in Markdown format.
    """
    messages_str = ""
    for message in messages:
        if isinstance(message, BaseMessage):
            messages_str += f"**{message.type}**:\n{message.content}"
            if message != messages[-1]:
                messages_str += "\n\n\n\n---\n\n\n\n"
        else:
            raise ValueError(f"Message is not an instance of BaseMessage: {message}")

    return messages_str


def load_text_file(filename):
    """
    Load a plaintext file and return its contents as a string.

    Parameters:
    filename (str): The name of the file to be loaded.

    Returns:
    str: The contents of the file.
    """
    # Get the frame of the caller
    caller_frame = inspect.stack()[1]
    caller_module = inspect.getmodule(caller_frame[0])

    # Ensure caller_module.__file__ is a string before proceeding
    if caller_module is not None and isinstance(caller_module.__file__, str):
        # Get the directory of the caller's file
        caller_dir = os.path.dirname(os.path.abspath(caller_module.__file__))
    else:
        # Default to the current working directory
        caller_dir = os.getcwd()

    # Construct the full file path
    full_file_path = os.path.join(caller_dir, filename)

    with open(full_file_path, "r") as file:
        return file.read()


def replace_percent_variables(
    prompt_generated_str, replacements=[("%%%INPUT_TABLE%%%", "{input_table}")]
):
    """
    Replaces percent variables in the prompt generated string with their corresponding replacements.

    Args:
        prompt_generated_str (str): The prompt generated string.
        replacements (list, optional): A list of tuples containing the percent variables and
        their replacements.
            Defaults to [("%%%INPUT_TABLE%%%", "{input_table}")].

    Returns:
        str: The prompt generated string with percent variables replaced.

    Raises:
        ValueError: If the prompt does not contain a percent variable, an error is raised.
    """
    for percent_str, replacement in replacements:
        # If the prompt does not contain the variable, raise error
        if percent_str not in prompt_generated_str:
            raise ValueError(
                f"Prompt does not contain the variable {percent_str}. "
                "Cannot replace the variable."
            )

        prompt_generated_str = prompt_generated_str.replace(percent_str, replacement)

    return prompt_generated_str


def print_cost(cb: OpenAICallbackHandler):
    """
    Prints the total cost and tokens used by the OpenAICallbackHandler.

    Parameters:
    cb (OpenAICallbackHandler): The OpenAICallbackHandler object.

    Returns:
    None
    """
    if cb.total_tokens > 0:
        print(f">> Total cost: {cb.total_cost:.3f} USD, tokens used {cb.total_tokens}")
