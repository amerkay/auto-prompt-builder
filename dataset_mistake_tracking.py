import pandas as pd


class DatasetMistakeTracking:
    def __init__(self, df_all):
        """
        Initialize the DatasetWithMistakeTracking.

        :param df_all: DataFrame, the full dataset with a 'ROW_NO' column and input/output columns.
        """
        self.df_all = df_all
        self.df_previous_mistakes = pd.DataFrame(columns=["ROW_NO", "count"])

    def update_mistakes(self, df_new_mistakes):
        """
        Update the tracking of mistakes.

        :param df_new_mistakes: DataFrame, containing 'ROW_NO' of new mistakes.
        """
        for row_no in df_new_mistakes["ROW_NO"]:
            row_no = int(row_no)
            if row_no in self.df_previous_mistakes["ROW_NO"].values:
                self.df_previous_mistakes.loc[
                    self.df_previous_mistakes["ROW_NO"] == row_no, "count"
                ] += 1
            else:
                new_row = pd.DataFrame({"ROW_NO": [row_no], "count": [1]})
                self.df_previous_mistakes = pd.concat(
                    [self.df_previous_mistakes, new_row], ignore_index=True
                )

    def get_sample(self, max_rows, is_include_mistakes=True):
        """
        Generate a sample dataset including previous mistakes.

        :param max_rows: int, maximum number of rows to return.
        :return: DataFrame, a sample of the dataset.
        """
        if is_include_mistakes:
            # Get rows with the highest mistake count, then fill in the rest with the top rows
            high_priority_mistakes = self._get_high_priority_mistakes(max_rows)
            remaining_rows = max_rows - len(high_priority_mistakes)
            sample = self._get_sample(remaining_rows)
            return pd.concat([high_priority_mistakes, sample])
        else:
            # Get a sample excluding high priority mistakes
            return self._get_sample(max_rows)

    def _get_high_priority_mistakes(self, max_rows):
        """
        Get rows with the highest mistake count.

        :param max_rows: int, maximum number of rows to consider for high priority mistakes.
        :return: DataFrame, rows with high mistake counts.
        """
        mistakes_sorted = self.df_previous_mistakes.sort_values(
            by="count", ascending=False
        )
        high_priority_row_nos = mistakes_sorted.head(max_rows)["ROW_NO"]
        return self.df_all[self.df_all["ROW_NO"].isin(high_priority_row_nos)]

    def _get_sample(self, num_rows):
        """
        Get a sample from the dataset excluding high priority mistakes.

        :param num_rows: int, number of rows to sample.
        :return: DataFrame, a sample of the dataset.
        """
        if num_rows <= 0:
            return pd.DataFrame()

        df_remaining = self.df_all[
            ~self.df_all["ROW_NO"].isin(self.df_previous_mistakes["ROW_NO"])
        ]

        return df_remaining.head(num_rows)


# Example usage
# df_all = pd.read_csv('your_dataset.csv')  # Assuming your dataset is in a CSV file
# dataset_mistake_tracker = DatasetWithMistakeTracking(df_all)
# df_new_mistakes = pd.DataFrame({'ROW_NO': [1, 2, 3]})  # Example new mistakes
# dataset_mistake_tracker.update_mistakes(df_new_mistakes)
# sample_with_mistakes = dataset_mistake_tracker.get_sample(10)
