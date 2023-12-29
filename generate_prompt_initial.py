from langchain.schema.output_parser import StrOutputParser

from utils import save_tmp_file, extract_prompt_from_answer
from utils_multiline_table import df_to_multiline_table

from prompts.writep_few_shot.prompt import (
    get_prompt_template as get_few_shot_prompt_template,
)
from prompts.writep_zero_shot.prompt import (
    get_prompt_template as get_zero_shot_prompt_template,
)


class GeneratePromptInitial:
    def __init__(self, model, is_few_shot, df_sample, idea_seed, plan_id):
        """
        Initialize the LangChainEvaluator class.

        Args:
        model: LangChain model used for generating data.
        df_sample: The original DataFrame for comparison.
        idea_seed: Identifier for the idea seed being tested.
        plan_id: Identifier for the ToT (Tree of Thought plan) being tested.
        """
        self.model = model
        self.df_sample = df_sample
        self.idea_seed = idea_seed
        self.plan_id = plan_id

        self.prompt_template = (
            get_few_shot_prompt_template()
            if is_few_shot
            else get_zero_shot_prompt_template()
        )

    def get_chain(self):
        """
        Returns the LangChain chain.
        """
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    def invoke(self):
        save_tmp_file(
            f"02-plan-{self.plan_id}-prompt_init-(1).md",
            self.prompt_template.format_messages(
                dataset_samples_table=df_to_multiline_table(self.df_sample),
                idea_seed=self.idea_seed,
            ),
        )

        # Invoke the LangChain chain to generate the prompt
        print("Generating initial prompt...")
        answer = self.get_chain().invoke(
            {
                "dataset_samples_table": df_to_multiline_table(self.df_sample),
                "idea_seed": self.idea_seed,
            }
        )

        save_tmp_file(f"02-plan-{self.plan_id}-prompt_init-(2)-response.md", answer)

        # Extract the generated prompt
        prompt_generated_str = extract_prompt_from_answer(answer)
        prompt_generated_str = prompt_generated_str.replace(
            "%%%INPUT_TABLE%%%", "{input_table}"
        )

        return prompt_generated_str
