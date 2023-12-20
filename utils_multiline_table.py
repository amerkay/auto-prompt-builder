import re
import pandas as pd


def df_to_multiline_table(df, is_remove_output_field=False):
    """
    Convert a pandas DataFrame to a multiline table format.

    Args:
        df (pandas.DataFrame): The DataFrame to convert.
        is_remove_output_field (bool, optional): Whether to remove the output
            field from the table. Defaults to False.

    Returns:
        str: The multiline table representation of the DataFrame.
    """
    result = ""
    for index, row in df.iterrows():
        result += "___START_OF_ROW___\n"
        if "ROW_NO" not in df.columns:
            result += "`ROW_NO`: " + str(index) + "\n"
        for column in df.columns:
            # skip output field if is_remove_output_field is True
            if is_remove_output_field and "output" in column.lower():
                continue

            result += "`" + column + "`: \n"
            result += str(row[column]) + "\n"
        result += "___END_OF_ROW___\n\n"
    return result


def parse_multiline_table(response_str, expected_count=None):
    """
    Parse a multi-line table into a Pandas DataFrame.

    Args:
    response_str (str): Multi-line table text.
    expected_count (int, optional): The expected number of rows.
        Defaults to None.

    Returns:
    DataFrame: Pandas DataFrame created from the multi-line table.
    """
    # Pattern to match each row
    row_pattern = r"___START_OF_ROW___(.*?)___END_OF_ROW___"
    # Extract all rows
    rows = re.findall(row_pattern, response_str, re.DOTALL)

    # Check if the expected count matches (if provided)
    if expected_count is not None and len(rows) != expected_count:
        error_message = (
            "Number of rows does not match the expected count. "
            "Expected {expected_count} rows, got {len(rows)}."
        )
        raise ValueError(error_message)

    # Parse each row into a dictionary
    data = []
    for row in rows:
        # Extract key-value pairs
        pairs = re.findall(r"`(.*?)`:(.*?)\n(?=`|$)", row, re.DOTALL)
        row_data = {key.strip(): value.strip() for key, value in pairs}
        data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data)
    return df
