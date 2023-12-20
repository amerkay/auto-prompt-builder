from utils import save_tmp_file
from utils_multiline_table import df_to_multiline_table, parse_multiline_table
from config import ROWS_MAX
from data_handling import chunk_dataframe

import pandas as pd
from langchain.schema.output_parser import StrOutputParser


def calculate_accuracy(df_original, df_generated, output_column_name):
    """
    Calculate the accuracy of generated data compared to the original dataset.

    Args:
    df_original (DataFrame): The original DataFrame.
    df_generated (DataFrame): The DataFrame generated from LangChain.
    output_column_name (str): The name of the output column to compare.

    Returns:
    float: The accuracy percentage.
    """
    # Add the 'Truth' column to the generated DataFrame
    df_generated = df_generated.assign(Truth=df_original[output_column_name])

    if pd.api.types.is_numeric_dtype(df_generated["Truth"]):
        # Cast the output column to numeric if 'Truth' is numeric
        df_generated[output_column_name] = pd.to_numeric(
            df_generated[output_column_name], errors="coerce"
        )
        df_generated["Is Correct?"] = df_generated.apply(
            lambda row: abs(row[output_column_name] - row["Truth"]) <= 2, axis=1
        )
    else:
        df_generated["Is Correct?"] = (
            df_generated["Truth"].str.lower()
            == df_generated[output_column_name].str.lower()
        )

    # print(df_generated)

    # Calculate the accuracy
    accuracy = df_generated["Is Correct?"].sum() / len(df_generated) * 100

    return accuracy, df_generated


def invoke_test_prompt_against_dataset(prompt_template, df, model, i_prompt):
    # Set up the LangChain chain to use the generated prompt
    chain35 = prompt_template | model | StrOutputParser()

    # Split the dataset into chunks
    df_chunks = chunk_dataframe(df, ROWS_MAX)

    # List to store results from each chunk
    chunk_results = []

    j = 1

    # Iterate through each chunk and invoke the LangChain chain
    for chunk in df_chunks:
        # Process the chunk
        df_generated_chunk = None
        try:
            df_generated_chunk = process_chunk(
                prompt_template, i_prompt, chain35, j, chunk
            )
        except Exception as e:
            # try one more time
            print("Trying one more time...", e)
            df_generated_chunk = process_chunk(
                prompt_template, i_prompt, chain35, j, chunk, retry=1
            )

        # Add the processed chunk to the results list
        chunk_results.append(df_generated_chunk)
        # Increment the prompt counter
        j = j + 1

    # Now you can aggregate or process 'chunk_results' as needed
    # For example, to concatenate all chunks into a single DataFrame:
    df_generated = pd.concat(chunk_results, ignore_index=True)

    # Add columns with `input` in their name from df to df_generated
    for column in df.columns:
        if "input" in column.lower():
            df_generated[column] = df[column]

    # Calculate the accuracy of the generated data for the entire dataset
    # First, find the name of the output column
    output_column_name = None
    for column in df_generated.columns:
        if "output" in column.lower():
            output_column_name = column
            break

    accuracy, df_generated = calculate_accuracy(df, df_generated, output_column_name)
    print(f"Correct answers: {accuracy:.2f}%")

    return df_generated, accuracy


def process_chunk(prompt_template, i_prompt, chain35, j, chunk, retry=0):
    print(f"Getting answer, chunk of {len(chunk)} rows...")
    save_tmp_file(
        f"03-prompt-{i_prompt}-chunk-{j}-request.md",
        prompt_template.format(
            input_table=df_to_multiline_table(chunk, is_remove_output_field=True)
        ),
    )

    # spaces as many retry times
    retry_spaces = " " * retry

    answer_prompt_gen_chunk = chain35.invoke(
        {
            "input_table": df_to_multiline_table(chunk, is_remove_output_field=True)
            + retry_spaces
        }
    )
    save_tmp_file(
        f"03-prompt-{i_prompt}-chunk-{j}-response.md", answer_prompt_gen_chunk
    )

    df_generated_chunk = parse_multiline_table(
        answer_prompt_gen_chunk, expected_count=len(chunk)
    )

    return df_generated_chunk
