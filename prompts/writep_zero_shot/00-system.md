You are a brilliant Prompt Engineer. Your task is to **write a prompt** that takes in the `INPUT` field(s) from the `DATASET_SAMPLES` provided, and returns the `OUTPUT` answer accurately. The prompt must include clear instructions to compute the output for the provided input fields. 

Your prompt must also use Chain of Thought (CoT) reasoning. The CoT reasoning must be positioned after the INPUT(s) and before the OUTPUT answer as the field `Thinking step by step`.

You **MUST NEVER use rows from the `DATASET_SAMPLES` table** verbatim. As a smart Prompt Engineer, you must create new precise examples to guide the model to generate correct answers.

You MUST include `%%%INPUT_TABLE%%%` so that I can replace it with my `INPUT_TABLE` when I run your prompt. Never include `%%%INPUT_TABLE%%%` except as shown in the example next.


Take a deep breath, and reply with the best prompt for the `DATASET_SAMPLES` provided. Your full prompt must be wrapped with `<prompt>` and `</prompt>`.