from operator import is_
from previous_attempts import PreviousAttempts, Attempt
from evaluate_against_dataset import EvaluateAgainstDataset
from generate_prompt_initial import GeneratePromptInitial
from generate_prompt_update import GeneratePromptUpdate
from dataset_mistake_tracking import DatasetMistakeTracking
from data_handling import get_df_incorrect_answers
from generate_expert_plans import GenerateExpertPlans
from best_prompt import BestPrompt


class BaseStrategy:
    """
    BaseStrategy is a class designed to automate the process of
    generating and evaluating prompts based on a dataset. It has common
    logic and methods to build strategies.
    """

    def __init__(
        self,
        model_prompt_writer,
        model_evaluate,
        df_original,
        idea_seed,
        goal_accuracy,
        max_attempts_per_plan,
        is_few_shot,
        eval_concurrency,
        rows_initial,
        rows_max,
        rows_incorrect,
        is_use_eval_aware_dataset=True,
    ):
        """
        Initializes the Strategy class with models, dataset, and configuration parameters.

        Args:
            model_prompt_writer (LanguageModel): Language model for prompt generation.
            model_evaluate (LanguageModel): Language model for prompt evaluation.
            df_original (pandas.DataFrame): The original dataset for evaluation.
            idea_seed (str): The seed idea for prompt generation.
            goal_accuracy (float): Target accuracy for the prompt.
            max_attempts_per_plan (int): Maximum number of attempts for each expert plan.
            is_few_shot (bool): Boolean indicating if the prompt generation should be few-shot.
            eval_concurrency (int): Level of concurrency for evaluation.
            rows_initial (int): Initial number of rows in the dataset.
            rows_max (int): Maximum number of rows in the dataset.
            rows_incorrect (int): Number of incorrect rows in the dataset.
            is_use_eval_aware_dataset (bool): Boolean indicating if the EvalAwareDataset should be used.

        Returns:
            None
        """
        self.model_prompt_writer = model_prompt_writer
        self.model_evaluate = model_evaluate
        self.df_original = df_original
        self.idea_seed = idea_seed
        self.goal_accuracy = goal_accuracy
        self.max_attempts_per_plan = max_attempts_per_plan
        self.is_few_shot = is_few_shot
        self.eval_concurrency = eval_concurrency
        self.rows_initial = rows_initial
        self.rows_max = rows_max
        self.rows_incorrect = rows_incorrect
        self.dataset_mistake_tracker = DatasetMistakeTracking(df_original)
        self.is_use_eval_aware_dataset = is_use_eval_aware_dataset

        self._init_evaluator()
        self._init_previous_attempts()
        self.best_prompt = BestPrompt()

    def _init_evaluator(self):
        """
        Initializes the evaluator with the original dataset.

        Returns:
            None
        """
        self.evaluator = EvaluateAgainstDataset(
            model=self.model_evaluate,
            df_original=self.df_original,
            max_chunk_rows=self.rows_max,
            concurrency=self.eval_concurrency,
        )

    def _init_previous_attempts(self):
        """
        Initializes the previous attempts with the original dataset.

        This method initializes the `previous_attempts` attribute with the original dataset length.
        It sets the `df_all_length` parameter of `PreviousAttempts` class to the length of `self.df_original`.

        Args:
            None

        Returns:
            None
        """
        self.attempt_no = 1
        self.previous_attempts = PreviousAttempts(df_all_length=len(self.df_original))

    def _generate_initial_prompt(self, plan):
        """
        Generates the initial prompt for a given expert plan.

        Args:
            plan_text (str): The text representation of the expert plan.

        Returns:
            str: The generated initial prompt string.
        """
        plan_text = plan.to_string(idea_seed=self.idea_seed)

        df_sample = self.dataset_mistake_tracker.get_sample(
            self.rows_initial, is_include_mistakes=self.is_use_eval_aware_dataset
        )
        gen_prompt_initial = GeneratePromptInitial(
            model=self.model_prompt_writer,
            is_few_shot=self.is_few_shot,
            df_sample=df_sample,
            idea_seed=plan_text,
            plan_id=plan.id,
        )
        return gen_prompt_initial.invoke()

    def _evaluate_prompt(self, prompt_str, plan_id):
        """
        Evaluates the generated prompt against the dataset.

        Args:
            prompt_str (str): The prompt string to be evaluated.
            plan_id (int): The ID of the plan.

        Returns:
            tuple: A tuple containing the generated dataframe and accuracy.
                The generated dataframe contains the results of the evaluation.
                The accuracy is a float value representing the accuracy of the evaluation.
        """
        df_generated, accuracy = self.evaluator.invoke(
            prompt_str=prompt_str, plan_id=plan_id, attempt_no=self.attempt_no
        )
        return df_generated, accuracy

    def _log_attempt(self, accuracy, prompt_str, plan, df_generated):
        """
        Logs each attempt, including the attempt number, accuracy, and changes made.

        Args:
            accuracy (float): The accuracy achieved in this attempt.
            prompt_str (str): The prompt string used in this attempt.
            plan (object): The plan associated with this attempt.
            df_generated (pandas.DataFrame): The dataframe generated from the last prompt evaluation.

        Returns:
            None
        """
        # Update best prompt (happens only if accuracy is higher than previous best)
        self.best_prompt.update(accuracy, prompt_str, plan)

        # Update the mistakes
        df_incorrect = get_df_incorrect_answers(df_generated)
        self.dataset_mistake_tracker.update_mistakes(df_incorrect)

    def _generate_expert_plans(self):
        """
        Generates expert plans using the GenerateExpertPlans class.

        Returns:
            The result of invoking the gen_expert_plans object.
        """
        gen_expert_plans = GenerateExpertPlans(
            model=self.model_prompt_writer,
            df_sample=self.dataset_mistake_tracker.get_sample(
                self.rows_initial, is_include_mistakes=self.is_use_eval_aware_dataset
            ),
            idea_seed=self.idea_seed,
        )
        return gen_expert_plans.invoke()

    def _update_prompt(self, df_generated, prompt_previous, plan):
        """
        Updates the prompt based on previous attempts and the current state of the dataset.

        Args:
            df_generated (pandas.DataFrame): The dataframe generated from the last prompt evaluation.
            prompt_previous (str): The previous prompt string.
            plan (Plan): The plan object.

        Returns:
            float: The accuracy achieved in this attempt.
        """
        self.attempt_no += 1
        plan_text = plan.to_string(idea_seed=self.idea_seed)

        # Generate the updated prompt
        gen_prompt_update = GeneratePromptUpdate(
            model=self.model_prompt_writer,
            attempt_no=self.attempt_no,
            idea_seed=plan_text,
            previous_attempts=self.previous_attempts,
            max_rows_incorrect=self.rows_incorrect,
            plan_id=plan.id,
        )
        # Invoke the LangChain chain to update the prompt
        prompt_str, changes_made_str = gen_prompt_update.invoke_with_retry(
            df_generated=df_generated, prompt_previous=prompt_previous
        )

        # Evaluate the updated prompt
        df_generated, accuracy = self._evaluate_prompt(prompt_str, plan.id)

        # Add attempt to previous attempts
        self.previous_attempts.add(Attempt(self.attempt_no, accuracy, changes_made_str))

        self._log_attempt(accuracy, prompt_str, plan, df_generated)

        print("\n---\n" + self.previous_attempts.to_string() + "---\n")

        return accuracy

    def _run_update_prompt_loop(
        self, plan, previous_accuracy, prompt_str, df_generated
    ):
        """
        Runs the update prompt loop to auto-magically improve the prompt until it
        reaches the goal accuracy or the maximum number of attempts is reached.

        Args:
            plan (Plan): The plan object.
            previous_accuracy (float): The previous accuracy of the prompt.
            prompt_str (str): The initial prompt string.
            df_generated (DataFrame): The generated data.

        Returns:
            float: The final accuracy of the prompt.
        """
        accuracy = previous_accuracy

        while (
            accuracy < self.goal_accuracy
            and self.attempt_no < self.max_attempts_per_plan
        ):
            accuracy = self._update_prompt(df_generated, prompt_str, plan)

        return accuracy

    def _run_plan_initial_prompt(self, plan, mutation=0):
        # Initiate the previous attempts list for this plan
        self._init_previous_attempts()

        # The plan
        mutation_spaces = " " * mutation
        plan_text = plan.to_string(idea_seed=self.idea_seed) + mutation_spaces
        print(f"\n==============\n==============\n\nPlan {plan.id}:\n{plan_text}\n")

        # Generate the initial prompt for this plan
        prompt_str = self._generate_initial_prompt(plan)

        # Evaluate the initial prompt
        df_generated, accuracy = self._evaluate_prompt(prompt_str, plan.id)

        # Add first attempt to previous attempts
        self.previous_attempts.add(Attempt(self.attempt_no, accuracy, "First attempt."))

        self._log_attempt(accuracy, prompt_str, plan, df_generated)

        return accuracy, prompt_str, df_generated

    def run(self):
        """
        The main method to run the iterative process of generating, evaluating,
        and updating prompts until the best prompt is found.

        Returns:
            Tuple: The best prompt. `return self.best_prompt.get_best_prompt()`.
            A tuple containing the best prompt, its accuracy, and the associated plan.
        """
        raise NotImplementedError
        # return self.best_prompt.get_best_prompt()
