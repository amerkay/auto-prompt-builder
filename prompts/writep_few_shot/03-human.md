# Problem Description
{idea_seed}


# `table_dataset_samples`
<table_dataset_samples>
{dataset_samples_table}
</table_dataset_samples>


The "Example `table_input`" you use in the prompt **MUST NEVER use rows from the `table_dataset_samples` provided**. You must make up new examples to guide GPT.
The "Example `table_output`" MUST ALWAYS include the `Thinking_step_by_step` column.
DO NOT FORGET that the output field starts `OUTPUT_` (OUTPUT_*).
DO NOT FORGET to include the variable `%%%INPUT_TABLE%%%`.
You MUST include the `Important formatting rules` section exactly like before.
You MUST choose examples that will guide the LLM using few shot prompting.