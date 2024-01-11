import re
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom


def extract_table(s):
    """
    Extracts the XML table string from the input string.

    The function searches for a string that starts with `<table_` and ends with `</table_`,
    capturing everything in between. If more than one table is found, it raises a ValueError.

    Args:
        s (str): The input string to search for the XML table string.

    Returns:
        str: The XML table string if found, otherwise an empty string.

    Raises:
        ValueError: If more than one table is found in the input string.

    Example:
        >>> extract_table('This is the answer: <table_output>...</table_output> You are welcome!')
        '<table_output>...</table_output>'
    """
    matches = re.findall("<table_.*?>.*?</table_.*?>", s, re.DOTALL)
    if len(matches) > 1:
        raise ValueError("More than one table found in the input string.")
    return matches[0] if matches else ""


def slugify_column_names(df):
    """
    Slugify column names of a DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame whose column names to slugify.

    Returns:
        pandas.DataFrame: The DataFrame with slugified column names.
    """

    def clean_column_name(name):
        # Remove special characters but keep spaces
        name = re.sub(r"[^\w\s]", "", name)
        # Replace spaces with underscores
        name = re.sub(r"\s+", "_", name)
        return name

    df.columns = [clean_column_name(col) for col in df.columns]
    return df


def df_to_xml_table(df, is_remove_output_field=False):
    """
    Convert a pandas DataFrame to an indented XML format without XML declaration.

    Args:
        df (pandas.DataFrame): The DataFrame to convert.
        is_remove_output_field (bool, optional): Whether to remove the output
            field from the XML. Defaults to False.

    Returns:
        str: The indented XML representation of the DataFrame without the XML declaration.
    """

    def prettify(elem):
        """Return a pretty-printed XML string for the Element, excluding the XML declaration."""
        rough_string = ET.tostring(elem, "unicode")
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="    ")
        # Split the string into lines and return joined string skipping the first line
        return "\n".join(pretty_string.split("\n")[1:])

    df = slugify_column_names(df)

    root = ET.Element("rows")
    for index, row in df.iterrows():
        row_elem = ET.SubElement(root, "row")
        for column in df.columns:
            # skip output field if is_remove_output_field is True
            if is_remove_output_field and "output" in column.lower():
                continue

            col_elem = ET.SubElement(row_elem, column)
            col_elem.text = str(row[column])

    return prettify(root).strip()


def parse_xml_table(response_str, expected_count=None):
    """
    Parse XML rows enclosed within <table_output> and <rows> tags into a Pandas DataFrame.

    Args:
        response_str (str): XML rows text.
        expected_count (int, optional): The expected number of rows.
            Defaults to None.

    Returns:
        DataFrame: Pandas DataFrame created from the XML rows.
    """
    # Extract XML string for the table
    table_str = extract_table(response_str)

    # Parse the XML string
    root = ET.fromstring(table_str)

    # Find the <rows> element
    rows_elem = root.find("rows")
    if rows_elem is None:
        raise ValueError("The XML does not contain <rows> element.")

    data = []
    for row_elem in rows_elem.findall("row"):
        row_data = {}
        for child in row_elem:
            row_data[child.tag] = child.text
        data.append(row_data)

    df = pd.DataFrame(data)

    # Check if the expected count matches (if provided)
    if expected_count is not None and len(df) != expected_count:
        error_message = (
            "Number of rows does not match the expected count. "
            f"Expected {expected_count} rows, got {len(df)}. "
            "Increase the MODEL_EVALUATE_MAX_TOKENS parameter?"
        )
        raise ValueError(error_message)

    return df
