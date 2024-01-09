## Problem Description
{idea_seed}


## Current Prompt
<prompt>
{current_prompt}
</prompt>


## Incorrect answers
I used the `Current Prompt`, but the following answers were wrong, and do not match the ground `Truth`.

{incorrect_answers_table}


## Previous attempts to get higher accuracy
Use the following log of changes per prompt to guide your next move. If the accuracy drops, you MUST undo some of the previous changes and try a different idea.

{previous_attempts}


---

You MUST NOT change the `## Important formatting rules:` and `INPUT_TABLE` sections, as they are crucial to how the prompt works.

You MUST also keep the same structure for the few shot learning and examples in the `Current Prompt`.


Focus on getting higher accuracy by analyzing the `Incorrect answers` above and updating the prompt to make sure that the prompt does not get similar answers incorrectly. I will try running the prompt you will output again through GPT-4 and I expect it to get the `Incorrect answers` above correctly. 