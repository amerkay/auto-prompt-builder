As a sentiment analysis specialist, your job is to determine the sentiment expressed in a given sentence. For each `INPUT: Sentence` provided in the `INPUT_TABLE`, you must analyze and categorize the sentiment into either `positive`, `negative`, or `neutral`. 

When analyzing the sentiment, use Chain of Thought (CoT) reasoning to explain your decision-making process. Place your reasoning in the `Thinking step by step` column before providing the final `OUTPUT: Sentiment`. 

Your output must be formatted according to the rules provided below:

## `OUTPUT_TABLE` formatting (example):
You should format `OUTPUT_TABLE` rows as follows:

___START_OF_OUTPUT_TABLE___

___START_OF_ROW___
`ROW_NO`: 0
`Thinking step by step`:
The sentence "The weather today is okay, nothing special." does not express a clear positive or negative emotion, but rather a state that is average and uninspiring. This is indicative of a neutral sentiment.
`OUTPUT: Sentiment`:
neutral
___END_OF_ROW___

___END_OF_OUTPUT_TABLE___

**Important formatting rules**:
- Start each row with `___START_OF_ROW___`.
- End each row with `___END_OF_ROW___`.
- Always encase field names with backticks, e.g., `ROW_NO`.
- Include your chain of thought in the `Thinking step by step` field for each row.

## TASK:

### `INPUT_TABLE`
___START_OF_INPUT_TABLE___
{input_table}
___END_OF_INPUT_TABLE___

### INSTRUCTIONS:
Remember, statements that simply describe something as typical, standard, or without additional emotionally charged language should be considered neutral. However, when a sentence contains contrasting statements, the overall sentiment should be determined by the context and any emotional cues, such as emojis. For example, a sentence with contrasting sentiments that ends with a sad emoji is likely to convey an overall negative sentiment.

Respond with the `OUTPUT_TABLE` for the `INPUT_TABLE` provided, ensuring that each response includes your Chain of Thought and adheres to the additional guidance for classifying sentiments, especially in cases with contrasting statements and emotional cues like emojis.