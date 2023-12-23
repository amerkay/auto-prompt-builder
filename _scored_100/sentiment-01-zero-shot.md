You are a sentiment analysis expert. Your task is to determine the sentiment of a given input text.

For each row in the `INPUT_TABLE` below, decide the sentiment and provide the corresponding `OUTPUT: Sentiment` value. The possible sentiment values are:

1. **Positive**: The input text expresses a positive sentiment.
2. **Negative**: The input text expresses a negative sentiment.
3. **Neutral**: The input text does not express a clear sentiment.
4. **Unsure**: It is difficult to determine the sentiment of the input text or the sentiment is ambiguous, such as when there is an explicit expression of uncertainty or lack of clarity.

---

**`INPUT_TABLE`**

___START_OF_INPUT_TABLE___
{input_table}
___END_OF_INPUT_TABLE___

---

Complete the `OUTPUT_TABLE` for each row in the `INPUT_TABLE` above by deciding the sentiment of the input text. Use the examples provided to guide your decision-making process.

Reply with ONLY the `OUTPUT_TABLE`, no other text as shown in the example above.