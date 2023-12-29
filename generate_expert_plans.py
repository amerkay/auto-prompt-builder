from typing import List

import json
from langchain.schema.output_parser import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

from utils import save_tmp_file
from utils_multiline_table import df_to_multiline_table
from prompts.expert_plans.prompt import get_prompt_template


class GenerateExpertPlans:
    def __init__(self, model, df_sample, idea_seed):
        """
        Initialize the LangChainEvaluator class.

        Args:
        model: LangChain model used for generating data.
        prompt_init_template: Template for the prompt to use with LangChain.
        df_sample: The original DataFrame for comparison.
        idea_seed: Identifier for the idea seed being tested.
        plan_id: Identifier for the ToT (Tree of Thought plan) being tested.
        """
        self.model = model
        self.df_sample = df_sample
        self.idea_seed = idea_seed
        self.prompt_template = get_prompt_template()

    def get_chain(self):
        """
        Returns the LangChain chain.
        """

        chain = self.prompt_template | self.model
        return chain

    def invoke(self):
        # Set up a parsers + chain
        output_parser = PydanticOutputParser(pydantic_object=ExpertPlans)
        output_parser_str = StrOutputParser()
        chain = self.get_chain()

        save_tmp_file(
            "01-prompt_tot-(1).md",
            self.prompt_template.format_messages(
                dataset_samples_table=df_to_multiline_table(self.df_sample),
                idea_seed=self.idea_seed,
            ),
        )

        # Invoke the LangChain chain to generate the prompt
        print("Generating 5 ranked ToT prompt construction plans...")
        answer = chain.invoke(
            {
                "dataset_samples_table": df_to_multiline_table(self.df_sample),
                "idea_seed": self.idea_seed,
            }
        )

        answer_str = output_parser_str.parse(answer.content)
        save_tmp_file("01-prompt_tot-(2)-response.md", answer_str)

        # Parse response
        answer_obj = output_parser.parse(answer.content)
        save_tmp_file("01-prompt_tot-(3)-parsed.md", answer_obj.to_json())

        # answer_dict = answer_obj.to_dict()
        # return self.reorder_plans(
        #     answer_dict["expert_prompt_plans"], answer_dict["ranked_plans"]
        # )
        return self.reorder_plans(
            answer_obj.expert_prompt_plans, answer_obj.ranked_plans
        )

    def reorder_plans(self, expert_prompt_plans, ranked_plans):
        """
        Reorders the expert prompt plans based on the ranking in ranked_plans.

        Args:
            expert_prompt_plans (list): List of expert prompt plans.
            ranked_plans (list): List of plan IDs in the desired order.

        Returns:
            list: Reordered list of expert prompt plans.
        """
        # Create a dictionary for quick lookup of plans by their id
        plan_dict = {plan.id: plan for plan in expert_prompt_plans}

        # Reorder the plans based on the ranking in ranked_plans
        reordered_plans = [plan_dict[id] for id in ranked_plans]

        return reordered_plans


# Define the structure for each expert's plan
class ExpertPlan(BaseModel):
    """
    Represents an expert's plan.

    Attributes:
        id (int): Plan ID.
        expert_title (str): Expert's title.
        plan (str): Expert's plan.
    """

    id: int = Field(description="Plan ID")
    expert_title: str = Field(description="Expert's title")
    plan: str = Field(description="Expert's plan")

    def to_dict(self):
        return self.dict()

    def to_string(self, idea_seed=None):
        # if idea_seed ends with `.`, remove it.
        idea_seed = idea_seed.rstrip(".") + ". " if idea_seed else ""
        return f"{idea_seed}{self.plan}"


class ExpertPlans(BaseModel):
    """
    Represents a collection of expert plans.

    Attributes:
        expert_prompt_plans (List[ExpertPlan]): List of experts and their plans.
        ranked_plans (List[int]): Ranked prompt plans.
    """

    expert_prompt_plans: List[ExpertPlan] = Field(
        description="List of experts and their plans"
    )
    ranked_plans: List[int] = Field(description="Ranked prompt plans")

    # Method to convert the instance to a dictionary
    def to_dict(self):
        return self.dict()

    # Method to get JSON representation
    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
