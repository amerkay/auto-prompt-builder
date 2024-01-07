from strategies.base import BaseStrategy


class BasicMemoryStrategy(BaseStrategy):
    """
    ExpertPlanMemoryStrategy is a class that extends SequentialStrategy to focus on
    utilizing expert plans more effectively, particularly by implementing a two-run
    strategy on the hardest rows of the dataset.
    """

    def _run_all_plans(self, ranked_expert_plans):
        """
        Runs a single iteration of the strategy.

        Args:
            ranked_expert_plans (list): A list of ranked expert plans.

        Returns:
            float: The accuracy achieved in the single run.
        """
        accuracy = 0

        for plan in ranked_expert_plans:
            try:
                accuracy, _, _ = self._run_plan_initial_prompt(plan)

                # Check if goal accuracy is already met
                if accuracy >= self.goal_accuracy:
                    break
            except Exception as e:
                print(f"Error: {e}")
                print(f">> Skipping plan {plan.id}...")
                continue

        return accuracy


    def run(self):
        """
        Overrides the run method of SequentialStrategy to implement a two-run
        strategy focused on expert plans and hardest dataset rows.

        Returns:
            Tuple: A tuple containing the best prompt, its accuracy, and the associated plan.
        """
        # Generate and rank expert plans
        ranked_expert_plans = self._generate_expert_plans()

        # First Run: Initial prompt generation for each expert plan
        accuracy = self._run_all_plans(ranked_expert_plans)

        # Second Run: Now with EvalAwareDataset knowing the hardest rows
        if accuracy < self.goal_accuracy:
            self._run_all_plans(ranked_expert_plans)

        return self.best_prompt.get_best_prompt()
