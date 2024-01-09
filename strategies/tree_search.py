from strategies.base import BaseStrategy


class TreeSearchStrategy(BaseStrategy):
    """
    TreeSearchStrategy is a class designed to automate the process of
    generating and evaluating prompts based on a dataset.
    """

    def _check_must_stop(
        self, accuracy, min_acceptable_accuracy, plan, mutation, previous_accuracy=0
    ):
        # Check if accuracy is below min_acceptable_accuracy, and stop if so
        if accuracy < min_acceptable_accuracy:
            print(
                f">>>> Accuracy below min_acceptable_accuracy for plan {plan.id}"
                f", mutation {mutation} is {accuracy}%. Next!"
            )
            return True

        # Check if accuracy is below previous_accuracy, and stop if so
        if accuracy < previous_accuracy:
            print(
                f">>>> Accuracy below previous accuracy for plan {plan.id}"
                f", mutation {mutation} is {accuracy}%. Next!"
            )
            return True

        # Check if the goal accuracy is achieved
        if accuracy >= self.goal_accuracy:
            print(
                f">>>> Goal accuracy {self.goal_accuracy}% achieved "
                f"for plan {plan.id}, mutation {mutation}!"
            )
            return True

        return False

    def _run_update_prompt_loop(
        self,
        plan,
        previous_accuracy,
        prompt_str,
        df_generated,
        min_acceptable_accuracy=70,
        mutation=0,
    ):
        """
        Overriding the method from the base class to implement a tree search.

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

        while self.attempt_no < self.max_attempts_per_plan:
            accuracy = self._update_prompt(df_generated, prompt_str, plan)

            if self._check_must_stop(
                accuracy, min_acceptable_accuracy, plan, mutation, previous_accuracy
            ):
                return accuracy

        return accuracy

    def _run_one_mutation(self, plan, mutation=0, min_acceptable_accuracy=70):
        """
        Runs a single mutation on the plan and returns the accuracy.

        Args:
            plan (Plan): The plan.
            mutation (int, optional): The index of the mutation to apply. Defaults to 0.

        Returns:
            float: The accuracy after applying the mutation, and updating the prompt.
        """
        accuracy, prompt_str, df_generated = self._run_plan_initial_prompt(
            plan, mutation
        )

        if self._check_must_stop(accuracy, min_acceptable_accuracy, plan, mutation):
            return accuracy

        accuracy = self._run_update_prompt_loop(
            plan, accuracy, prompt_str, df_generated, min_acceptable_accuracy, mutation
        )

        return accuracy

    def run(self, max_mutations=1, min_acceptable_accuracy=70):
        """
        Returns:
            Tuple: A tuple containing the best prompt, its accuracy, and the associated plan.
        """
        # Generate and rank expert plans
        ranked_expert_plans = self._generate_expert_plans()

        accuracy = 0

        # Loop through each expert plan
        for i, plan in enumerate(ranked_expert_plans):
            # if i > 2:
            #     print(f"\n\n\nTEMP: Stopping because we've tried {i} plans already.")
            #     break
            #
            # if plan.id != 5:
            #     continue

            try:
                for mutation in range(1, max_mutations + 1):
                    print(f"\n-> Running plan {plan.id} with mutation {mutation}...")

                    accuracy = self._run_one_mutation(
                        plan, mutation, min_acceptable_accuracy
                    )

                    # Break the loop if the goal accuracy is achieved
                    if self._check_must_stop(
                        accuracy, min_acceptable_accuracy, plan, mutation
                    ):
                        return self.best_prompt.get_best_prompt()
            except Exception as e:
                print(f"Error: {e}")
                print(f">> Skipping plan {plan.id}...")

        return self.best_prompt.get_best_prompt()
