from strategies.base import BaseStrategy

class SequentialStrategy(BaseStrategy):
    """
    SequentialStrategy is a class designed to automate the process of
    generating and evaluating prompts based on a dataset. It iteratively generates
    prompts using expert plans, evaluates them, and updates them based on the feedback
    until a desired accuracy is achieved or a maximum number of attempts is reached.
    """

    def run(self):
        """
        The main method to run the iterative process of generating, evaluating,
        and updating prompts based on expert plans.

        Returns:
            Tuple: A tuple containing the best prompt, its accuracy, and the associated plan.
        """
        # Generate and rank expert plans
        ranked_expert_plans = self._generate_expert_plans()

        # Loop through each expert plan
        for i, plan in enumerate(ranked_expert_plans):
            # if i >= 1:
            #     print(f"\n\n\nTEMP: Stopping because we've tried {i} plans already.")
            #     break
            #
            # if plan.id != 5:
            #     continue

            try:
                accuracy, prompt_str, df_generated = self._run_plan_initial_prompt(plan)

                accuracy = self._run_update_prompt_loop(
                    plan, accuracy, prompt_str, df_generated
                )

                # Break the loop if the goal accuracy is achieved
                if accuracy >= self.goal_accuracy:
                    break
            except Exception as e:
                print(f"Error: {e}")
                print(f">> Skipping plan {plan.id}...")

        return self.best_prompt.get_best_prompt()
