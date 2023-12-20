import re
import os


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


def save_tmp_file(filename, content_str, dir="_tmp"):
    """
    Saves the file `./_tmp/{filename}` with the specified content.

    Parameters:
    filename (str): The name of the file to be saved.
    content_str (str): The content to be written to the file.

    Returns:
    None
    """

    # Create the tmp directory if it doesn't exist
    os.makedirs(dir, exist_ok=True)

    # Define the full path for the file
    file_path = os.path.join(dir, filename)

    # Write the content to the file
    with open(file_path, "w") as file:
        file.write(content_str)
