from utils import (
    save_tmp_file,
    extract_prompt_from_answer,
    extract_changes_made_from_answer,
)
from utils_multiline_table import df_to_multiline_table
from langchain.schema.output_parser import StrOutputParser


def invoke_update_prompt_with_retry(
    prompt_template,
    df_generated,
    prompt_previous,
    model,
    previous_attempts_str,
    i_prompt,
    max_rows_incorrect,
    idea_seed,
    retries=3
):
    for retry in range(retries):
        try:
            return invoke_update_prompt(
                prompt_template,
                df_generated,
                prompt_previous,
                model,
                previous_attempts_str,
                i_prompt,
                max_rows_incorrect,
                idea_seed,
                retry=retry
            )
        except Exception as e:
            print(f"Error updating prompt: {e}")
            print(f"Retrying... ({retry + 1}/{retries})")

    raise ValueError(f"Failed to update prompt after {retries} retries")


def invoke_update_prompt(
    prompt_template,
    df_generated,
    prompt_previous,
    model,
    previous_attempts_str,
    i_prompt,
    max_rows_incorrect,
    idea_seed,
    retry=0
):
    # Get the incorrect answers from the generated data
    df_incorrect = get_incorrect_answers(df_generated, max_rows_incorrect)

    # Load the prompt to update the generated prompt
    chain_updatep = prompt_template | model | StrOutputParser()

    # Invoke the LangChain chain to update the prompt
    print("Updating prompt...")
    prompt_updatep_str = prompt_template.format(
        current_prompt=prompt_previous,
        incorrect_answers_table=df_to_multiline_table(df_incorrect),
        previous_attempts=previous_attempts_str,
        idea_seed=idea_seed,
    )
    # print("\n\n\n>> prompt_updatep is")
    # print(prompt_updatep_str, "\n\n")
    save_tmp_file(f"04-prompt_updatep-{i_prompt}-retry-{retry}.md", prompt_updatep_str)

    answer_updatep = chain_updatep.invoke(
        {
            "current_prompt": prompt_previous,
            "incorrect_answers_table": df_to_multiline_table(df_incorrect),
            "previous_attempts": previous_attempts_str,
            "idea_seed": idea_seed,
        }
    )
    save_tmp_file(f"05-prompt_updatep-{i_prompt}-retry-{retry}-response.md", answer_updatep)

    # Extract the updated prompt
    prompt_updated_str = extract_prompt_from_answer(answer_updatep)
    save_tmp_file(
        f"06-prompt_updatep-{i_prompt}-retry-{retry}-extracted.md", prompt_updated_str)

    changes_made_str = extract_changes_made_from_answer(answer_updatep)
    save_tmp_file(
        f"06-prompt_updatep-{i_prompt}-retry-{retry}-changes-made.md", changes_made_str)

    # print(f"\n\n>> prompt_updated_str is:", prompt_updated_str)

    return prompt_updated_str, changes_made_str


def get_incorrect_answers(df_generated, max_rows):
    # Filter df_generated to only include incorrect answers
    df_incorrect = df_generated[~df_generated["Is Correct?"]].reset_index(drop=True)

    print(f"Incorrect answers count: {len(df_incorrect)}")
    # print(df_to_multiline_table(df_incorrect), "\n")

    # max_rows = min(max_rows, len(df_incorrect))

    if max_rows > len(df_incorrect):
        max_rows = len(df_incorrect)
        print(f"Pick the first {max_rows} examples...")
        df_incorrect = df_incorrect.head(max_rows)
    else:
        print(f"Pick {max_rows} random incorrect examples...")
        df_incorrect = df_incorrect.sample(max_rows).reset_index(drop=True)

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

        if a['i_prompt'] > 1:
            result += f"Changes made to the prompt compared to attempt {a['i_prompt'] - 1}:\n"

        result += f"{a['changes_made']}\n\n"

    return result
