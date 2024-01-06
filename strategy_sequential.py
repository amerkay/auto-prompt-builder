from previous_attempts import PreviousAttempts, Attempt
from evaluate_against_dataset import EvaluateAgainstDataset
from generate_prompt_initial import GeneratePromptInitial
from generate_prompt_update import GeneratePromptUpdate
from eval_aware_dataset import EvalAwareDataset
from data_handling import get_df_incorrect_answers
from generate_expert_plans import GenerateExpertPlans
from best_prompt import BestPrompt


class AutoPromptSequentialStrategy:
    """
    AutoPromptSequentialStrategy is a class designed to automate the process of
    generating and evaluating prompts based on a dataset. It iteratively generates
    prompts using expert plans, evaluates them, and updates them based on the feedback
    until a desired accuracy is achieved or a maximum number of attempts is reached.
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
    ):
        """
        Initializes the AutoPromptSequentialStrategy class with models, dataset,
        and configuration parameters.

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
        self.dataset_tracker = EvalAwareDataset(df_original)

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
        self.previous_attempts = PreviousAttempts(df_all_length=len(self.df_original))

    def _generate_initial_prompt(self, plan_text):
        """
        Generates the initial prompt for a given expert plan.

        Args:
            plan_text (str): The text representation of the expert plan.

        Returns:
            str: The generated initial prompt string.
        """
        df_sample = self.dataset_tracker.get_sample(self.rows_initial)
        gen_prompt_initial = GeneratePromptInitial(
            model=self.model_prompt_writer,
            is_few_shot=self.is_few_shot,
            df_sample=df_sample,
            idea_seed=plan_text,
            plan_id="plan_id_placeholder",  # Placeholder for plan ID
        )
        return gen_prompt_initial.invoke()

    def _evaluate_prompt(self, prompt_str, attempt_no, plan_id):
        """
        Evaluates the generated prompt against the dataset.

        Args:
            prompt_str (str): The prompt string to be evaluated.
            attempt_no (int): The attempt number for this evaluation.
            plan_id (int): The ID of the plan.

        Returns:
            tuple: A tuple containing the generated dataframe and accuracy.
                The generated dataframe contains the results of the evaluation.
                The accuracy is a float value representing the accuracy of the evaluation.
        """
        df_generated, accuracy = self.evaluator.invoke(
            prompt_str=prompt_str, plan_id=plan_id, attempt_no=attempt_no
        )
        return df_generated, accuracy

    def _update_prompt(
        self, df_generated, prompt_previous, plan_text, attempt_no, plan_id
    ):
        """
        Updates the prompt based on previous attempts and the current state of the dataset.

        Args:
            df_generated (pandas.DataFrame): The dataframe generated from the last prompt evaluation.
            prompt_previous (str): The previous prompt string.
            plan_text (str): The text representation of the current expert plan.
            attempt_no (int): The attempt number for this update.
            plan_id (int): The ID of the plan.

        Returns:
            tuple: A tuple containing the updated prompt string and the changes made.
        """
        gen_prompt_update = GeneratePromptUpdate(
            model=self.model_prompt_writer,
            attempt_no=attempt_no,
            idea_seed=plan_text,
            previous_attempts=self.previous_attempts,
            max_rows_incorrect=self.rows_incorrect,
            plan_id=plan_id,
        )
        return gen_prompt_update.invoke_with_retry(
            df_generated=df_generated, prompt_previous=prompt_previous
        )

    def _log_attempt(self, attempt_no, accuracy, changes_made, prompt_str):
        """
        Logs each attempt, including the attempt number, accuracy, and changes made.

        Args:
            attempt_no (int): The attempt number.
            accuracy (float): The accuracy achieved in this attempt.
            changes_made (str): Description of the changes made in this attempt.
            prompt_str (str): The prompt string used in this attempt.

        Returns:
            None
        """
        self.previous_attempts.add(
            Attempt(attempt_no=attempt_no, accuracy=accuracy, changes_made=changes_made)
        )
        self.best_prompt.update(accuracy, prompt_str)

    def _generate_expert_plans(self):
        """Generates expert plans using the GenerateExpertPlans class.

        Returns:
            The result of invoking the gen_expert_plans object.
        """
        gen_expert_plans = GenerateExpertPlans(
            model=self.model_prompt_writer,
            df_sample=self.dataset_tracker.get_sample(self.rows_initial),
            idea_seed=self.idea_seed,
        )
        return gen_expert_plans.invoke()

    def run(self):
        """
        The main method to run the iterative process of generating, evaluating,
        and updating prompts based on expert plans.

        Returns:
            Tuple: A tuple containing the best prompt and its accuracy.
        """
        # Generate and rank expert plans
        ranked_expert_plans = self._generate_expert_plans()

        prompt_str, accuracy = None, 0  # Default values

        # Loop through each expert plan
        for i, plan in enumerate(ranked_expert_plans):
            # if plan.id != 5:
            #     continue

            # The prompt counter used for the main loop
            attempt_no = 1

            # initiate the previous attempts list for this plan
            self._init_previous_attempts()

            # The plan
            plan_text = plan.to_string(idea_seed=self.idea_seed)

            print(f"\n==============\n==============\n\nPlan {plan.id}:\n{plan_text}\n")

            try:
                # Generate the initial prompt for this plan
                prompt_str = self._generate_initial_prompt(plan_text)

                # Evaluate the initial prompt
                df_generated, accuracy = self._evaluate_prompt(
                    prompt_str, attempt_no, plan.id
                )
                df_incorrect = get_df_incorrect_answers(df_generated)
                self.dataset_tracker.update_mistakes(df_incorrect)
                self._log_attempt(attempt_no, accuracy, "First attempt.", prompt_str)

                ## The Update Prompt loop to auto-magically improve the prompt ###
                ## Runs until the prompt is good enough (or max loops is reached).
                while (
                    accuracy < self.goal_accuracy
                    and attempt_no < self.max_attempts_per_plan
                ):
                    attempt_no += 1
                    prompt_str, changes_made_str = self._update_prompt(
                        df_generated, prompt_str, plan_text, attempt_no, plan.id
                    )
                    df_generated, accuracy = self._evaluate_prompt(
                        prompt_str, attempt_no, plan.id
                    )
                    df_incorrect = get_df_incorrect_answers(df_generated)
                    self.dataset_tracker.update_mistakes(df_incorrect)
                    self._log_attempt(
                        attempt_no, accuracy, changes_made_str, prompt_str
                    )

                    print("\n---\n" + self.previous_attempts.to_string() + "---\n")
            except Exception as e:
                print(f"Error: {e}")
                print(f">> Skipping plan {plan.id}...")
                continue

            # Break the loop if the goal accuracy is achieved
            if accuracy >= self.goal_accuracy:
                break

            if i >= 2:
                print(f"\n\n\nTEMP: Stopping because we've tried {i+1} plans already.")
                break

        return self.best_prompt.get_best_prompt()
