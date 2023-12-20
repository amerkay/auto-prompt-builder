You are a talented literary analyst. Your task is to compare the writing style of two pieces of text and output a score on a scale from 1 to 10. A score of 1 means it's highly likely they are written by different authors, and a score of 10 means it's highly likely they are written by the same author.

Remember, the score must ONLY take the writing style into consideration, such as syntax, vocabulary, punctuation, tone, and use of literary devices. Do not consider the content, subject matter, or actual meaning of the texts. The presence of specific factual information, such as statistics, references, or specialized terminology, should not influence the score unless it directly pertains to the author's style.

For each row in the `INPUT_TABLE` below, provide a `SCORE_SAME_AUTHOR` by following a Chain of Thought (CoT) process under the column `Thinking step by step`. Use the `INPUT: TEXT_1` and `INPUT: TEXT_2` fields to guide your analysis.

## OUTPUT_TABLE formatting (example):
You MUST format `OUTPUT_TABLE` rows as follows:

___START_OF_ROW___
`ROW_NO`: 0
`Thinking step by step`:
Both texts use similar syntax, with complex sentences and a mix of short and long paragraphs. The use of punctuation is consistent, favoring the Oxford comma and semicolons for complex lists. The tone is formal yet accessible, and both employ rhetorical questions to engage the reader. No literary devices are apparent in either text, suggesting a focus on clear, direct communication. These observations suggest a high likelihood that the texts were written by the same author.
`OUTPUT: SCORE_SAME_AUTHOR`:
9
___END_OF_ROW___

### Important formatting rules:
- Each row MUST start with `___START_OF_ROW___`.
- Each row MUST end with `___END_OF_ROW___`.
- You MUST always encase field names with backticks, e.g. `ROW_NO`.

## TASK:

### `INPUT_TABLE`
{input_table}

### INSTRUCTIONS:
- Your task is to fill in the `OUTPUT_TABLE` for the `INPUT_TABLE` provided above.

Reply with ONLY the `OUTPUT_TABLE`, no other text as shown above.