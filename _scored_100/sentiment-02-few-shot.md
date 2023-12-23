You are a sentiment analyst. Your task is to determine the sentiment of a given sentence.

For each row in the `INPUT_TABLE` below, determine the `OUTPUT: Sentiment` column using a few-shot learning approach. The `OUTPUT: Sentiment` can be one of the following categories:

1. **Positive**: The sentence expresses a positive sentiment.
2. **Neutral**: The sentence expresses a neutral sentiment.
3. **Negative**: The sentence expresses a negative sentiment.
4. **Unsure**: The sentiment of the sentence is unclear or ambiguous.


---


## EXAMPLE

Use the examples below to guide you:

### Example `INPUT_TABLE`

___START_OF_INPUT_TABLE___

___START_OF_ROW___
`ROW_NO`: 1
`INPUT: Sentence`:
I'm loving this new recipe!
___END_OF_ROW___

___START_OF_ROW___
`ROW_NO`: 2
`INPUT: Sentence`:
This book is just average.
___END_OF_ROW___

___START_OF_ROW___
`ROW_NO`: 3
`INPUT: Sentence`:
I'm so angry at the terrible service!
___END_OF_ROW___

___END_OF_INPUT_TABLE___


### Example `OUTPUT_TABLE`

___START_OF_OUTPUT_TABLE___

___START_OF_ROW___
`ROW_NO`: 1
`OUTPUT: Sentiment`:
Positive
___END_OF_ROW___

___START_OF_ROW___
`ROW_NO`: 2
`OUTPUT: Sentiment`:
Neutral
___END_OF_ROW___

___START_OF_ROW___
`ROW_NO`: 3
`OUTPUT: Sentiment`:
Negative
___END_OF_ROW___

___END_OF_OUTPUT_TABLE___


## Important formatting rules:
- Each row MUST start with `___START_OF_ROW___`.
- Each row MUST end with `___END_OF_ROW___`.
- You MUST always encase field names with backticks, e.g. `ROW_NO`.

---

## YOUR TASK:

**`INPUT_TABLE`**

___START_OF_INPUT_TABLE___
{input_table}
___END_OF_INPUT_TABLE___


Complete the `OUTPUT_TABLE` for each row in the `INPUT_TABLE` above using a few-shot learning approach.

Reply with ONLY the `OUTPUT_TABLE`, no other text as shown in the example above.