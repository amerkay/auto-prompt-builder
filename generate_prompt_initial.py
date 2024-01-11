from langchain.schema.output_parser import StrOutputParser
from langchain.callbacks import get_openai_callback

from utils import save_log_file, extract_prompt_from_answer, replace_percent_variables, print_cost
from utils_xml_table import df_to_xml_table

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
        """
        Invokes the LangChain chain to generate the prompt.
        """

        variables = {
            "dataset_samples_table": df_to_xml_table(self.df_sample),
            "idea_seed": self.idea_seed,
        }

        # Format the prompt
        print("Generating initial prompt...")
        prompt_formatted = self.prompt_template.format(**variables)

        # Define the file prefix
        file_prefix = f"02-plan-{self.plan_id}-prompt_init"

        save_log_file(f"{file_prefix}-(1).md", prompt_formatted)

        # Invoke the LangChain chain to generate the prompt
        answer = None
        with get_openai_callback() as cb:
            answer = self.get_chain().invoke(variables)
            print_cost(cb)

        save_log_file(f"{file_prefix}-(2)-response.md", answer)

        # Extract the generated prompt
        prompt_generated_str = extract_prompt_from_answer(answer)
        prompt_generated_str = replace_percent_variables(prompt_generated_str)

        return prompt_generated_str
