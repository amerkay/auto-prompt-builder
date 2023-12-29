class Attempt:
    i_prompt: int
    accuracy: float
    changes_made: str

    def __init__(self, i_prompt, accuracy, changes_made):
        self.i_prompt = i_prompt
        self.accuracy = accuracy
        self.changes_made = changes_made


class PreviousAttempts:
    def __init__(self, df_all_length=0):
        self.df_all_length = df_all_length
        self.previous_attempts = []

    def add(self, attempt: Attempt):
        self.previous_attempts.append(attempt)

    def to_string(self):
        if len(self.previous_attempts) == 0:
            return "No previous attempts."

        result = ""
        for a in self.previous_attempts:
            count_wrong = self.df_all_length - int(
                self.df_all_length * a.accuracy / 100
            )
            result += f"### Attempt {a.i_prompt}: {a.accuracy:.2f}% accuracy"
            result += f" ({count_wrong} wrong out of {self.df_all_length} test rows)\n"

            if a.i_prompt > 1:
                result += f"Changes made to the prompt compared to attempt {a.i_prompt - 1}:\n"

            result += f"{a.changes_made}\n"

        return result
