from utils import save_tmp_file
from utils_multiline_table import df_to_multiline_table, parse_multiline_table
from data_handling import chunk_dataframe

import pandas as pd
import concurrent.futures

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


def invoke_test_prompt_against_dataset(prompt_template, df, model, i_prompt, max_chunk_rows):
    # Set up the LangChain chain to use the generated prompt
    chain35 = prompt_template | model | StrOutputParser()

    # Split the dataset into chunks
    df_chunks = chunk_dataframe(df, max_chunk_rows)

    # Call the new function
    df_generated = process_chunks_and_aggregate(df_chunks, prompt_template, i_prompt, chain35)

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


def process_chunks_and_aggregate(df_chunks, prompt_template, i_prompt, chain):
    # Initialize an ordered dictionary to store results from each chunk
    chunk_list = []

    # Define the number of workers to use (maximum of 3)
    num_workers = min(len(df_chunks), 3)

    # Use a ThreadPoolExecutor to execute multiple chunks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(process_chunk_with_retry, prompt_template, i_prompt, chain, j, chunk):
                j for j, chunk in enumerate(df_chunks, start=1)
        }

        # Get the results from the completed Future instances
        for future in concurrent.futures.as_completed(futures):
            try:
                chunk_list.append(future.result())
            except Exception as exc:
                print(f"Processing chunk failed with exception: {exc}")

    # Concatenate the results from each chunk into a single DataFrame and sort
    df_generated = pd.concat(chunk_list)
    df_generated = df_generated.sort_values(by=["ROW_NO"]).reset_index(drop=True)

    return df_generated


def process_chunk_with_retry(prompt_template, i_prompt, chain, j, chunk, retries=2):
    for retry in range(retries):
        try:
            return process_chunk(prompt_template, i_prompt, chain, j, chunk, retry=retry)
        except Exception as e:
            print("Retrying...", e)

    raise ValueError(f"Failed to process chunk {j} after {retries} retries")


def process_chunk(prompt_template, i_prompt, chain35, j, chunk, retry=0):
    print(f"Getting chunk {j} with {len(chunk)} rows...")
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
