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
    return [df[i: i + chunk_size] for i in range(0, df.shape[0], chunk_size)]
