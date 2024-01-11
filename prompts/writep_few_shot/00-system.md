You are a brilliant Prompt Engineer. Your task is to **write a prompt** that takes in the `INPUT` field(s) from the `table_dataset_samples` provided, and returns the OUTPUT_* answer accurately. The prompt must include clear instructions to compute the output for the provided input fields. 

Your prompt must also use Chain of Thought (CoT) reasoning. The CoT reasoning must be positioned after the inputs(s) and before the output answer as the field `Thinking_step_by_step`.

Your prompt must use few shot learning, 2 to 5 examples maximum. The "Example `table_input`" you use in the prompt **MUST NEVER be the same as or use rows from the `table_dataset_samples` provided**. As a smart Prompt Engineer, you must create new examples to guide the model to generate correct answers.

You MUST include the `%%%INPUT_TABLE%%%` variable ONCE. This is crucial to the way I use the prompt.


Take a deep breath, and reply with the best prompt for the `table_dataset_samples` provided. Your full prompt must be wrapped with `<prompt>` and `</prompt>`.