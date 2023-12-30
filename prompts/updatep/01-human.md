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

You MUST include this statement in your updated prompt: "Remember each row MUST start with `___START_OF_ROW___` and end with `___END_OF_ROW___`. Each field within a row is denoted by backticks. For example, the ROW_NO will be `ROW_NO`, etc."

Remember to keep the same structure for the few shot learning and examples in the `Current Prompt` section.