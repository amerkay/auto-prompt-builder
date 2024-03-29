from previous_attempts import PreviousAttempts
from data_handling import get_df_incorrect_answers
from utils import (
    save_log_file,
    extract_prompt_from_answer,
    extract_changes_made_from_answer,
    print_cost,
    replace_percent_variables
)
from utils_xml_table import df_to_xml_table
from langchain.schema.output_parser import StrOutputParser
from prompts.updatep.prompt import get_prompt_template
from langchain.callbacks import get_openai_callback


class GeneratePromptUpdate:
    def __init__(
        self,
        model,
        attempt_no: int,
        plan_id: int,
        idea_seed: str,
        previous_attempts: PreviousAttempts,
        max_rows_incorrect: int,
    ):
        self.model = model
        self.attempt_no = attempt_no
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
        retries=2,
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

        # spaces as many retry times
        retry_spaces = " " * retry

        variables = {
            "current_prompt": prompt_previous.replace("{input_table}", "%%%INPUT_TABLE%%%"),
            "incorrect_answers_table": df_to_xml_table(df_incorrect),
            "previous_attempts": self.previous_attempts.to_string(),
            "idea_seed": self.idea_seed + retry_spaces,
        }

        # Invoke the LangChain chain to update the prompt
        print("\nUpdating prompt...")
        prompt_updatep_str = self.prompt_template.format(**variables)

        # print("\n\n\n>> prompt_updatep is")
        # print(prompt_updatep_str, "\n\n")

        file_prefix = (
            f"04-updatep-plan-{self.plan_id}-attempt-{self.attempt_no}-retry-{retry}"
        )

        save_log_file(f"{file_prefix}-(1).md", prompt_updatep_str)

        answer = None
        with get_openai_callback() as cb:
            answer = self.get_chain().invoke(variables)
            print_cost(cb)

        save_log_file(f"{file_prefix}-(2)-response.md", answer)

        # Extract the updated prompt
        prompt_updated_str = extract_prompt_from_answer(answer)
        save_log_file(f"{file_prefix}-(3)-extracted.md", prompt_updated_str)

        changes_made_str = extract_changes_made_from_answer(answer)
        save_log_file(f"{file_prefix}-(4)-changes-made.md", changes_made_str)

        prompt_updated_str = replace_percent_variables(prompt_updated_str)

        # print(f"\n\n>> prompt_updated_str is:", prompt_updated_str)
        return prompt_updated_str, changes_made_str

    def get_incorrect_answers(self, df_generated):

        # Filter df_generated to only include incorrect answers
        df_incorrect = get_df_incorrect_answers(df_generated)
        print(f"Incorrect answers count: {len(df_incorrect)}")

        max_rows = self.max_rows_incorrect
        if max_rows >= len(df_incorrect):
            max_rows = len(df_incorrect)
            print(f"Pick the first {max_rows} incorrect examples...")
            df_incorrect = df_incorrect.head(max_rows)
        else:
            print(f"Pick {max_rows} random incorrect examples...")
            df_incorrect = df_incorrect.sample(max_rows, random_state=42)
            df_incorrect = df_incorrect.reset_index(drop=True)

        return df_incorrect
