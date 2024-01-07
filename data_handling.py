import pandas as pd


def load_and_clean_dataset(file_path):
    """
    Load the dataset from a CSV or XLSX file and drop the first column
    if it's a sequential index.

    Args:
    file_path (str): The path to the dataset file.

    Returns:
    DataFrame: The cleaned Pandas DataFrame.
    """
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path, sep=",", encoding="utf-8")
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(
            "Unsupported file format. Only CSV and XLSX files are supported."
        )

    # If the first column is a sequential index, drop it
    first_column = df.columns[0]
    if pd.api.types.is_integer_dtype(df[first_column]):
        df = df.sort_values(by=first_column).reset_index(drop=True)
        difference = df[first_column] - df.index - 1

        if difference.nunique() == 1:
            df = df.drop(first_column, axis=1)

    # Add a ROW_NO column if it doesn't exist, add to beginning of DataFrame
    if "ROW_NO" not in df.columns:
        df.insert(0, "ROW_NO", range(1, 1 + len(df)))

    return df


def chunk_dataframe(df, chunk_size):
    """
    Split a DataFrame into chunks of a specified maximum size.

    Args:
    df (DataFrame): The original DataFrame.
    chunk_size (int): The maximum number of rows in each chunk.

    Returns:
    list[DataFrame]: A list of DataFrames, each with a maximum
        of chunk_size rows.
    """

    return [
        df[i : i + chunk_size] for i in range(0, df.shape[0], chunk_size)  # noqa: E203
    ]


def get_input_columns(df):
    """
    Returns a list of column names that contain the word "input".
    """
    # Get all columns that have 'input' in their name
    input_columns = [column for column in df.columns if "input" in column.lower()]
    return input_columns


def get_output_column_name(df):
    """
    Returns the name of the output column.

    Raises:
    ValueError: If no 'output' column is found.

    Returns:
    str: The name of the output column.
    """
    # Find the name of the 'OUTPUT' column
    for column in df.columns:
        if "output" in column.lower():
            return column

    raise ValueError("No 'output' column found in the DataFrame.")


def get_df_incorrect_answers(df_generated):
    """
    Returns a DataFrame containing only the incorrect answers.

    Args:
    df_generated (DataFrame): The generated DataFrame from the EvaluateAgainstDataset class.

    Returns:
    DataFrame: A DataFrame containing only the incorrect answers.
    """
    # Filter df_generated to only include incorrect answers
    df_incorrect = df_generated[~df_generated["Is Correct?"]].reset_index(drop=True)
    # Drop the column `Thinking step by step`, if it exists
    if "Thinking step by step" in df_incorrect.columns:
        df_incorrect = df_incorrect.drop(columns=["Thinking step by step"])

    return df_incorrect
