class BestPrompt:
    """
    This class is used to keep track of the best prompt and its accuracy.

    Attributes:
        accuracy (float): The accuracy of the best prompt.
        prompt (str): The text of the best prompt.
        plan (object): The plan associated with the best prompt.
    """

    def __init__(self):
        """
        Initialize the BestPrompt class with an accuracy of 0 and an empty prompt.
        """
        self.accuracy = 0
        self.prompt = ""
        self.plan = None

    def update(self, new_accuracy, new_prompt, plan):
        """
        Update the best prompt if the new prompt has higher accuracy.

        Args:
            new_accuracy (float): Accuracy of the new prompt.
            new_prompt (str): The new prompt text.
            plan (object): The plan associated with the new prompt.
        """
        if new_accuracy > self.accuracy:
            self.accuracy = new_accuracy
            self.prompt = new_prompt
            self.plan = plan

    def get_best_prompt(self):
        """
        Returns the best prompt and its accuracy.

        Returns:
            Tuple: A tuple containing the best prompt, its accuracy, and the associated plan.
        """
        return self.prompt, self.accuracy, self.plan



# # Example of how to use the BestPrompt class
# best_prompt = BestPrompt()
# best_prompt.update(95, "Example prompt 1")
# print(f"Current best prompt: '{best_prompt.get_best_prompt()[1]}' with accuracy {best_prompt.get_best_prompt()[0]}%")

# best_prompt.update(97, "Example prompt 2")
# print(f"Updated best prompt: '{best_prompt.get_best_prompt()[1]}' with accuracy {best_prompt.get_best_prompt()[0]}%")
