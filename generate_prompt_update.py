from previous_attempts import PreviousAttempts
from utils import (
    save_tmp_file,
    extract_prompt_from_answer,
    extract_changes_made_from_answer,
)
from utils_multiline_table import df_to_multiline_table
from langchain.schema.output_parser import StrOutputParser
from prompts.updatep.prompt import get_prompt_template


class GeneratePromptUpdate:
    def __init__(
        self,
        model,
        i_prompt: int,
        plan_id: int,
        idea_seed: str,
        previous_attempts: PreviousAttempts,
        max_rows_incorrect: int,
    ):
        self.model = model
        self.i_prompt = i_prompt
        self.plan_id = plan_id
        self.idea_seed = idea_seed
        self.previous_attempts = previous_attempts
        self.max_rows_incorrect = max_rows_incorrect

        self.prompt_template = get_prompt_template()

    def get_chain(self):
        """
        Returns the LangChain chain.
        """
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    def invoke_with_retry(
        self,
        df_generated,
        prompt_previous,
        retries=3,
    ):
        for retry in range(retries):
            try:
                return self.invoke(
                    df_generated,
                    prompt_previous,
                    retry=retry,
                )
            except Exception as e:
                print(f"Error updating prompt: {e}")
                print(f"Retrying... ({retry + 1}/{retries})")

        raise ValueError(f"Failed to update prompt after {retries} retries")

    def invoke(self, df_generated, prompt_previous, retry=0):
        # Get the incorrect answers from the generated data
        df_incorrect = self.get_incorrect_answers(df_generated)

        # Invoke the LangChain chain to update the prompt
        print("Updating prompt...")
        prompt_updatep_str = self.prompt_template.format(
            current_prompt=prompt_previous,
            incorrect_answers_table=df_to_multiline_table(df_incorrect),
            previous_attempts=self.previous_attempts.to_string(),
            idea_seed=self.idea_seed,
        )
        # print("\n\n\n>> prompt_updatep is")
        # print(prompt_updatep_str, "\n\n")

        file_prefix = (
            f"04-updatep-plan-{self.plan_id}-attempt-{self.i_prompt}-retry-{retry}"
        )

        save_tmp_file(f"{file_prefix}-(1).md", prompt_updatep_str)

        answer_updatep = self.get_chain().invoke(
            {
                "current_prompt": prompt_previous,
                "incorrect_answers_table": df_to_multiline_table(df_incorrect),
                "previous_attempts": self.previous_attempts.to_string(),
                "idea_seed": self.idea_seed,
            }
        )
        save_tmp_file(f"{file_prefix}-(2)-response.md", answer_updatep)

        # Extract the updated prompt
        prompt_updated_str = extract_prompt_from_answer(answer_updatep)
        save_tmp_file(f"{file_prefix}-(3)-extracted.md", prompt_updated_str)

        changes_made_str = extract_changes_made_from_answer(answer_updatep)
        save_tmp_file(f"{file_prefix}-(4)-changes-made.md", changes_made_str)

        # print(f"\n\n>> prompt_updated_str is:", prompt_updated_str)

        return prompt_updated_str, changes_made_str

    def get_incorrect_answers(self, df_generated):
        max_rows = self.max_rows_incorrect

        # Filter df_generated to only include incorrect answers
        df_incorrect = df_generated[~df_generated["Is Correct?"]].reset_index(drop=True)

        print(f"Incorrect answers count: {len(df_incorrect)}")
        # print(df_to_multiline_table(df_incorrect), "\n")

        if max_rows > len(df_incorrect):
            max_rows = len(df_incorrect)
            print(f"Pick the first {max_rows} examples...")
            df_incorrect = df_incorrect.head(max_rows)
        else:
            print(f"Pick {max_rows} random incorrect examples...")
            df_incorrect = df_incorrect.sample(max_rows).reset_index(drop=True)

        # print(df_to_multiline_table(df_incorrect), "\n")

        return df_incorrect
