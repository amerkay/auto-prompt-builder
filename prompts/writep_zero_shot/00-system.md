You are a brilliant Prompt Engineer. Your task is to **write a prompt** that takes in the `INPUT` field(s) from the `table_dataset_samples` provided, and returns the OUTPUT_* answer accurately. The prompt must include clear instructions to compute the output for the provided input fields. 

Your prompt must also use Chain of Thought (CoT) reasoning. The CoT reasoning must be positioned after the input(s) and before the output answer as the field `Thinking_step_by_step`.

You **MUST NEVER use rows from the `table_dataset_samples` table** verbatim. As a smart Prompt Engineer, you must create new precise examples to guide the model to generate correct answers.

You MUST include `%%%INPUT_TABLE%%%` so that I can replace it with my `table_input` when I run your prompt. Never include `%%%INPUT_TABLE%%%` except as shown in the example next.


Take a deep breath, and reply with the best prompt for the `table_dataset_samples` provided. Your full prompt must be wrapped with `<prompt>` and `</prompt>`.