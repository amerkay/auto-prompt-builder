class Attempt:
    attempt_no: int
    accuracy: float
    changes_made: str

    def __init__(self, attempt_no, accuracy, changes_made):
        self.attempt_no = attempt_no
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
            result += f"### Attempt {a.attempt_no}: {a.accuracy:.2f}% accuracy"
            result += f" ({count_wrong} wrong out of {self.df_all_length} test rows)\n"

            if a.attempt_no > 1:
                result += f"Changes made to the prompt compared to attempt {a.attempt_no - 1}:\n"

            result += f"{a.changes_made}\n"

        return result
