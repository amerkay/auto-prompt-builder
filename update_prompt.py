from utils import (
    save_tmp_file,
    extract_prompt_from_answer,
    extract_changes_made_from_answer,
)
from utils_multiline_table import df_to_multiline_table
from config import IDEA_SEED, ROWS_INCORRECT, PROMPT_UPDATE_FILE

from langchain.prompts import load_prompt
from langchain.schema.output_parser import StrOutputParser


def invoke_update_prompt(
    df_generated, prompt_previous, model, previous_attempts_str, i_prompt
):
    # Get the incorrect answers from the generated data
    df_incorrect = get_incorrect_answers(df_generated)

    # Load the prompt to update the generated prompt
    prompt_updatep = load_prompt(PROMPT_UPDATE_FILE)
    chain_updatep = prompt_updatep | model | StrOutputParser()

    # Invoke the LangChain chain to update the prompt
    print("Updating prompt using gpt-4-turbo...")
    prompt_updatep_str = prompt_updatep.format(
        current_prompt=prompt_previous,
        incorrect_answers_table=df_to_multiline_table(df_incorrect),
        previous_attempts=previous_attempts_str,
        idea_seed=IDEA_SEED,
    )
    # print("\n\n\n>> prompt_updatep is")
    # print(prompt_updatep_str, "\n\n")
    save_tmp_file(f"04-prompt_updatep-{i_prompt}.md", prompt_updatep_str)

    answer_updatep = chain_updatep.invoke(
        {
            "current_prompt": prompt_previous,
            "incorrect_answers_table": df_to_multiline_table(df_incorrect),
            "previous_attempts": previous_attempts_str,
            "idea_seed": IDEA_SEED,
        }
    )
    save_tmp_file(f"05-prompt_updatep-{i_prompt}-response.md", answer_updatep)

    # if "TRUTH_IS_WRONG" in answer_updatep:
    #     print(f"\n>>", answer_updatep)
    #     raise ValueError("TRUTH_IS_WRONG")

    # Extract the updated prompt
    prompt_updated_str = extract_prompt_from_answer(answer_updatep)
    save_tmp_file(f"06-prompt_updatep-{i_prompt}-extracted.md", prompt_updated_str)

    changes_made_str = extract_changes_made_from_answer(answer_updatep)
    save_tmp_file(f"06-prompt_updatep-{i_prompt}-changes-made.md", changes_made_str)

    # print(f"\n\n>> prompt_updated_str is:", prompt_updated_str)

    return prompt_updated_str, changes_made_str


def get_incorrect_answers(df_generated):
    # Filter df_generated to only include incorrect answers
    df_incorrect = df_generated[~df_generated["Is Correct?"]].reset_index(drop=True)

    print(f"Incorrect answers count: {len(df_incorrect)}")
    # print(df_to_multiline_table(df_incorrect), "\n")

    print(f"Pick the first {int(ROWS_INCORRECT)} examples...")
    df_incorrect = df_incorrect.head(ROWS_INCORRECT)
    # df_incorrect = df_incorrect.sample(ROWS_INCORRECT).reset_index(drop=True)
    # print(df_to_multiline_table(df_incorrect), "\n")

    return df_incorrect


def previous_attempts_add(previous_attempts, i_prompt, accuracy, changes_made_str):
    previous_attempts.append(
        {
            "i_prompt": i_prompt,
            "accuracy": accuracy,
            "changes_made": changes_made_str,
        }
    )


def previous_attempts_to_str(previous_attempts, df_all):
    if len(previous_attempts) == 0:
        return "No previous attempts."

    result = ""
    for a in previous_attempts:
        count_wrong = len(df_all) - int(len(df_all) * a["accuracy"] / 100)
        result += f"### Attempt {a['i_prompt']}: {a['accuracy']:.2f}% accuracy"
        result += f" ({count_wrong} wrong out of {len(df_all)} test rows)\n"
        result += f"Changes made:\n{a['changes_made']}\n\n"

    return result
