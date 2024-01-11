## Problem Description
{idea_seed}


## Current Prompt
<prompt>
{current_prompt}
</prompt>


## Incorrect answers
I used the `Current Prompt`, but the following answers were wrong, and do not match the ground `Truth`.
<table_incorrect_answers>
{incorrect_answers_table}
</table_incorrect_answers>


## Previous attempts to get higher accuracy
Use the following log of changes per prompt to guide your next move. If the accuracy drops, you MUST undo some of the previous changes and try a different idea.

{previous_attempts}


---

# YOUR TASK:

Your updated `<prompt>` MUST NEVER change the `Important formatting rules` and `TASK` heading sections, as they are crucial to how the prompt works. Your updated prompt MUST keep the same structure and formatting of the `Current Prompt`.

=> DO NOT forget that the variable `%%%INPUT_TABLE%%%` under the `TASK` heading and "`table_input`" subheading is crucial and must be preserved as is in the updated prompt in the same structure.

Your Goal is focusing on getting higher accuracy by analyzing the `Incorrect answers` above and updating the prompt to make sure that the prompt does not get similar answers incorrectly. I will try running the prompt you will output again through GPT-4 and I expect it to get the `Incorrect answers` above correctly. 

Reply with the updated prompt that performs better than the `Current Prompt`. Your update prompt MUST NEVER be the exact same as the Current Prompt, it must be updated to perform better. This is very important.